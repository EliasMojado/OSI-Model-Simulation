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
    
    def decapsulate(self, data: bytes) -> bytes:
        decoded = data.decode('utf-8')
        if decoded.startswith("IP_HEADER:") and "|" in decoded:
            header_end = decoded.find("|")
            inner = decoded[header_end+1:]
            return inner.encode('utf-8')
        return data
