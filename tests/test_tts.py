from tts import set_voiceover_meta


def test_set_voiceover_meta():
    manifest = {"scenes": []}
    set_voiceover_meta(manifest, "edge", "audio/voiceover.mp3")
    assert manifest["voiceover"] == {"engine": "edge", "file": "audio/voiceover.mp3"}
