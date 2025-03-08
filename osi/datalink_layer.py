import uuid
import socket
import threading

ARP_PORT = 12345

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
        self.arp_table = {}  # Maps IP addresses to MAC addresses.
        # Start the ARP responder in a background thread.
        threading.Thread(target=self.arp_listener, daemon=True).start()

    def arp_listener(self):
        """
        Listen for ARP requests on ARP_PORT and respond with our MAC address.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', ARP_PORT))
        print(f"[DataLinkLayer] ARP listener running on port {ARP_PORT} ", end="\n")
        while True:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8').strip()
            if message == "ARP_REQUEST":
                response = f"ARP_RESPONSE:{self.mac}"
                sock.sendto(response.encode('utf-8'), addr)
                print(f"[DataLinkLayer] Responded to ARP request from {addr} with MAC {self.mac} ", end="\n")

    def request_mac(self, receiver_ip: str) -> str:
        """
        Request the MAC address of the receiver via ARP.
        """
        if receiver_ip in self.arp_table:
            print(f"[DataLinkLayer] Using cached MAC {self.arp_table[receiver_ip]} for IP {receiver_ip}")
            return self.arp_table[receiver_ip]
        try:
            print(f"[DataLinkLayer] Sending ARP request to {receiver_ip}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto("ARP_REQUEST".encode('utf-8'), (receiver_ip, ARP_PORT))
            data, _ = sock.recvfrom(1024)
            response = data.decode('utf-8').strip()
            if response.startswith("ARP_RESPONSE:"):
                remote_mac = response.split("ARP_RESPONSE:")[1]
                self.arp_table[receiver_ip] = remote_mac
                print(f"[DataLinkLayer] Learned MAC {remote_mac} for IP {receiver_ip}")
                return remote_mac
        except Exception as e:
            print(f"[DataLinkLayer] Error requesting MAC from {receiver_ip}: {e}")
        return None

    def encapsulate(self, data: bytes, receiver_ip: str) -> bytes:
        """
        Simulate Data Link Layer encapsulation by adding a header and trailer.
        The header contains the receiver's MAC address obtained via ARP.
        """
        remote_mac = self.request_mac(receiver_ip)
        if remote_mac is None:
            raise Exception(f"Failed to resolve MAC for {receiver_ip}")
        header = f"DL_HEADER({remote_mac})|".encode('utf-8')
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
            # Extract the MAC address from the header, subtracting 1 to remove the closing ')'
            header = decoded[10:header_end-1]
            if header == self.mac:
                print(f"[DataLinkLayer] MAC address matched: {header}")
                inner = decoded[header_end+1:trailer_start]
                print(f"[DataLinkLayer] Decapsulated data: {inner}")
                return inner.encode('utf-8')
            else:
                raise Exception(f"MAC address mismatch: expected {self.mac}, got {header}")
        return data

