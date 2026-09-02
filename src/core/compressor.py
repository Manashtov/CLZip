import os
import gc
import re
import glob
import shutil
import tempfile
import tarfile
import py7zr
import pyzipper
import zstandard as zstd
from pathlib import Path
from typing import Callable, Optional, List
from src.core.exceptions import CompressionError, DecompressionError

# Intentar importar rarfile de forma segura
try:
    import rarfile
except ImportError:
    rarfile = None

CHUNK_SIZE = 4 * 1024 * 1024

class ZstdEngine:
    @staticmethod
    def is_archive_encrypted(archive_path: Path) -> bool:
        archive_path = Path(archive_path)
        ext = archive_path.suffix.lower()

        if ext == ".zip":
            try:
                with pyzipper.AESZipFile(str(archive_path), "r") as zf:
                    for info in zf.infolist():
                        if info.flag_bits & 0x1:
                            return True
            except Exception:
                pass
        elif ext == ".7z":
            try:
                with py7zr.SevenZipFile(str(archive_path), mode="r") as sz:
                    return sz.needs_password()
            except Exception:
                return True
        elif ext == ".rar" and rarfile:
            try:
                with rarfile.RarFile(str(archive_path), mode="r") as rf:
                    return rf.needs_password()
            except Exception:
                return False
        return False

    @staticmethod
    def compress(
        items: List[Path],
        dest_archive: Path,
        level: int = 3,
        split_size_mb: int = 0,
        password: str = "",
        format_type: str = "zip",
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None
    ) -> None:
        dest_archive = Path(dest_archive)
        temp_dest = dest_archive.with_suffix(".tmp_archive")

        print(f"\n{'='*50}")
        print(f"[CRYPTO-LOG] >>> INICIANDO COMPRESIÓN <<<")
        print(f"[CRYPTO-LOG] Destino: {dest_archive.name}")
        print(f"[CRYPTO-LOG] Formato: {format_type}")
        print(f"[CRYPTO-LOG] Contraseña: {'SÍ (Longitud: ' + str(len(password)) + ')' if password else 'NO (Sin cifrado)'}")

        try:
            file_list: List[tuple[Path, str]] = []
            for item in items:
                item = Path(item)
                if item.is_file():
                    file_list.append((item, item.name))
                elif item.is_dir():
                    for root, _, files in os.walk(item):
                        for f in files:
                            full_p = Path(root) / f
                            arcname = str(full_p.relative_to(item.parent)).replace("\\", "/")
                            file_list.append((full_p, arcname))

            total_files = len(file_list)
            if total_files == 0:
                raise CompressionError("No hay archivos válidos para comprimir.")

            # 1. COMPRESIÓN ZIP
            if format_type == "zip":
                enc = pyzipper.WZ_AES if password else None
                total_bytes = sum(f[0].stat().st_size for f in file_list) or 1
                bytes_done = 0

                with pyzipper.AESZipFile(
                    str(temp_dest),
                    "w",
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=enc
                ) as zf:
                    if password:
                        pwd_bytes = password.encode("utf-8")
                        zf.setpassword(pwd_bytes)
                        zf.setencryption(pyzipper.WZ_AES, nbits=256)
                        print(f"[CRYPTO-LOG] ✓ Cifrado AES-256 habilitado en pyzipper.")

                    for fpath, arcname in file_list:
                        if is_cancelled and is_cancelled():
                            return

                        with open(fpath, "rb") as src, zf.open(arcname, "w") as dst:
                            while chunk := src.read(CHUNK_SIZE):
                                dst.write(chunk)
                                bytes_done += len(chunk)
                                if progress_cb:
                                    progress_cb(bytes_done, total_bytes, "status_zip_stage")

                with pyzipper.AESZipFile(str(temp_dest), "r") as zf_chk:
                    cifrados = sum(1 for i in zf_chk.infolist() if (i.flag_bits & 0x1))
                    print(f"[CRYPTO-LOG] Elementos en archivo: {len(zf_chk.infolist())} | Protegidos: {cifrados}")

            # 2. COMPRESIÓN ZSTANDARD
            else:
                temp_tar = dest_archive.parent / f"~{dest_archive.stem}_temp.tar"
                total_raw_bytes = sum(f[0].stat().st_size for f in file_list) or 1
                tar_bytes_written = 0

                print(f"[CRYPTO-LOG] Fase 1: Creando contenedor TAR...")
                with tarfile.open(temp_tar, "w") as tar:
                    for fpath, arcname in file_list:
                        if is_cancelled and is_cancelled():
                            if temp_tar.exists():
                                temp_tar.unlink(missing_ok=True)
                            return
                        tar.add(str(fpath), arcname=arcname)
                        tar_bytes_written += fpath.stat().st_size
                        if progress_cb:
                            progress_cb(tar_bytes_written, total_raw_bytes * 2, "status_tar_stage")

                tar_size = temp_tar.stat().st_size
                print(f"[CRYPTO-LOG] Fase 2: Comprimiendo con Zstandard (Nivel {level})...")

                z_read = 0
                cctx = zstd.ZstdCompressor(level=level, threads=-1)

                with open(temp_tar, "rb") as ifh, open(temp_dest, "wb") as ofh:
                    with cctx.stream_writer(ofh) as compressor:
                        while chunk := ifh.read(CHUNK_SIZE):
                            if is_cancelled and is_cancelled():
                                if temp_tar.exists():
                                    temp_tar.unlink(missing_ok=True)
                                return
                            compressor.write(chunk)
                            z_read += len(chunk)
                            if progress_cb:
                                current_total = total_raw_bytes + int((z_read / tar_size) * total_raw_bytes)
                                progress_cb(current_total, total_raw_bytes * 2, "status_zstd_stage")

                if temp_tar.exists():
                    temp_tar.unlink(missing_ok=True)

            if split_size_mb > 0:
                ZstdEngine._split_file(temp_dest, dest_archive, split_size_mb * 1024 * 1024)
                temp_dest.unlink(missing_ok=True)
            else:
                if dest_archive.exists():
                    dest_archive.unlink()
                temp_dest.rename(dest_archive)

            print(f"[CRYPTO-LOG] ✓ Archivo final creado: {dest_archive.name}")
            print(f"{'='*50}\n")

        except Exception as e:
            print(f"[CRYPTO-LOG] ❌ ERROR EN COMPRESIÓN: {e}")
            if temp_dest.exists():
                temp_dest.unlink(missing_ok=True)
            raise CompressionError(f"Error en compresión: {str(e)}") from e
        finally:
            gc.collect()

    @staticmethod
    def _split_file(src_file: Path, base_dest: Path, chunk_bytes: int):
        part_num = 1
        with open(src_file, "rb") as f_in:
            while True:
                part_path = base_dest.with_suffix(f".part{part_num:03d}")
                with open(part_path, "wb") as f_out:
                    written = 0
                    while written < chunk_bytes:
                        read_len = min(CHUNK_SIZE, chunk_bytes - written)
                        buffer = f_in.read(read_len)
                        if not buffer:
                            return
                        f_out.write(buffer)
                        written += len(buffer)
                part_num += 1

    @staticmethod
    def decompress(
        archive_path: Path,
        output_dir: Path,
        password: str = "",
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None
    ) -> None:
        archive_path = Path(archive_path)
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*50}")
        print(f"[CRYPTO-LOG] >>> INICIANDO DESCOMPRESIÓN <<<")
        print(f"[CRYPTO-LOG] Archivo: {archive_path.name}")
        print(f"[CRYPTO-LOG] Clave recibida: {'SÍ (Longitud: ' + str(len(password)) + ')' if password else 'NO (Sin clave)'}")

        unified_file = archive_path
        temp_joined = None
        if re.search(r'\.(part\d+|\d{3}|z\d{2})$', archive_path.name.lower()):
            temp_joined = output_dir / f"joined_{archive_path.stem}"
            ZstdEngine._join_parts(archive_path, temp_joined)
            unified_file = temp_joined

        try:
            name_lower = unified_file.name.lower()

            # EXTRAER ZIP
            if name_lower.endswith(".zip"):
                with pyzipper.AESZipFile(str(unified_file), "r") as zf:
                    pwd_bytes = password.encode("utf-8") if password else None
                    if pwd_bytes:
                        zf.setpassword(pwd_bytes)

                    infolist = zf.infolist()
                    encrypted_files = [info for info in infolist if (info.flag_bits & 0x1)]

                    if encrypted_files:
                        if not pwd_bytes:
                            raise DecompressionError("El archivo requiere una contraseña.")

                        try:
                            sample = encrypted_files[0]
                            with zf.open(sample, pwd=pwd_bytes) as test_fp:
                                test_fp.read(1024)
                            print("[CRYPTO-LOG] ✓ Clave correcta validada.")
                        except Exception as auth_err:
                            raise DecompressionError("Contraseña incorrecta.") from auth_err

                    total_bytes = sum(info.file_size for info in infolist) or 1
                    bytes_extracted = 0

                    for info in infolist:
                        if is_cancelled and is_cancelled():
                            return

                        target_path = output_dir / info.filename
                        if info.is_dir() or info.filename.endswith("/") or info.filename.endswith("\\"):
                            target_path.mkdir(parents=True, exist_ok=True)
                            continue

                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info, pwd=pwd_bytes) as source, open(target_path, "wb") as target:
                            while chunk := source.read(CHUNK_SIZE):
                                target.write(chunk)
                                bytes_extracted += len(chunk)
                                if progress_cb:
                                    progress_cb(bytes_extracted, total_bytes, "status_extract_stage")

            # EXTRAER 7Z
            elif name_lower.endswith(".7z"):
                with py7zr.SevenZipFile(str(unified_file), mode="r", password=password or None) as sz:
                    sz.extractall(path=str(output_dir))
                    if progress_cb:
                        progress_cb(100, 100, "status_extract_stage")

            # EXTRAER RAR
            elif name_lower.endswith(".rar"):
                if rarfile is None:
                    raise DecompressionError("El módulo 'rarfile' no está instalado. Ejecute: pip install rarfile")
                with rarfile.RarFile(str(unified_file), mode="r") as rf:
                    if password:
                        rf.setpassword(password)
                    rf.extractall(path=str(output_dir))
                    if progress_cb:
                        progress_cb(100, 100, "status_extract_stage")

            # EXTRAER TAR Y DERIVADOS (.tar, .tar.gz, .tgz, .tar.bz2, .tar.xz)
            elif any(name_lower.endswith(ext) for ext in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz", ".gz", ".bz2", ".xz"]):
                with tarfile.open(str(unified_file), "r:*") as tf:
                    tf.extractall(str(output_dir))
                    if progress_cb:
                        progress_cb(100, 100, "status_extract_stage")

            # EXTRAER ZSTANDARD (.zst, .tzst)
            elif name_lower.endswith((".zst", ".tzst")):
                temp_tar = output_dir / f"extracted_{unified_file.stem}.tar"
                total_bytes = unified_file.stat().st_size
                z_read = 0
                dctx = zstd.ZstdDecompressor()
                
                with open(unified_file, "rb") as ifh, open(temp_tar, "wb") as ofh:
                    with dctx.stream_writer(ofh) as decompressor:
                        while chunk := ifh.read(CHUNK_SIZE):
                            if is_cancelled and is_cancelled():
                                return
                            decompressor.write(chunk)
                            z_read += len(chunk)
                            if progress_cb:
                                progress_cb(z_read, total_bytes, "status_extract_stage")

                if tarfile.is_tarfile(temp_tar):
                    with tarfile.open(temp_tar, "r") as tf:
                        tf.extractall(output_dir)
                    temp_tar.unlink(missing_ok=True)
                else:
                    final_name = unified_file.name.replace(".zst", "").replace(".tzst", "")
                    temp_tar.rename(output_dir / final_name)

            else:
                raise DecompressionError(f"Formato no soportado: {archive_path.suffix}")

            print(f"[CRYPTO-LOG] ✓ Descompresión finalizada con éxito.")
            print(f"{'='*50}\n")

        except DecompressionError:
            raise
        except Exception as e:
            print(f"[CRYPTO-LOG] ❌ ERROR: {e}")
            raise DecompressionError(f"Error al descomprimir: {str(e)}") from e
        finally:
            if temp_joined and temp_joined.exists():
                temp_joined.unlink(missing_ok=True)
            gc.collect()

    @staticmethod
    def recrypt_archive(
        archive_path: Path,
        new_password: str,
        current_password: str = "",
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None
    ) -> int:
        archive_path = Path(archive_path)
        temp_dir = Path(tempfile.mkdtemp(prefix="clzip_recrypt_"))
        temp_out = archive_path.parent / f"~{archive_path.stem}_recrypt.tmp"

        print(f"\n{'='*50}")
        print(f"[CRYPTO-LOG] >>> RE-CIFRANDO ARCHIVO EXISTENTE <<<")
        print(f"[CRYPTO-LOG] Archivo origen: {archive_path.name}")

        try:
            def unwrap_cb(c, t, stage="status_recrypt_unpack"):
                if progress_cb:
                    progress_cb(int(c * 0.5), t, "status_recrypt_unpack")

            ZstdEngine.decompress(
                archive_path=archive_path,
                output_dir=temp_dir,
                password=current_password,
                progress_cb=unwrap_cb,
                is_cancelled=is_cancelled
            )

            if is_cancelled and is_cancelled():
                return 0

            items = list(temp_dir.iterdir())
            if not items:
                raise CompressionError("El archivo no contiene elementos para re-cifrar.")

            def wrap_cb(c, t, stage="status_recrypt_pack"):
                if progress_cb:
                    progress_cb(int(t * 0.5 + c * 0.5), t, "status_recrypt_pack")

            ZstdEngine.compress(
                items=items,
                dest_archive=temp_out,
                password=new_password,
                format_type="zip",
                progress_cb=wrap_cb,
                is_cancelled=is_cancelled
            )

            if is_cancelled and is_cancelled():
                if temp_out.exists():
                    temp_out.unlink(missing_ok=True)
                return 0

            protected_count = 0
            with pyzipper.AESZipFile(str(temp_out), "r") as zf_chk:
                protected_count = sum(1 for i in zf_chk.infolist() if (i.flag_bits & 0x1))

            gc.collect()
            os.replace(str(temp_out), str(archive_path))
            print(f"[CRYPTO-LOG] ✓ Archivo re-cifrado: {archive_path.name} ({protected_count} protegidos)")
            print(f"{'='*50}\n")
            return protected_count

        except Exception as e:
            if temp_out.exists():
                temp_out.unlink(missing_ok=True)
            print(f"[CRYPTO-LOG] ❌ ERROR EN RE-CIFRADO: {e}")
            raise CompressionError(f"Error al aplicar contraseña: {str(e)}") from e
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            gc.collect()

    @staticmethod
    def _join_parts(first_part: Path, dest_unified: Path):
        base_pattern = re.sub(r'\.(part\d+|\d{3}|z\d{2})$', '.*', str(first_part))
        parts = sorted(glob.glob(base_pattern))
        with open(dest_unified, "wb") as outfile:
            for part in parts:
                with open(part, "rb") as infile:
                    while chunk := infile.read(CHUNK_SIZE):
                        outfile.write(chunk)