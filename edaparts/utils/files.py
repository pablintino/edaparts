import hashlib
import os
import pathlib
import shutil
import tempfile
import uuid
from typing import BinaryIO


class TempCopiedFile:

    def __init__(self, binary_io: BinaryIO):
        temp_dir = tempfile.gettempdir()
        self.path = pathlib.Path(os.path.join(temp_dir, uuid.uuid4().hex))
        with open(self.path, "wb") as f_dest:
            shutil.copyfileobj(binary_io, f_dest)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.path.unlink(missing_ok=True)


def hash_sha256(path: str | pathlib.Path) -> str:
    with open(path, "rb", buffering=0) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()
