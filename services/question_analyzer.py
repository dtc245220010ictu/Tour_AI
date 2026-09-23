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
}

KEYWORD_DESTINATIONS = {
    "biển": ["Hạ Long", "Đà Nẵng", "Phú Quốc"],
    "đảo": ["Phú Quốc"],
    "cano": ["Phú Quốc"],
    "du thuyền": ["Hạ Long"],
    "núi": ["Sa Pa", "Hà Giang", "Đà Lạt"],
    "săn mây": ["Sa Pa", "Đà Lạt", "Hà Giang"],
    "đèo": ["Hà Giang"],
    "hoa": ["Đà Lạt"],
}

def remove_accents(input_str: str) -> str:
    """Converts Vietnamese characters to ASCII without diacritics."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

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

        # 1. Identify destinations
        matched_destinations = set()
        for key, dest_name in DESTINATION_MAP.items():
            if key in q_lower or remove_accents(key) in q_no_accent:
                matched_destinations.add(dest_name)

        # 2. Extract keywords & map to destinations if none found
        extracted_keywords = []
        for kw, dest_list in KEYWORD_DESTINATIONS.items():
            if kw in q_lower or remove_accents(kw) in q_no_accent:
                extracted_keywords.append(kw)
                if not matched_destinations:
                    for d in dest_list:
                        matched_destinations.add(d)

        # 3. Parse price limits
        min_price, max_price = QuestionAnalyzer.parse_price(q_clean)

        # 4. Parse duration
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

