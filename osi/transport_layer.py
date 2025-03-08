import socket
import json
from typing import Tuple

class TransportLayer:
    def __init__(self):
        # Registry mapping destination port numbers to connection objects.
        self.port_registry = {}

    def register(self, port: int, conn: socket.socket):
        """Register a client connection for a given port."""
        self.port_registry[port] = conn
        print(f"[TransportLayer] Registered connection on port {port}")

    def deregister(self, port: int):
        """Remove a client connection from the registry."""
        if port in self.port_registry:
            del self.port_registry[port]
            print(f"[TransportLayer] Deregistered connection on port {port}")

    def send_via_registered(self, dest_port: int, message_obj: object) -> bool:
        """
        Attempt to send a message via a registered connection.
        Returns True if successful, False otherwise.
        """
        if dest_port in self.port_registry:
            conn = self.port_registry[dest_port]
            try:
                message_str = json.dumps(message_obj)
                conn.sendall(message_str.encode('utf-8'))
                print(f"[TransportLayer] Message routed to registered connection on port {dest_port}.")
                return True
            except Exception as e:
                print(f"[TransportLayer] Error sending message on port {dest_port}: {e}")
        else:
            print(f"[TransportLayer] No registered connection for port {dest_port}.")
        return False
    
    def encapsulate(self, data: bytes, dest_port: int) -> bytes:
        """
        Encapsulate the data with a transport header that includes the destination port.
        This header is prepended to the given bytes data.
        """
        header = f"TRANS_HEADER:{dest_port}|".encode('utf-8')
        encapsulated_data = header + data
        print(f"[TransportLayer] Encapsulated data: {encapsulated_data}")
        return encapsulated_data
    
    def decapsulate(self, data: bytes) -> Tuple[bytes, int]:
        """
        Decapsulate the transport header from the data.
        Returns a tuple of the inner data and the destination port.
        """
        decoded = data.decode('utf-8')
        if decoded.startswith("TRANS_HEADER:") and "|" in decoded:
            # Expected format: "TRANS_HEADER:{dest_port}|{inner_data}"
            header_part, inner_part = decoded.split('|', 1)
            try:
                dest_port = int(header_part.split(':')[1])
            except Exception as e:
                print(f"[TransportLayer] Error parsing transport header port: {e}")
                dest_port = None
            print(f"[TransportLayer] Decapsulated data: {inner_part}")
            return inner_part.encode('utf-8'), dest_port
        return data, None

