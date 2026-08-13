from capture_screens import slugify


def test_slugify_basic():
    assert slugify("home page") == "home-page"
    assert slugify("Dashboard (v2)") == "Dashboard-v2"


def test_slugify_paths():
    assert slugify("/users/:id") == "users-id"
    assert slugify("a/b") == "a-b"


def test_slugify_edge_cases():
    assert slugify("  spaces  ") == "spaces"
    assert slugify("") == "shot"
    assert slugify("!!!") == "shot"
