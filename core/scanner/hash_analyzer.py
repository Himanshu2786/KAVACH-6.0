"""
KAVACH 6.0 Desktop - Hash & Size Analyzer.
Calculates SHA-256 and SHA-1 hashes using streaming chunked reads without loading large files into memory.
"""

import hashlib
import os
from typing import Tuple

CHUNK_SIZE = 64 * 1024 # 64 KB chunks

class HashAnalyzer:
    @staticmethod
    def calculate_sha256(file_path: str) -> str:
        """Calculates SHA-256 hash of a file safely."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return "UNREADABLE_HASH"

    @staticmethod
    def get_file_metadata(file_path: str) -> Tuple[int, str]:
        """Returns (file_size_in_bytes, sha256_hash)."""
        try:
            size = os.path.getsize(file_path)
        except Exception:
            size = 0
            
        sha = HashAnalyzer.calculate_sha256(file_path)
        return size, sha
