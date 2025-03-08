class PresentationLayer:
    def encapsulate(self, data: str) -> bytes:
        encoded = data.encode('utf-8')
        print(f"[PresentationLayer] Encoded data: {encoded}")
        return encoded

    def decapsulate(self, data: bytes) -> str:
        decoded = data.decode('utf-8')
        print(f"[PresentationLayer] Decoded data: {decoded}")
        return decoded
