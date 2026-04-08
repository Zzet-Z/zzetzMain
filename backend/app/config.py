from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def _load_env_file() -> None:
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_default_config() -> dict[str, object]:
    _load_env_file()

    upload_dir = os.environ.get("UPLOAD_FOLDER", "uploads")
    flask_env = os.environ.get("FLASK_ENV", "development")

    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev"),
        "DATABASE_URL": os.environ.get("DATABASE_URL", "sqlite:///app.db"),
        "UPLOAD_DIR": upload_dir,
        "MAX_ACTIVE_SESSIONS": 5,
        "MAX_UPLOAD_SIZE_MB": 8,
        "MAX_UPLOAD_COUNT": 12,
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "OPENAI_MODEL": os.environ.get("OPENAI_MODEL", "qwen3.5-plus"),
        "OPENAI_BASE_URL": os.environ.get(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        "OPENAI_TIMEOUT": int(os.environ.get("OPENAI_TIMEOUT", "60")),
        "ENV": flask_env,
        "DEBUG": flask_env == "development",
    }
