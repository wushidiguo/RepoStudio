import json
import sys

import pytest

import estimate_duration


def test_count_words_ascii():
    assert estimate_duration.count_words("hello world") == 2
    assert estimate_duration.count_words("don't stop") == 2
    assert estimate_duration.count_words("state-of-the-art tool") == 2


def test_count_words_accented_latin():
    # Regression: accented letters must not split a word ("déjà" was "d" + "j").
    assert estimate_duration.count_words("déjà vu") == 2
    assert estimate_duration.count_words("café naïveté") == 2
    assert estimate_duration.count_words("São Paulo") == 2


def test_count_words_numbers():
    assert estimate_duration.count_words("42,000 lines of Python") == 5


def test_count_words_excludes_cjk():
    assert estimate_duration.count_words("你好 world") == 1


def test_count_cjk_chars():
    assert estimate_duration.count_cjk_chars("你好世界") == 4
    assert estimate_duration.count_cjk_chars("hello") == 0


def test_estimate_pure_english():
    assert estimate_duration.estimate_scene_duration("hello world", "en") == pytest.approx(
        2 / estimate_duration.WORDS_PER_SEC["en"]
    )


def test_estimate_cjk_counts_english_too():
    # Regression: English words mixed into a CJK narration were previously ignored.
    est = estimate_duration.estimate_scene_duration("你好世界 hello world", "zh")
    expected = (
        4 / estimate_duration.CHARS_PER_SEC_DEFAULT + 2 / estimate_duration.WORDS_PER_SEC["en"]
    )
    assert est == pytest.approx(expected)


def test_estimate_accented_language():
    # "déjà vu" is 2 French words, not 3.
    assert estimate_duration.estimate_scene_duration("déjà vu", "fr") == pytest.approx(
        2 / estimate_duration.WORDS_PER_SEC["fr"]
    )


def test_estimate_empty():
    assert estimate_duration.estimate_scene_duration("", "en") == 0.0
    assert estimate_duration.estimate_scene_duration("   ", "ja") == 0.0


def _write_manifest(path, scenes):
    path.write_text(
        json.dumps({"meta": {"language": "en"}, "scenes": scenes}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_main_pass(tmp_path, monkeypatch):
    m = tmp_path / "manifest.json"
    _write_manifest(m, [{"id": "01", "narration": "word " * 200, "duration_s": 80}])
    monkeypatch.setattr(sys, "argv", ["estimate_duration.py", "--manifest", str(m), "--json"])
    assert estimate_duration.main() == 0


def test_main_fail_too_short(tmp_path, monkeypatch):
    m = tmp_path / "manifest.json"
    _write_manifest(m, [{"id": "01", "narration": "word " * 5, "duration_s": 10}])
    monkeypatch.setattr(sys, "argv", ["estimate_duration.py", "--manifest", str(m)])
    assert estimate_duration.main() == 2
