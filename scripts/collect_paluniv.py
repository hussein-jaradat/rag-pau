"""Collect Palestine Ahliya University public documents into data/docs/.

    python scripts/collect_paluniv.py            # downloads ~60-100 pages + PDFs (2-4 minutes)

What it collects (all public, official site paluniv.edu.ps; sources listed in README):
  * PDFs: Student Guide 2024-2025 and 2023-2024 (old vs new version), Bachelor's and Diploma
    degree regulations, Basic Statute.
  * Pages: admission & registration regulations, bachelor requirements, FAQ, new students,
    scholarships, payment.
  * Every program page under every faculty (overview, admission, STUDY PLAN tables, course
    descriptions). Program links are found automatically: links on a faculty page that are
    NOT in the site-wide menu.
Writes data/docs/_meta.json with title / url / date for each file (used for citations).
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "docs"
BASE = "https://www.paluniv.edu.ps/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PalUniv-RAG-Advisor/1.0 (student project)"}

PDFS = {
    "student_guide_2024_2025.pdf": ("دليل الطالب 2024-2025", "2024",
        "https://paluniv.edu.ps/wp-content/uploads/2024/05/%D8%AF%D9%84%D9%8A%D9%84-%D8%A7%D9%84%D8%B7%D8%A7%D9%84%D8%A8-2024-2.pdf"),
    "student_guide_2023_2024.pdf": ("دليل الطالب 2023-2024 (نسخة أقدم)", "2023",
        "https://www.paluniv.edu.ps/wp-content/uploads/2023/06/2023-2024-%D8%AF%D9%84%D9%8A%D9%84-%D8%A7%D9%84%D8%B7%D8%A7%D9%84%D8%A8.pdf"),
    "bachelor_degree_regulation.pdf": ("نظام منح درجة البكالوريوس", "2016",
        "http://paluniv.edu.ps/wp-content/uploads/2016/01/Bachelor.pdf"),
    "diploma_degree_regulation.pdf": ("نظام منح درجة الدبلوم", "2016",
        "http://paluniv.edu.ps/wp-content/uploads/2016/01/doplom.pdf"),
    "basic_statute.pdf": ("النظام الأساسي للجامعة", "2020",
        "https://paluniv.edu.ps/wp-content/uploads/2020/09/%D8%A7%D9%84%D9%86%D8%B8%D8%A7%D9%85-%D8%A7%D9%84%D8%A7%D8%B3%D8%A7%D8%B3%D9%8A.pdf"),
}

PAGES = {   # page_id: (file name, title)
    136966: ("admission_registration_regulations", "الأنظمة واللوائح للقبول والتسجيل"),
    136965: ("bachelor_requirements", "شروط منح درجة البكالوريوس"),
    15551: ("admission_faq", "الأسئلة الشائعة - القبول والتسجيل"),
    137891: ("new_students_admission", "قبول الطلبة الجدد"),
    136964: ("new_students_enrollment", "الطلبة الجدد - آلية الالتحاق"),
    13757: ("scholarships", "المنح والمساعدات"),
    138288: ("payment_palpay", "الدفع عن طريق PalPay"),
    14224: ("admission_deanship", "عمادة القبول والتسجيل"),
    15510: ("bachelor_programs", "برامج البكالوريوس"),
    15609: ("diploma_programs", "برامج الدبلوم"),
}

FACULTIES = {
    3167: "كلية العلوم الإنسانية والتربوية",
    3182: "كلية العلوم الإدارية والمالية",
    3196: "كلية العلوم الطبية المساندة",
    3205: "كلية الهندسة وتكنولوجيا المعلومات",
    3212: "كلية الحقوق",
    136960: "كلية المهن والعلوم التطبيقية",
}


def get(url: str, binary: bool = False, tries: int = 3):
    url = urllib.parse.quote(url, safe=":/?=&%#")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", errors="ignore")
        except Exception as e:
            if i == tries - 1:
                print(f"   ! failed {url[:90]} ({e})")
                return None
            time.sleep(2)


def page_ids(html: str) -> set[int]:
    return {int(m) for m in re.findall(r"[?&]page_id=(\d+)", html or "")}


def title_of(html: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html or "", re.S)
    t = re.sub(r"\s+", " ", m.group(1)).strip() if m else fallback
    t = re.split(r"\s[\|–-]\s", t)[0].strip()
    return t or fallback


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "programs").mkdir(exist_ok=True)
    meta_path = OUT / "_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    # remove the demo sample docs so they don't mix with real data
    for demo in ["student_regulations_2024.md", "student_regulations_2022_old.md", "cs_courses.csv",
                 "registration_guide_en.pdf"]:
        if (OUT / demo).exists():
            (OUT / demo).rename(OUT / f"_demo_{demo}")          # files starting with _ are ignored
            meta.pop(demo, None)

    print("1) PDFs")
    for name, (title, date, url) in PDFS.items():
        data = get(url, binary=True)
        if data and data[:4] == b"%PDF":
            (OUT / name).write_bytes(data)
            meta[name] = {"title": title, "date": date, "url": url}
            print(f"   ok {name} ({len(data)//1024} KB)")
        time.sleep(0.5)

    print("2) Regulation pages")
    for pid, (name, title) in PAGES.items():
        url = f"{BASE}?page_id={pid}"
        html = get(url)
        if html:
            (OUT / f"{name}.html").write_text(html, encoding="utf-8")
            meta[f"{name}.html"] = {"title": title, "date": "2025", "url": url}
            print(f"   ok {name}")
        time.sleep(0.5)

    print("3) Programs (study plans + course descriptions)")
    # A link counts as a program page if the page itself contains a study plan / course list.
    seen = set(PAGES) | set(FACULTIES)
    sources = {fid: fname for fid, fname in FACULTIES.items()}
    sources.update({15510: "برامج البكالوريوس", 15609: "برامج الدبلوم"})
    kept = 0
    for fid, fname in sources.items():
        html = get(f"{BASE}?page_id={fid}")
        if not html:
            continue
        cands = sorted(page_ids(html) - seen)
        print(f"   {fname}: checking {len(cands)} links")
        for pid in cands[:120]:
            seen.add(pid)
            url = f"{BASE}?page_id={pid}"
            ph = get(url)
            time.sleep(0.25)
            if not ph or not any(k in ph for k in ("الخطة الدراسية", "اسم المساق", "وصف المساقات")):
                continue
            title = title_of(ph, f"برنامج {pid}")
            fn = f"programs/{pid}.html"
            (OUT / fn).write_text(ph, encoding="utf-8")
            meta[fn] = {"title": title, "faculty": fname, "date": "2025", "url": url}
            kept += 1
            print(f"      ok {pid}  {title}")
    print(f"   program pages kept: {kept}")

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDone: {len(meta)} documents in {OUT}\nNext: python -m scripts.build_index")


if __name__ == "__main__":
    sys.exit(main())
