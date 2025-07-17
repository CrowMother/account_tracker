from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from secrets import get_secret  # noqa: E402


def test_get_secret_from_env(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("MY_KEY=from_file\n")
    monkeypatch.setenv("MY_KEY", "from_env")
    result = get_secret("MY_KEY", str(env_file))
    assert result == "from_env"


def test_get_secret_from_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("MY_KEY=from_file\n")
    monkeypatch.delenv("MY_KEY", raising=False)
    result = get_secret("MY_KEY", str(env_file))
    assert result == "from_file"


def test_get_secret_missing(monkeypatch, tmp_path, caplog):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    monkeypatch.delenv("MY_KEY", raising=False)
    with caplog.at_level("ERROR"):
        result = get_secret("MY_KEY", str(env_file))
    assert result is None
    assert "Error getting secret" in caplog.text
