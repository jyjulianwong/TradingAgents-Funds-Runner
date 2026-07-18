from abc import ABC, abstractmethod
from pathlib import Path


class BaseUploader(ABC):
    """Upload a local file to a remote storage location."""

    @abstractmethod
    def upload(self, local_path: Path, remote_key: str) -> str:
        """Upload *local_path* at *remote_key* and return a public URL or identifier."""
