"""Environment variable loader for envcast.

Supports loading .env files and system environment variables
for diffing and syncing across deployment targets.
"""

import os
from pathlib import Path
from typing import Dict, Optional


class EnvLoader:
    """Loads environment variables from various sources."""

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath
        self._env: Dict[str, str] = {}

    def load_file(self, filepath: Optional[str] = None) -> Dict[str, str]:
        """Load environment variables from a .env file."""
        path = Path(filepath or self.filepath)

        if not path.exists():
            raise FileNotFoundError(f"Env file not found: {path}")

        env = {}
        with path.open("r") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(
                        f"Invalid format on line {line_number}: '{line}'"
                    )
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if not key:
                    raise ValueError(
                        f"Empty key on line {line_number}"
                    )
                env[key] = value

        self._env = env
        return env

    def load_system(self, prefix: Optional[str] = None) -> Dict[str, str]:
        """Load environment variables from the current system environment."""
        env = dict(os.environ)
        if prefix:
            env = {k: v for k, v in env.items() if k.startswith(prefix)}
        self._env = env
        return env

    @property
    def env(self) -> Dict[str, str]:
        """Return the currently loaded environment variables."""
        return dict(self._env)
