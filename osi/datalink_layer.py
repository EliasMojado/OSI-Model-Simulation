import uuid

def get_mac_address() -> str:
    """
    Retrieve the real MAC address of the machine as a hex string.
    """
    mac = ':'.join('{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                   for elements in range(0, 48, 8)[::-1])
    return mac

class DataLinkLayer:
    def __init__(self):
        self.mac = get_mac_address()
        print(f"[DataLinkLayer] Using real MAC address: {self.mac}")

    def get_mac(self) -> str:
        return self.mac

    def encapsulate(self, data: bytes) -> bytes:
        """
        Simulate data link layer encapsulation by adding a header and trailer
        containing the real MAC address.
        """
        header = f"DL_HEADER({self.mac})|".encode('utf-8')
        trailer = "|DL_TRAILER".encode('utf-8')
        framed = header + data + trailer
        print(f"[DataLinkLayer] Framed data: {framed}")
        return framed
    
    def decapsulate(self, data: bytes) -> bytes:
        decoded = data.decode('utf-8')
        # Remove the header and trailer if present.
        if decoded.startswith("DL_HEADER(") and "|DL_TRAILER" in decoded:
            header_end = decoded.find("|")
            trailer_start = decoded.rfind("|DL_TRAILER")
            inner = decoded[header_end+1:trailer_start]
            return inner.encode('utf-8')
        return data
