import time
from pathlib import Path
from typing import List
from PyQt6.QtCore import QThread, pyqtSignal
from src.core.compressor import ZstdEngine

class CompressionWorker(QThread):
    # porcentaje, velocidad MB/s, transcurrido(s), restante(s), clave_de_fase_i18n
    progress_changed = pyqtSignal(int, float, int, int, str)
    operation_finished = pyqtSignal(float, int)  # tiempo_total, elementos_afectados
    error_occurred = pyqtSignal(str)

    def __init__(
        self, 
        mode: str, 
        sources: List[Path], 
        dest: Path, 
        level: int = 3, 
        split_mb: int = 0, 
        password: str = "",
        format_type: str = "zip",
        current_password: str = ""
    ):
        super().__init__()
        self.mode = mode
        self.sources = sources
        self.dest = dest
        self.level = level
        self.split_mb = split_mb
        self.password = password
        self.format_type = format_type
        self.current_password = current_password
        self._is_cancelled = False
        self._start_time = 0.0
        self._last_time = 0.0
        self._last_bytes = 0
        self._current_stage = ""

    def run(self):
        self._start_time = time.time()
        self._last_time = self._start_time
        self._last_bytes = 0
        affected_count = 0

        try:
            if self.mode == "compress":
                ZstdEngine.compress(
                    items=self.sources,
                    dest_archive=self.dest,
                    level=self.level,
                    split_size_mb=self.split_mb,
                    password=self.password,
                    format_type=self.format_type,
                    progress_cb=self._on_progress,
                    is_cancelled=lambda: self._is_cancelled
                )
            elif self.mode == "decompress":
                ZstdEngine.decompress(
                    archive_path=self.sources[0],
                    output_dir=self.dest,
                    password=self.password,
                    progress_cb=self._on_progress,
                    is_cancelled=lambda: self._is_cancelled
                )
            elif self.mode == "recrypt":
                affected_count = ZstdEngine.recrypt_archive(
                    archive_path=self.sources[0],
                    new_password=self.password,
                    current_password=self.current_password,
                    progress_cb=self._on_progress,
                    is_cancelled=lambda: self._is_cancelled
                )

            if not self._is_cancelled:
                self.operation_finished.emit(time.time() - self._start_time, affected_count)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _on_progress(self, current: int, total: int, stage_key: str = ""):
        now = time.time()
        elapsed = max(1, int(now - self._start_time))
        dt = now - self._last_time
        speed = 0.0

        if dt >= 0.2:
            speed = ((current - self._last_bytes) / (1024 * 1024)) / dt
            self._last_bytes = current
            self._last_time = now

        percentage = int((current / total) * 100) if total > 0 else 0
        bytes_left = max(0, total - current)
        bytes_per_sec = current / elapsed
        eta_seconds = int(bytes_left / bytes_per_sec) if bytes_per_sec > 0 else 0

        self.progress_changed.emit(min(100, percentage), max(0.0, speed), elapsed, eta_seconds, stage_key)