import hashlib

from app.agents.discovery_service import (
    _content_hash,
    _location_type_from_location,
    _normalize_field,
    _role_type_from_title,
)


def test_normalize_field_removes_extra_whitespace():
    assert _normalize_field("  Hello   World \n") == "Hello World"


def test_role_type_infers_intern_and_senior():
    assert _role_type_from_title("Software Engineering Intern") == "intern"
    assert _role_type_from_title("Senior Backend Engineer") == "senior"
    assert _role_type_from_title("Backend Engineer") == "associate"


def test_location_type_parses_remote_and_hybrid():
    assert _location_type_from_location("Remote") == "remote"
    assert _location_type_from_location("Bengaluru (Hybrid)") == "hybrid"
    assert _location_type_from_location("Jaipur, India") == "onsite"


def test_content_hash_is_consistent():
    h1 = _content_hash("Title", "Company", "Loc")
    h2 = hashlib.sha256(b"Title|Company|Loc").hexdigest()
    assert h1 == h2
