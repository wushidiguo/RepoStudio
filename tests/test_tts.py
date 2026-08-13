from tts import set_voiceover_meta, split_sentences


def test_set_voiceover_meta():
    manifest = {"scenes": []}
    set_voiceover_meta(manifest, "edge", "audio/voiceover.mp3")
    assert manifest["voiceover"] == {"engine": "edge", "file": "audio/voiceover.mp3"}


def test_split_sentences_latin():
    assert split_sentences("First sentence. Second sentence!") == [
        "First sentence.",
        "Second sentence!",
    ]


def test_split_sentences_single():
    assert split_sentences("One.") == ["One."]
    assert split_sentences("   ") == []


def test_split_sentences_keeps_decimals():
    # "3.12" is not a sentence boundary.
    assert split_sentences("Python 3.12 is fast.") == ["Python 3.12 is fast."]


def test_split_sentences_cjk():
    assert split_sentences("你好。世界！") == ["你好。", "世界！"]
