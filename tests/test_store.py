from matcher import store


def test_not_configured_without_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    assert store.configured() is False
    assert store.remote_load("student") is None       # signals "use disk"
    assert store.remote_save("student", {"a": {}}) is False
    assert store.backend_name() == "local disk"


def test_configured_flag_with_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "key")
    assert store.configured() is True
    assert store.backend_name() == "Supabase"
