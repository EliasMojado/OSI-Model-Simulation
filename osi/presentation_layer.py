class PresentationLayer:
    def encode(self, data: str) -> bytes:
        """
        Encode the provided string data to bytes using UTF-8.
        """
        encoded = data.encode('utf-8')
        print(f"[PresentationLayer] Encoded data: {encoded}")
        return encoded

    def decode(self, data: bytes) -> str:
        """
        Decode the bytes data back into a string using UTF-8.
        """
        decoded = data.decode('utf-8')
        print(f"[PresentationLayer] Decoded data: {decoded}")
        return decoded

    def encapsulate(self, data: str) -> bytes:
        """
        In this simulation, the Presentation Layer’s encapsulation is the encoding step.
        """
        return self.encode(data)
