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

def test_retrieve_duration_range_filter():
    """A day range like [3, 4] must match tours of 3 OR 4 days (inclusive)."""
    intent = {
        "destinations": [],
        "max_price": 5_000_000,
        "min_price": None,
        "duration_days": [3, 4],
        "sort_by": None
    }
    results = TourRetriever.retrieve_tours(intent)

    assert len(results) >= 1
    for tour in results:
        assert 3 <= tour["duration_days"] <= 4
        assert tour["base_price"] <= 5_000_000

def test_alternative_tours_fall_back_when_destination_has_no_tours():
    """When the requested destination has no tours at all, alternatives must
    still suggest OTHER available tours so the chatbot can introduce them
    after honestly reporting that no matching tour exists."""
    intent = {"destinations": ["Hà Nội"]}

    assert TourRetriever.retrieve_tours(intent) == []

    alternatives = TourRetriever.retrieve_alternative_tours(intent)
    assert len(alternatives) > 0
    assert all(alt["destination_name"] != "Hà Nội" for alt in alternatives)

