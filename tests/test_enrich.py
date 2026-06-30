import matcher.enrich as e
from matcher.data_io import Slot, Student


def test_sync_retries_then_base_fallback(monkeypatch):
    """A row that always errors is attempted 1 + max_retries times, then falls
    back to a base (unenriched) record — empty tags, parsed gender, flagged."""
    calls = {"n": 0}
    monkeypatch.setattr(e, "_client", lambda key: object())

    def boom(*a, **k):
        calls["n"] += 1
        raise RuntimeError("api down")

    monkeypatch.setattr(e, "_one_llm_call", boom)
    monkeypatch.setattr(e.time, "sleep", lambda *_: None)  # don't actually wait

    s = Student("s1", "S", "Male", [Slot("monday", 540)], "nervous", "cùng giới (Male)")
    out = e.enrich_sync([s], "student", "model", "key", max_workers=1, max_retries=2)

    assert calls["n"] == 3                          # 1 initial + 2 retries
    assert out["s1"]["source"] == "unenriched"      # no keyword tagging
    assert out["s1"]["llm_failed"] is True          # flagged for transparency
    assert out["s1"]["desired_focus"] == []         # semantic tags empty until LLM
    assert out["s1"]["requested_mentor_gender"] == "Male"  # gender floor still parsed


def test_sync_succeeds_without_retry(monkeypatch):
    calls = {"n": 0}
    monkeypatch.setattr(e, "_client", lambda key: object())

    def ok(client, model, system, payload, schema, name):
        calls["n"] += 1
        return {"requested_mentor_gender": None, "desired_focus": ["study-habits"],
                "desired_traits": [], "symptom_category": "none"}

    monkeypatch.setattr(e, "_one_llm_call", ok)
    s = Student("s1", "S", "Male", [Slot("monday", 540)], "", "")
    out = e.enrich_sync([s], "student", "model", "key", max_workers=1, max_retries=2)

    assert calls["n"] == 1                        # no retry needed
    assert out["s1"]["source"] == "llm"
