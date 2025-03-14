import zlib
import base64
from cryptography.fernet import Fernet

class PresentationLayer:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encapsulate(self, data: str) -> bytes:
        compressed = zlib.compress(data.encode('utf-8'))
        print(f"[PresentationLayer] Compressed data: {compressed}")

        encrypted = self.cipher.encrypt(compressed)
        print(f"[PresentationLayer] Encrypted data: {encrypted}")

        encoded = base64.b64encode(encrypted)
        print(f"[PresentationLayer] Encoded data: {encoded}")

        return encoded

    def decapsulate(self, data: bytes) -> str:
        decoded = base64.b64decode(data)
        print(f"[PresentationLayer] Decoded data: {decoded}")

        decrypted = self.cipher.decrypt(decoded)
        print(f"[PresentationLayer] Decrypted data: {decrypted}")

        decompressed = zlib.decompress(decrypted)
        print(f"[PresentationLayer] Decompressed data: {decompressed}")

        return decompressed.decode('utf-8')