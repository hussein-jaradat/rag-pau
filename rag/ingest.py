"""Ingestion layer: load -> clean -> structure-aware chunking -> metadata.

Supports PDF (text + tables, page numbers kept), DOCX, TXT/MD, HTML, CSV.
Every chunk keeps: source file, title, page, section heading, type (text/table),
document date/version and access level, so answers can cite "file, p. 4, Article 7"
and the retriever can filter by role or prefer the newest version.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .arabic import fix_reversed_lines, is_arabic, strip_artifacts

SUPPORTED = {".pdf", ".docx", ".txt", ".md", ".html", ".htm", ".csv"}


@dataclass
class Chunk:
    id: str
    text: str                      # the passage shown to the LLM / user
    source: str                    # file name
    title: str
    page: int | None = None
    section: str = ""
    kind: str = "text"             # text | table
    lang: str = "ar"
    date: str = ""                 # document date or version, e.g. 2024
    access: str = "public"         # for RBAC: public | staff | hr | admin ...
    url: str = ""
    extra: dict = field(default_factory=dict)

    def header(self) -> str:
        """Contextual header prepended for embedding/BM25 (not shown twice)."""
        bits = [self.title]
        if self.section:
            bits.append(self.section)
        return " > ".join(b for b in bits if b)

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- loaders
@dataclass
class Page:
    number: int | None
    text: str
    tables: list[str] = field(default_factory=list)


def _table_to_md(rows: list[list]) -> str:
    rows = [[(c or "").replace("\n", " ").strip() for c in r] for r in rows if r and any(r)]
    if len(rows) < 2:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    head = "| " + " | ".join(rows[0]) + " |"
    sep = "|" + "---|" * width
    body = ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join([head, sep, *body])


def _course_records(rows: list[list[str]], caption: str, program: str) -> list[str]:
    """Study-plan tables (often two semesters side by side: س.م | اسم المساق | رقم المساق ...)
    -> one self-contained line per course, e.g.
    'برنامج X | السنة الأولى - الفصل الأول | المساق: البرمجة 1 | رقم المساق: 410132 | الساعات المعتمدة: 3'."""
    hdr_i = next((i for i, r in enumerate(rows) if any("اسم المساق" in c or "المساق" == c.strip() for c in r)), None)
    if hdr_i is None:
        return []
    hdr = rows[hdr_i]
    groups, cur = [], {}
    for j, h in enumerate(hdr):
        h = h.strip()
        key = ("name" if "اسم" in h else "code" if ("رقم" in h or "الرمز" in h) else
               "hours" if ("س.م" in h or "ساع" in h) else "pre" if "متطلب" in h else None)
        if key is None:
            continue
        if key in cur:
            groups.append(cur)
            cur = {}
        cur[key] = j
    if cur:
        groups.append(cur)
    sems = [c for c in (rows[hdr_i - 1] if hdr_i > 0 else []) if c.strip()]
    out = []
    for r in rows[hdr_i + 1:]:
        for gi, g in enumerate(groups):
            name = r[g["name"]].strip() if "name" in g and g["name"] < len(r) else ""
            if not name or "مجموع" in name or "المجموع" in name:
                continue
            parts = [program, caption + (f" - {sems[gi]}" if gi < len(sems) else ""), f"المساق: {name}"]
            for k, lab in (("code", "رقم المساق"), ("hours", "الساعات المعتمدة"), ("pre", "المتطلب السابق")):
                if k in g and g[k] < len(r) and r[g[k]].strip():
                    parts.append(f"{lab}: {r[g[k]].strip()}")
            out.append(" | ".join(p for p in parts if p))
    return out


def load_pdf(path: Path) -> list[Page]:
    pages: list[Page] = []
    try:
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            for i, p in enumerate(pdf.pages, start=1):
                tables = []
                try:
                    for t in p.extract_tables() or []:
                        md = _table_to_md(t)
                        if md:
                            tables.append(md)
                except Exception:
                    pass
                text = p.extract_text() or ""
                pages.append(Page(i, text, tables))
    except ImportError:
        from pypdf import PdfReader

        for i, p in enumerate(PdfReader(str(path)).pages, start=1):
            pages.append(Page(i, p.extract_text() or ""))
    # Scanned PDF? (no text at all) -> try OCR if available
    if pages and sum(len(p.text.strip()) for p in pages) < 50:
        pages = _ocr_pdf(path) or pages
    return pages


def _ocr_pdf(path: Path) -> list[Page]:
    """Optional OCR for scanned PDFs: needs `pip install pytesseract pdf2image`
    plus the tesseract binary with the `ara` language pack."""
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        print(f"[ingest] {path.name}: looks scanned; install pytesseract+pdf2image for OCR")
        return []
    out = []
    for i, img in enumerate(convert_from_path(str(path), dpi=250), start=1):
        out.append(Page(i, pytesseract.image_to_string(img, lang="ara+eng")))
    return out


def load_docx(path: Path) -> list[Page]:
    import docx

    d = docx.Document(str(path))
    lines = []
    for para in d.paragraphs:
        t = para.text.strip()
        if not t:
            continue
        if para.style is not None and para.style.name.lower().startswith(("heading", "title")):
            t = "# " + t
        lines.append(t)
    tables = [_table_to_md([[c.text for c in r.cells] for r in t.rows]) for t in d.tables]
    return [Page(None, "\n".join(lines), [t for t in tables if t])]


def load_html(path: Path) -> list[Page]:
    """Web page -> main content text + tables (study plans) as Markdown tables.
    Menus, headers, footers, sidebars and scripts are dropped."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return [Page(None, re.sub(r"<[^>]+>", " ", raw))]
    soup = BeautifulSoup(raw, "lxml")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form",
                     "iframe", "svg", "button"]):
        tag.decompose()
    for sel in [".menu", ".navbar", ".sidebar", ".widget", ".breadcrumb", "#footer", "#header",
                ".site-footer", ".site-header", ".elementor-location-header",
                ".elementor-location-footer", ".share", ".social"]:
        for t in soup.select(sel):
            t.decompose()
    main = None
    for sel in [".entry-content", "article", "main", "#content", ".elementor-section-wrap",
                ".content", "#primary"]:
        cand = soup.select_one(sel)
        if cand and len(cand.get_text(strip=True)) > 300:
            main = cand
            break
    main = main or soup.body or soup
    tables = []
    for t in main.find_all("table"):
        # the nearest heading above the table gives it context (e.g. "السنة الأولى")
        prev = t.find_previous(re.compile("^h[1-6]$"))
        cap = prev.get_text(" ", strip=True) if prev else ""
        rows = []
        for tr in t.find_all("tr"):
            row = []
            for c in tr.find_all(["th", "td"]):
                row.extend([c.get_text(" ", strip=True)] + [""] * (int(c.get("colspan", 1) or 1) - 1))
            rows.append(row)
        page_title = soup.title.get_text(" ", strip=True).split("|")[0].strip() if soup.title else ""
        recs = _course_records(rows, cap, page_title)
        if recs:
            tables.append("@@RECORDS@@" + cap + "\n" + "\n".join(recs))
        else:
            md = _table_to_md(rows)
            if md:
                tables.append((f"**{cap}**\n" if cap else "") + md)
        t.decompose()
    for h in main.find_all(re.compile("^h[1-4]$")):
        h.replace_with(f"\n\n# {h.get_text(' ', strip=True)}\n")
    for br in main.find_all("br"):
        br.replace_with("\n")
    for blk in main.find_all(["p", "li", "div", "section", "h5", "h6", "tr"]):
        blk.append("\n")
    text = main.get_text(" ")
    text = "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return [Page(None, text, tables)]


def load_csv(path: Path) -> list[Page]:
    """Each row becomes a self-contained 'record' line (good for FAQs, course lists)."""
    with path.open(encoding="utf-8", errors="ignore", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    head, body = rows[0], rows[1:]
    lines = ["; ".join(f"{h}: {v}" for h, v in zip(head, r) if v) for r in body]
    return [Page(None, "\n\n".join(lines))]


def load_file(path: Path) -> list[Page]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    if ext == ".docx":
        return load_docx(path)
    if ext in {".html", ".htm"}:
        return load_html(path)
    if ext == ".csv":
        return load_csv(path)
    return [Page(None, path.read_text(encoding="utf-8", errors="ignore"))]


# --------------------------------------------------------------------------- cleaning
PAGE_NUM = re.compile(r"^\s*(page|صفحة|ص)?\s*\d+\s*(of|من|/)?\s*\d*\s*$", re.I)


def clean_pages(pages: list[Page]) -> list[Page]:
    """Remove repeated headers/footers (lines on >40% of pages), page numbers,
    broken whitespace; fix reversed Arabic."""
    for p in pages:
        p.text = fix_reversed_lines(strip_artifacts(p.text))
    if len(pages) >= 3:
        counts = Counter()
        for p in pages:
            for line in {l.strip() for l in p.text.split("\n") if l.strip()}:
                counts[line] += 1
        repeated = {l for l, c in counts.items() if c / len(pages) > 0.4 and len(l) < 120}
    else:
        repeated = set()
    for p in pages:
        keep = []
        for line in p.text.split("\n"):
            s = line.strip()
            if not s or s in repeated or PAGE_NUM.match(s):
                keep.append("") if not s else None
                continue
            keep.append(re.sub(r"[ \t]+", " ", s))
        p.text = re.sub(r"\n{3,}", "\n\n", "\n".join(keep)).strip()
    return pages


# --------------------------------------------------------------------------- chunking
HEADING = re.compile(
    r"^(#{1,4}\s+.+"                                   # markdown heading
    r"|(?:المادة|مادة|البند|الفصل|الباب|القسم|الجزء|الفرع)\s*[\(\[]?\s*[\d٠-٩]+.*"  # Arabic legal
    r"|(?:Article|Section|Chapter|Part|Clause)\s+[\dIVX]+.*"  # English legal
    r"|[\d٠-٩]+(?:\.[\d٠-٩]+)*[\.\)]\s+\S.{0,80})$",       # 1. / 2.3) numbered titles
    re.I,
)
SENT_SPLIT = re.compile(r"(?<=[\.\!\?؟。])\s+|\n")


def _is_heading(line: str) -> bool:
    s = line.strip()
    return bool(s) and len(s) < 120 and bool(HEADING.match(s))


def _split_long(text: str, size: int, overlap: int) -> list[str]:
    """Sentence-aware window: never cut in the middle of a sentence if avoidable."""
    sents = [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]
    out, cur = [], ""
    for s in sents:
        if len(s) > size:                                   # monster sentence: hard cut
            if cur:
                out.append(cur)
                cur = ""
            step = max(size - overlap, 1)
            out.extend(s[i:i + size] for i in range(0, len(s), step))
            continue
        if len(cur) + len(s) + 1 <= size:
            cur = f"{cur} {s}".strip()
        else:
            out.append(cur)
            tail = cur[-overlap:] if overlap else ""
            tail = tail[tail.find(" ") + 1:] if " " in tail else tail
            cur = f"{tail} {s}".strip()
    if cur:
        out.append(cur)
    return out


def chunk_document(pages: list[Page], meta: dict, size: int, overlap: int) -> list[Chunk]:
    source, title = meta["source"], meta.get("title") or Path(meta["source"]).stem
    chunks: list[Chunk] = []
    section = ""
    lang_sample = " ".join(p.text[:500] for p in pages[:3])
    lang = "ar" if is_arabic(lang_sample) else "en"

    def emit(text: str, page, kind="text"):
        text = text.strip()
        if len(text) < 25:
            return
        cid = hashlib.md5(f"{source}|{page}|{len(chunks)}|{text[:50]}".encode()).hexdigest()[:12]
        chunks.append(Chunk(
            id=cid, text=text, source=source, title=title, page=page, section=section,
            kind=kind, lang=lang, date=str(meta.get("date", "")), access=meta.get("access", "public"),
            url=meta.get("url", ""), extra={k: v for k, v in meta.items()
                                            if k not in {"source", "title", "date", "access", "url"}},
        ))

    record_mode = bool(meta.get("records")) or source.lower().endswith(".csv")
    for p in pages:
        buf: list[str] = []

        def flush():
            if buf:
                for piece in _split_long("\n".join(buf), size, overlap):
                    emit(piece, p.number)
                buf.clear()

        if record_mode:                      # CSV / FAQ: one record = one chunk
            for rec in re.split(r"\n\s*\n", p.text):
                emit(rec, p.number, "record")
            continue
        for para in re.split(r"\n\s*\n", p.text):
            lines: list[str] = []
            for line in para.split("\n"):
                if _is_heading(line):        # headings can sit inside a PDF paragraph
                    if lines:
                        if sum(len(b) for b in buf) + sum(len(x) for x in lines) > size:
                            flush()
                        buf.append("\n".join(lines))
                        lines = []
                    flush()
                    section = line.lstrip("# ").strip()
                else:
                    lines.append(line)
            para_text = "\n".join(lines).strip()
            if not para_text:
                continue
            if sum(len(b) for b in buf) + len(para_text) > size:
                flush()
            buf.append(para_text)
        flush()
        for t in p.tables:                                  # tables stay whole (or split by rows)
            if t.startswith("@@RECORDS@@"):                 # study plan: one course = one chunk
                cap, _, body = t[len("@@RECORDS@@"):].partition("\n")
                saved, section = section, cap or section
                for rec in body.split("\n"):
                    emit(rec, p.number, "course")
                section = saved
                continue
            if t.startswith("**"):
                saved, section = section, t[2:t.find("**", 2)] or section
            else:
                saved = section
            if len(t) <= size * 2:
                emit(t, p.number, "table")
            else:
                rows = t.split("\n")
                head, body = rows[:2], rows[2:]
                part: list[str] = []
                for r in body:
                    if sum(len(x) for x in part) + len(r) > size * 2:
                        emit("\n".join(head + part), p.number, "table")
                        part = []
                    part.append(r)
                emit("\n".join(head + part), p.number, "table")
            section = saved
    return chunks


# --------------------------------------------------------------------------- driver
def _guess_date(name: str, text: str) -> str:
    m = re.search(r"(19|20)\d{2}", name) or re.search(r"(?:20)\d{2}", text[:2000])
    return m.group(0) if m else ""


def load_meta(docs_dir: Path) -> dict:
    """Optional sidecar: data/docs/_meta.json
    {"file.pdf": {"title": "...", "date": "2024", "access": "hr", "url": "..."}}"""
    f = docs_dir / "_meta.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def ingest_folder(docs_dir: Path, size: int = 900, overlap: int = 150) -> tuple[list[Chunk], dict]:
    sidecar = load_meta(docs_dir)
    all_chunks: list[Chunk] = []
    report = {"files": [], "skipped": []}
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file() or path.name.startswith(("_", ".")):
            continue
        if path.suffix.lower() not in SUPPORTED:
            report["skipped"].append(path.name)
            continue
        try:
            pages = clean_pages(load_file(path))
        except Exception as e:  # one bad file must never kill the whole index
            report["skipped"].append(f"{path.name} ({e})")
            continue
        rel = path.relative_to(docs_dir).as_posix()      # "/" on Windows too (matches _meta.json)
        meta = {"source": rel, **sidecar.get(rel, sidecar.get(path.name, {}))}
        meta.setdefault("date", _guess_date(path.name, pages[0].text if pages else ""))
        chunks = chunk_document(pages, meta, size, overlap)
        all_chunks.extend(chunks)
        report["files"].append({"file": rel, "pages": len(pages), "chunks": len(chunks),
                                "tables": sum(len(p.tables) for p in pages),
                                "chars": sum(len(p.text) for p in pages)})
    # exact-duplicate removal
    seen, unique = set(), []
    for c in all_chunks:
        key = re.sub(r"\s+", " ", c.text)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    report["duplicates_removed"] = len(all_chunks) - len(unique)
    report["total_chunks"] = len(unique)
    return unique, report
