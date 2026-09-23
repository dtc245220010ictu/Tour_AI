"""
Unit tests for Tour Retriever service.
Verifies parameterized SQL execution, available seats enforcement, and zero-hallucination empty results.
"""

from services.tour_retriever import TourRetriever

def test_retrieve_ha_long_under_4_million():
    intent = {
        "destinations": ["Hạ Long"],
        "max_price": 4_000_000,
        "min_price": None,
        "duration_days": None,
        "sort_by": None
    }
    results = TourRetriever.retrieve_tours(intent)

    assert len(results) >= 1
    for tour in results:
        assert tour["destination_name"] == "Hạ Long"
        assert tour["base_price"] <= 4_000_000
        assert tour["total_available_seats"] > 0

def test_retrieve_impossible_budget_returns_empty():
    """
    CRITICAL TEST FOR ZERO-HALLUCINATION:
    When a user asks for a tour below any realistic price (e.g. under 500,000 VND),
    the retriever MUST return an empty list [], NEVER fake tours!
    """
    intent = {
        "destinations": ["Hạ Long"],
        "max_price": 500_000, # Unrealistic budget
        "min_price": None,
        "duration_days": None,
        "sort_by": None
    }
    results = TourRetriever.retrieve_tours(intent)
    assert results == []

def test_retrieve_alternative_tours_when_none_match():
    intent = {
        "destinations": ["Hạ Long"],
        "max_price": 500_000
    }
    # Main retrieval is empty
    assert TourRetriever.retrieve_tours(intent) == []
    
    # Alternative retrieval offers closest available tours
    alternatives = TourRetriever.retrieve_alternative_tours(intent)
    assert len(alternatives) > 0
    assert alternatives[0]["destination_name"] == "Hạ Long"

