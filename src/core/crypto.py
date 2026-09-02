import os
from pathlib import Path
from typing import Callable, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_SIZE = 16
NONCE_SIZE = 12
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB

class CryptoEngine:
    """Implementación de cifrado autenticado AES-256-GCM con PBKDF2."""

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return kdf.derive(password.encode("utf-8"))

    @classmethod
    def encrypt_file(
        cls, 
        input_path: Path, 
        output_path: Path, 
        password: str,
        progress_cb: Optional[Callable[[int, int], None]] = None
    ) -> None:
        salt = os.urandom(SALT_SIZE)
        key = cls.derive_key(password, salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(NONCE_SIZE)

        total_size = input_path.stat().st_size
        processed = 0

        with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
            # Header: Encabezado mágico + salt + nonce
            fout.write(b"CLZIP_ENC")
            fout.write(salt)
            fout.write(nonce)

            data = fin.read()
            encrypted_data = aesgcm.encrypt(nonce, data, None)
            fout.write(encrypted_data)
            
            if progress_cb:
                progress_cb(total_size, total_size)

    @classmethod
    def decrypt_file(
        cls, 
        input_path: Path, 
        output_path: Path, 
        password: str,
        progress_cb: Optional[Callable[[int, int], None]] = None
    ) -> None:
        with open(input_path, "rb") as fin:
            magic = fin.read(9)
            if magic != b"CLZIP_ENC":
                raise ValueError("Formato cifrado inválido o archivo no cifrado por clzip.")
            salt = fin.read(SALT_SIZE)
            nonce = fin.read(NONCE_SIZE)
            ciphertext = fin.read()

        key = cls.derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        try:
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError("Contraseña incorrecta o datos manipulados.") from e

        with open(output_path, "wb") as fout:
            fout.write(decrypted_data)

        if progress_cb:
            progress_cb(len(decrypted_data), len(decrypted_data))