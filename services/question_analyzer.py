"""
Question Analyzer for TourAI RAG Pipeline.
Extracts structured intent from Vietnamese natural language queries.
"""

import re
import unicodedata

DESTINATION_MAP = {
    "ha long": "Hạ Long",
    "hạ long": "Hạ Long",
    "da nang": "Đà Nẵng",
    "đà nẵng": "Đà Nẵng",
    "hoi an": "Đà Nẵng",
    "hội an": "Đà Nẵng",
    "phu quoc": "Phú Quốc",
    "phú quốc": "Phú Quốc",
    "sa pa": "Sa Pa",
    "sapa": "Sa Pa",
    "fansipan": "Sa Pa",
    "da lat": "Đà Lạt",
    "đà lạt": "Đà Lạt",
    "dalat": "Đà Lạt",
    "ha giang": "Hà Giang",
    "hà giang": "Hà Giang",
    "dong van": "Hà Giang",
    "đồng văn": "Hà Giang",
    "ma pi leng": "Hà Giang",
    "mã pí lèng": "Hà Giang",
    "nha trang": "Nha Trang",
    "ninh binh": "Ninh Bình",
    "ninh bình": "Ninh Bình",
    "trang an": "Ninh Bình",
    "tràng an": "Ninh Bình",
    "tam coc": "Ninh Bình",
    "tàm cốc": "Ninh Bình",
    "hue": "Huế",
    "huế": "Huế",
    "quy nhon": "Quy Nhơn",
    "quy nhơn": "Quy Nhơn",
    "phu yen": "Phú Yên",
    "phú yên": "Phú Yên",
    "vung tau": "Vũng Tàu",
    "vũng tàu": "Vũng Tàu",
    "con dao": "Côn Đảo",
    "côn đảo": "Côn Đảo",
    "moc chau": "Mộc Châu",
    "mộc châu": "Mộc Châu",
    "buon ma thuot": "Buôn Ma Thuột",
    "buôn ma thuột": "Buôn Ma Thuột",
}

KEYWORD_DESTINATIONS = {
    "biển": ["Hạ Long", "Đà Nẵng", "Hội An", "Phú Quốc", "Nha Trang", "Huế", "Quy Nhơn", "Phú Yên", "Vũng Tàu", "Côn Đảo"],
    "đảo": ["Phú Quốc", "Côn Đảo"],
    "cano": ["Phú Quốc"],
    "du thuyền": ["Hạ Long"],
    "núi": ["Sa Pa", "Hà Giang", "Đà Lạt", "Mộc Châu"],
    "săn mây": ["Sa Pa", "Đà Lạt", "Hà Giang", "Mộc Châu"],
    "đèo": ["Hà Giang"],
    "hoa": ["Đà Lạt"],
}

# Verbs signalling a "summarize / build a report" request.
_SUMMARY_VERBS = [
    "tóm tắt", "tổng hợp", "phân tích", "thống kê", "báo cáo", "tổng kết",
    "summary", "summarize",
]

# Nouns signalling the request is about CUSTOMER FEEDBACK (not tours).
_FEEDBACK_NOUNS = [
    "phản hồi", "đánh giá", "nhận xét", "góp ý", "ý kiến", "review", "feedback",
]

def remove_accents(input_str: str) -> str:
    """Converts Vietnamese characters to ASCII without diacritics."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

def matches_term(text: str, term: str) -> bool:
    """Whole-word match of `term` inside `text`.

    Word boundaries are required so short terms never match inside unrelated
    words: accent-stripped "khoảng" -> "khoang" must NOT trigger keyword "hoa",
    otherwise the query is wrongly mapped to Đà Lạt and returns zero tours.
    """
    if not text or not term:
        return False
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None

def to_vnd(num_str: str, unit: str) -> float:
    """Converts a numeric string + Vietnamese unit to VND."""
    value = float(num_str.replace(",", "."))
    return value * 1_000 if unit in ("nghin", "ngan", "k") else value * 1_000_000

class QuestionAnalyzer:
    @staticmethod
    def parse_price(text: str):
        """Extracts min and max prices from text in VND."""
        min_price = None
        max_price = None
        lower = text.lower()

        # Handle 'dưới / tối đa X triệu / tr / củ / m'
        match_under_trieu = re.search(r'(?:dưới|tối đa|nhỏ hơn|<=|dưới tầm)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|củ|m\b)', lower)
        if match_under_trieu:
            val = float(match_under_trieu.group(1).replace(',', '.'))
            max_price = val * 1_000_000

        # Handle 'dưới / tối đa X nghìn / ngàn / k'
        match_under_nghin = re.search(r'(?:dưới|tối đa|nhỏ hơn|<=|dưới tầm)\s*(\d+(?:[.,]\d+)?)\s*(?:nghìn|ngàn|k\b)', lower)
        if match_under_nghin and not max_price:
            val = float(match_under_nghin.group(1).replace(',', '.'))
            max_price = val * 1_000

        # Pattern like "2tr5"
        match_tr_k = re.search(r'(?:dưới|tối đa|nhỏ hơn|<=)?\s*(\d+)tr(\d+)', lower)
        if match_tr_k and not max_price:
            major = int(match_tr_k.group(1))
            minor = int(match_tr_k.group(2))
            max_price = major * 1_000_000 + minor * 100_000

        # Pattern like "dưới 5.000.000" or "dưới 5000000"
        match_under_num = re.search(r'(?:dưới|tối đa|nhỏ hơn|<=)\s*([\d.]+)\s*(?:vnd|vnđ|đ)?\b', lower)
        if match_under_num and not max_price:
            raw = match_under_num.group(1).replace('.', '')
            if raw.isdigit() and len(raw) >= 5:
                max_price = float(raw)

        # Handle range: "từ X đến Y triệu" or "tầm X - Y triệu"
        match_range = re.search(r'(?:từ|tầm|khoảng)\s*(\d+(?:[.,]\d+)?)\s*(?:đến|-)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|củ)', lower)
        if match_range:
            min_price = float(match_range.group(1).replace(',', '.')) * 1_000_000
            max_price = float(match_range.group(2).replace(',', '.')) * 1_000_000

        # Handle "trên / từ X triệu"
        match_above = re.search(r'(?:trên|từ|ít nhất|lớn hơn|>=)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|củ)', lower)
        if match_above and not min_price:
            min_price = float(match_above.group(1).replace(',', '.')) * 1_000_000

        # Handle "trên / từ X nghìn / ngàn / k"
        match_above_nghin = re.search(r'(?:trên|từ|ít nhất|lớn hơn|>=)\s*(\d+(?:[.,]\d+)?)\s*(?:nghìn|ngàn|k\b)', lower)
        if match_above_nghin and not min_price:
            min_price = float(match_above_nghin.group(1).replace(',', '.')) * 1_000

        # Fallback pass (accent-insensitive, runs only when nothing matched above):
        # handles inputs without diacritics ("duoi 5 trieu") and budget phrases
        # that carry no explicit prefix ("khoảng 5 triệu", "tour 5 triệu", "tôi có 5 triệu").
        plain = remove_accents(text.lower())

        # "duoi / toi da / nho hon / khong qua / tam do X trieu|nghin"
        if min_price is None and max_price is None:
            m_under = re.search(
                r"(?<!\w)(?:duoi|toi da|nho hon|khong qua|tam do)(?!\w)\s*"
                r"(\d+(?:[.,]\d+)?)\s*(trieu|tr|cu|nghin|ngan|k)(?!\w)",
                plain,
            )
            if m_under:
                max_price = to_vnd(m_under.group(1), m_under.group(2))

        # "tu / tam / khoang X den Y trieu" (range without diacritics)
        if min_price is None and max_price is None:
            m_range = re.search(
                r"(?<!\w)(?:tu|tam|khoang)(?!\w)\s*"
                r"(\d+(?:[.,]\d+)?)\s*(?:den|-)\s*(\d+(?:[.,]\d+)?)\s*(?:trieu|tr|cu)(?!\w)",
                plain,
            )
            if m_range:
                min_price = float(m_range.group(1).replace(",", ".")) * 1_000_000
                max_price = float(m_range.group(2).replace(",", ".")) * 1_000_000

        # "tren / tu / it nhat / lon hon X trieu"
        if min_price is None and max_price is None:
            m_above = re.search(
                r"(?<!\w)(?:tren|tu|it nhat|lon hon)(?!\w)\s*"
                r"(\d+(?:[.,]\d+)?)\s*(trieu|tr|cu|nghin|ngan|k)(?!\w)",
                plain,
            )
            if m_above:
                min_price = to_vnd(m_above.group(1), m_above.group(2))

        # Bare budget: "tour 5 triệu", "giá 5 triệu", "5 triệu" -> budget ceiling
        if min_price is None and max_price is None:
            m_bare = re.search(r"(\d+(?:[.,]\d+)?)\s*(trieu|tr|cu)(?!\w)", plain)
            if m_bare:
                max_price = to_vnd(m_bare.group(1), m_bare.group(2))

        return min_price, max_price

    @staticmethod
    def parse_duration(text: str):
        """Extracts duration in days from text."""
        lower = text.lower()
        match = re.search(r'(\d+)\s*(?:ngày|n\b|ngay)', lower)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def parse_duration_range(text: str):
        """Extracts a day range like '3-4 ngày' / 'từ 3 đến 4 ngày' -> (3, 4).

        Returns None when the query asks for a single duration (or none at all),
        so callers can keep using `duration_days` as a plain integer.
        """
        plain = remove_accents(text.lower())
        match = re.search(r'(\d+)\s*(?:den|-|~)\s*(\d+)\s*(?:ngay|n\b)', plain)
        if match:
            lo, hi = int(match.group(1)), int(match.group(2))
            if lo == hi:
                return None
            return (lo, hi) if lo < hi else (hi, lo)
        return None

    @staticmethod
    def is_feedback_summary_question(question: str) -> bool:
        """
        Detects requests asking to summarize / report CUSTOMER FEEDBACK
        (e.g. "Tóm tắt phản hồi khách hàng", "Phân tích đánh giá của khách").

        The chat assistant must answer these with a real feedback report from the
        database instead of treating them as tour-consultation questions.
        Both a summary verb AND a feedback noun must appear; a question like
        "Tóm tắt giúp tôi tour Sa Pa" or "Tour nào khách hàng đánh giá cao?" is
        NOT considered a feedback-summary request.
        """
        if not question or not question.strip():
            return False

        plain = remove_accents(question.lower())
        has_summary_verb = any(matches_term(plain, remove_accents(verb)) for verb in _SUMMARY_VERBS)
        has_feedback_noun = any(matches_term(plain, remove_accents(noun)) for noun in _FEEDBACK_NOUNS)
        return has_summary_verb and has_feedback_noun

    @staticmethod
    def analyze_question(question: str) -> dict:
        """
        Takes raw natural language Vietnamese question and returns structured intent.
        """
        if not question or not question.strip():
            return {
                "destinations": [],
                "min_price": None,
                "max_price": None,
                "duration_days": None,
                "keywords": [],
                "sort_by": None
            }

        q_clean = question.strip()
        q_lower = q_clean.lower()
        q_no_accent = remove_accents(q_clean)

        # 1. Identify destinations (whole-word matching avoids false positives)
        matched_destinations = set()
        for key, dest_name in DESTINATION_MAP.items():
            if matches_term(q_lower, key) or matches_term(q_no_accent, remove_accents(key)):
                matched_destinations.add(dest_name)

        # 2. Extract keywords & map to destinations if none found
        extracted_keywords = []
        for kw, dest_list in KEYWORD_DESTINATIONS.items():
            if matches_term(q_lower, kw) or matches_term(q_no_accent, remove_accents(kw)):
                extracted_keywords.append(kw)
                if not matched_destinations:
                    for d in dest_list:
                        matched_destinations.add(d)

        # 3. Parse price limits
        min_price, max_price = QuestionAnalyzer.parse_price(q_clean)

        # 4. Parse duration: a range like "3-4 ngày" becomes [3, 4],
        #    a single value stays an integer (e.g. 3).
        duration_range = QuestionAnalyzer.parse_duration_range(q_clean)
        if duration_range:
            duration_days = [duration_range[0], duration_range[1]]
        else:
            duration_days = QuestionAnalyzer.parse_duration(q_clean)

        # 5. Determine sort preference
        sort_by = None
        if any(term in q_lower for term in ["giá rẻ nhất", "rẻ nhất", "thấp nhất", "tiết kiệm nhất"]):
            sort_by = "price_asc"
        elif any(term in q_lower for term in ["cao cấp", "sang trọng nhất", "đắt nhất", "vip nhất"]):
            sort_by = "price_desc"

        return {
            "destinations": sorted(list(matched_destinations)),
            "min_price": min_price,
            "max_price": max_price,
            "duration_days": duration_days,
            "keywords": extracted_keywords,
            "sort_by": sort_by,
            "raw_question": q_clean
        }

