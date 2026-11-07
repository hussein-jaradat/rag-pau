"""Arabic text utilities: cleaning PDF artefacts, normalisation for search,
light stemming for BM25, and dialect -> MSA query expansion.

Why this matters: Arabic PDFs often come out with presentation-form glyphs,
invisible bidi marks and sometimes reversed word order. And users type in
Palestinian dialect ("ليش ورق الزيتون بصفّر؟") while documents are in MSA.
"""
from __future__ import annotations

import re
import unicodedata

AR_RANGE = re.compile(r"[؀-ۿ]")
BIDI_MARKS = re.compile(r"[​-‏‪-‮⁦-⁩﻿]")
DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
TATWEEL = "ـ"

# Very common function words, used to detect reversed text coming out of PDFs.
_COMMON = {"في", "من", "على", "إلى", "الى", "عن", "التي", "الذي", "أن", "مع", "هذا", "هذه"}
_COMMON_REV = {w[::-1] for w in _COMMON}

STOPWORDS = {
    "في", "من", "على", "الى", "إلى", "عن", "ان", "أن", "إن", "او", "أو", "ثم", "مع", "هذا", "هذه",
    "ذلك", "تلك", "التي", "الذي", "الذين", "ما", "ماذا", "لماذا", "كيف", "هل", "كم", "متى", "اين",
    "أين", "و", "يا", "لا", "لم", "لن", "قد", "كان", "كانت", "يكون", "هو", "هي", "هم", "انا", "أنا",
    "نحن", "انت", "أنت", "كل", "بعض", "غير", "بين", "عند", "اذا", "إذا", "حتى", "بعد", "قبل",
    # dialect fillers
    "شو", "ايش", "إيش", "ليش", "وين", "قديش", "كيفاش", "بدي", "بدنا", "هاد", "هاي", "هيك", "اشي",
    "the", "a", "an", "of", "to", "in", "is", "are", "and", "or", "for", "on", "what", "how",
    "do", "does", "i", "my", "can", "with", "be", "it", "this", "that", "which", "who", "when",
}

# Palestinian/Levantine dialect -> MSA hints (expanded at query time).
DIALECT_MAP = {
    "ليش": "لماذا", "شو": "ما", "ايش": "ما", "إيش": "ما", "وين": "أين", "قديش": "كم",
    "امتى": "متى", "إمتى": "متى", "بدي": "أريد", "بدنا": "نريد", "مش": "ليس", "هلأ": "الآن",
    "هسا": "الآن", "هسه": "الآن", "كتير": "كثير", "منيح": "جيد", "بصفر": "اصفرار",
    "بيصفر": "اصفرار", "صفار": "اصفرار", "مصفر": "اصفرار", "ورق": "أوراق", "شجر": "أشجار",
    "دوا": "دواء", "حبة": "قرص", "حبوب": "أقراص", "وجع": "ألم", "بوجعني": "ألم", "راسي": "الرأس",
    "سخنة": "حرارة", "سخونة": "حمى", "مصاري": "مال", "فلوس": "مال", "مصروف": "رسوم",
    "شغل": "عمل", "بشتغل": "يعمل", "معاش": "راتب", "اجازة": "إجازة", "فرصة": "إجازة",
    "مادة": "مساق", "مواد": "مساقات", "سجل": "تسجيل", "بسجل": "تسجيل", "اسقط": "رسوب",
    "رسبت": "رسوب", "سقطت": "رسوب", "معدلي": "المعدل", "تخرج": "التخرج", "زبون": "عميل",
    "عقد": "عقد", "بلدية": "البلدية", "ترخيص": "ترخيص", "رخصة": "ترخيص",
}


def strip_artifacts(text: str) -> str:
    """Fix the usual PDF extraction problems (safe for any language)."""
    text = unicodedata.normalize("NFKC", text)        # presentation forms -> letters
    text = BIDI_MARKS.sub("", text)
    text = text.replace(TATWEEL, "")
    text = text.replace(" ", " ")
    return text


def is_arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    return sum(1 for c in letters if AR_RANGE.match(c)) / len(letters) > 0.3


def fix_reversed_lines(text: str) -> str:
    """Some PDF extractors output Arabic characters reversed (visual order).
    Detect it with common function words and reverse each affected line."""
    words = re.findall(r"[؀-ۿ]+", text)
    if len(words) < 20:
        return text
    normal = sum(w in _COMMON for w in words)
    reversed_ = sum(w in _COMMON_REV for w in words)
    if reversed_ <= normal * 1.5 or reversed_ < 3:
        return text
    return "\n".join(line[::-1] if AR_RANGE.search(line) else line for line in text.split("\n"))


def normalize(text: str) -> str:
    """Search-time normalisation (applied to BOTH documents and queries)."""
    text = strip_artifacts(text).lower()
    text = DIACRITICS.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    text = re.sub(r"[٠-٩]", lambda m: str(ord(m.group()) - 0x0660), text)   # Arabic-Indic digits
    text = re.sub(r"[۰-۹]", lambda m: str(ord(m.group()) - 0x06F0), text)
    return text


_PREFIXES = ("وال", "بال", "كال", "فال", "لل", "ال")
_SUFFIXES = ("ات", "ون", "ين", "ان", "ها", "هم", "هن", "كم", "نا", "يه", "ه", "ي")


def light_stem(word: str) -> str:
    """Tiny light stemmer: strips the article/conjunction prefixes and common
    suffixes. Good enough to make BM25 match الطالب / طالب / والطلاب closer."""
    if not AR_RANGE.search(word):
        return word[:-1] if len(word) > 4 and word.endswith("s") else word
    for p in _PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 2:
            word = word[len(p):]
            break
    for s in _SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 3:
            word = word[: -len(s)]
            break
    return word


AR_LETTERS = "\u0621-\u063a\u0641-\u064a\u0671-\u06d3"   # letters only (no ؟ ، ؛)
TOKEN_RE = re.compile(f"[{AR_LETTERS}]+|[a-z0-9]+(?:[-_.][a-z0-9]+)*")


def tokenize(text: str, stem: bool = True) -> list[str]:
    toks = TOKEN_RE.findall(normalize(text))
    out = []
    for t in toks:
        if len(t) > 2 and t[0] in "وف" and t[1:] in STOPWORDS:   # وكم / فما -> stopword
            continue
        if t in STOPWORDS or (len(t) < 2 and not t.isdigit()):
            continue
        out.append(light_stem(t) if stem else t)
    return out


def expand_dialect(query: str) -> str:
    """Add MSA equivalents of dialect words (keeps the original words too)."""
    extra = []
    for w in re.findall(f"[{AR_LETTERS}]+", query):
        base = w[1:] if w.startswith(("و", "ب")) and w[1:] in DIALECT_MAP else w
        if base in DIALECT_MAP and DIALECT_MAP[base] not in query:
            extra.append(DIALECT_MAP[base])
    return query if not extra else f"{query} {' '.join(extra)}"
