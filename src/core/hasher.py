import hashlib
import zlib
from pathlib import Path
from typing import Dict, Callable, Optional

class ChecksumEngine:
    """Calculador multi-algoritmo de sumas de verificación."""

    @staticmethod
    def calculate_hashes(
        file_path: Path, 
        progress_cb: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, str]:
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        crc = 0

        total_bytes = file_path.stat().st_size
        read_bytes = 0

        with open(file_path, "rb") as f:
            while chunk := f.read(4 * 1024 * 1024):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)
                crc = zlib.crc32(chunk, crc)
                read_bytes += len(chunk)
                if progress_cb:
                    progress_cb(read_bytes, total_bytes)

        return {
            "CRC32": f"{crc & 0xFFFFFFFF:08X}",
            "MD5": md5.hexdigest().upper(),
            "SHA-1": sha1.hexdigest().upper(),
            "SHA-256": sha256.hexdigest().upper(),
        }