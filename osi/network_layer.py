from typing import Tuple

class NetworkLayer:
    def __init__(self, src_ip: str):
        """
        Initialize the NetworkLayer with a source IP address.
        """
        self.src_ip = src_ip

    def encapsulate(self, data: bytes, dest_ip: str) -> bytes:
        """
        Encapsulate the data (from the transport layer) with a network (IP) header.
        The header includes the source and destination IP addresses.
        Format: "IP_HEADER:<src_ip>,<dest_ip>|" followed by the transport segment.
        """
        header_str = f"IP_HEADER:{self.src_ip},{dest_ip}|"
        header_bytes = header_str.encode('utf-8')
        encapsulated_data = header_bytes + data
        print(f"[NetworkLayer] Encapsulated data: {encapsulated_data}")
        return encapsulated_data

    def decapsulate(self, data: bytes) -> Tuple[bytes, str]:
        """
        Decapsulate the network (IP) header from the data.
        Verify that the destination IP in the header matches our own IP (self.src_ip).
        Returns a tuple: (inner_data as bytes, sender_ip as str).
        """
        decoded = data.decode('utf-8')
        if decoded.startswith("IP_HEADER:") and "|" in decoded:
            header_end = decoded.find("|")
            # Remove the "IP_HEADER:" prefix.
            header = decoded[len("IP_HEADER:"):header_end]
            # The header should be in the format "<sender_ip>,<dest_ip>"
            parts = header.split(",")
            if len(parts) != 2:
                raise Exception("Invalid IP header format.")
            sender_ip, dest_ip = parts
            # Verify that the destination IP matches our own.
            if dest_ip != self.src_ip:
                raise Exception(f"Packet not addressed to us: expected {self.src_ip}, got {dest_ip}")
            inner = decoded[header_end+1:]
            return inner.encode('utf-8'), sender_ip
        return data, None
