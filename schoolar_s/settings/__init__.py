import os
from pathlib import Path


def _load_env_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


env_label = (os.getenv("DJANGO_ENV") or "").lower()
env_file = None
if env_label in {"prod", "production"}:
    env_file = ".env.production"
elif env_label in {"dev", "development", "local"}:
    env_file = ".env.development"

if env_file:
    root_dir = Path(__file__).resolve().parent.parent.parent
    _load_env_file(root_dir / env_file)

from .base import *
