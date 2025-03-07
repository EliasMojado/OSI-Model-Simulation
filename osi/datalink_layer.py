import random
import os

VIRTUAL_MAC_FILE = "virtual_mac.txt"

def generate_virtual_mac() -> str:
    """
    Generate or retrieve a persistent virtual MAC address.
    """
    if os.path.exists(VIRTUAL_MAC_FILE):
        with open(VIRTUAL_MAC_FILE, "r") as file:
            mac_address = file.read().strip()
            if mac_address:
                print(f"[DataLinkLayer] Loaded persistent virtual MAC from file: {mac_address}")
                return mac_address

    mac_bytes = [random.randint(0, 255) for _ in range(6)]
    mac_address = ':'.join(f'{byte:02x}' for byte in mac_bytes)
    with open(VIRTUAL_MAC_FILE, "w") as file:
        file.write(mac_address)
    print(f"[DataLinkLayer] Generated new virtual MAC: {mac_address}")
    return mac_address

class DataLinkLayer:
    def __init__(self):
        self.virtual_mac = generate_virtual_mac()

    def get_virtual_mac(self) -> str:
        return self.virtual_mac

    def encapsulate(self, data: bytes) -> bytes:
        """
        Simulate data link layer encapsulation by adding a header and trailer containing the virtual MAC.
        """
        mac = self.get_virtual_mac()
        header = f"DL_HEADER({mac})|".encode('utf-8')
        trailer = "|DL_TRAILER".encode('utf-8')
        framed = header + data + trailer
        print(f"[DataLinkLayer] Framed data: {framed}")
        return framed
