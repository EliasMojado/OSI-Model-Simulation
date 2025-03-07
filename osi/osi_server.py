import socket
import threading
import json
from application_layer import ApplicationLayer
from datalink_layer import DataLinkLayer
from transport_layer import TransportLayer

class OSIServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.data_link_layer = DataLinkLayer()
        self.app_layer = ApplicationLayer()
        self.transport_layer = TransportLayer()
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"OSI Server is running on port {self.port}")
        try:
            while True:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Shutting down OSI Server.")
        finally:
            self.server_socket.close()

    def handle_client(self, conn: socket.socket, addr):
        print(f"OSI Server: Connection established with {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                self.process_received_data(data, conn)
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()
            print(f"OSI Server: Connection closed with {addr}")

    def process_received_data(self, raw_data: bytes, conn: socket.socket):
        # Simulate Physical Layer reception.
        print("[PhysicalLayer] Received raw data:", raw_data)
        
        # Simulate Data Link Layer decapsulation.
        virtual_mac = self.data_link_layer.get_virtual_mac()
        print(f"[DataLinkLayer] Decapsulating frame using virtual MAC: {virtual_mac}...")
        
        # Simulate processing at the upper layers.
        print("[Network/Transport/Session/Presentation Layers] Processing data...")
        
        # Decode the received data (assumed to be JSON-encoded).
        try:
            message_obj = json.loads(raw_data.decode('utf-8'))
        except Exception as e:
            print("Error decoding message:", e)
            return

        # Check if this is a registration message.
        if message_obj.get("type") == "register":
            reg_port = message_obj.get("port")
            if reg_port is not None:
                self.transport_layer.register(reg_port, conn)
            return

        # Check for destination information.
        if "destination" in message_obj:
            destination_ip = message_obj.pop("destination")
            # Use provided destination port, or default to the OSI server's port.
            dest_port = message_obj.pop("dest_port", self.port)
            print(f"[OSI Server] Received send command for destination {destination_ip}:{dest_port}")
            self.send_message(destination_ip, dest_port, message_obj)
        else:
            # Otherwise, deliver the message to this server's Application Layer.
            self.app_layer.process_message(message_obj)

    def send_message(self, ip_address: str, dest_port: int, message_obj: object):
        # Simulate encapsulation at the Application Layer.
        print("[ApplicationLayer] Preparing to send message:", message_obj)
        
        # Simulate encapsulation at the upper layers.
        print("[Presentation/Session/Transport/Network Layers] Encapsulating message...")
        
        # Simulate Data Link Layer encapsulation.
        virtual_mac = self.data_link_layer.get_virtual_mac()
        print(f"[DataLinkLayer] Encapsulating frame with virtual MAC: {virtual_mac}...")
        
        # Simulate Physical Layer conversion to raw bytes.
        try:
            message_str = json.dumps(message_obj)
        except Exception as e:
            print("Error encoding message:", e)
            return
        raw_data = message_str.encode('utf-8')
        print("[PhysicalLayer] Sending raw data:", raw_data)

        # Use the transport layer's port registry to send the message if possible.
        if not self.transport_layer.send_via_registered(dest_port, message_obj):
            # Fallback: Open a new socket connection to the destination.
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((ip_address, dest_port))
                    s.sendall(raw_data)
                    print(f"Message sent to {ip_address}:{dest_port} through OSI layers.")
            except Exception as e:
                print(f"Error sending message to {ip_address}:{dest_port}: {e}")

if __name__ == "__main__":
    server = OSIServer()
    server.start()
