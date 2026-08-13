from export_srt import build_srt, format_timestamp


def test_format_timestamp():
    assert format_timestamp(0) == "00:00:00,000"
    assert format_timestamp(61.5) == "00:01:01,500"
    assert format_timestamp(3661.234) == "01:01:01,234"


def test_build_srt_basic():
    manifest = {
        "scenes": [
            {"id": "01", "narration": "Hello world. Second sentence.", "duration_s": 6},
        ]
    }
    srt = build_srt(manifest)
    assert "00:00:00,000 -->" in srt
    assert "Hello world." in srt
    assert "Second sentence." in srt
    assert srt.count(" --> ") == 2


def test_build_srt_skips_silent_scenes():
    manifest = {
        "scenes": [
            {"id": "01", "narration": "", "duration_s": 3},
            {"id": "02", "narration": "One.", "duration_s": 3},
        ]
    }
    srt = build_srt(manifest)
    assert srt.count(" --> ") == 1
    # The cue starts after the 3s silent scene.
    assert "00:00:03,000 -->" in srt


def test_build_srt_empty():
    assert build_srt({"scenes": []}) == ""
    assert build_srt({"scenes": [{"id": "01", "duration_s": 5}]}) == ""
