import socket
import json

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
