import socket
import threading
import json
from application_layer import ApplicationLayer
from datalink_layer import DataLinkLayer
from transport_layer import TransportLayer
from presentation_layer import PresentationLayer
from session_layer import SessionLayer

class OSIServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.app_layer = ApplicationLayer()
        self.presentation_layer = PresentationLayer()
        self.session_layer = SessionLayer(receiver_ip=None, port=port)
        self.transport_layer = TransportLayer()
        self.data_link_layer = DataLinkLayer()
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
        # Session handshake phase:
        try:
            # Receive an initial message from the client.
            initial_data = conn.recv(1024)
            if not initial_data:
                conn.close()
                return
            # First, try to let the Session Layer handle an incoming handshake.
            session_id = self.session_layer.handle_incoming_session(conn, initial_data)
            if session_id:
                print(f"[OSIServer] Session established via incoming handshake; session_id: {session_id}")
            else:
                # If the client did not initiate the handshake, let the server initiate one.
                session_id = self.session_layer.initiate_session(conn)
                if session_id:
                    print(f"[OSIServer] Session initiated with client; session_id: {session_id}")
                else:
                    print("[OSIServer] Session handshake failed; closing connection.")
                    conn.close()
                    return
        except Exception as e:
            print(f"[OSIServer] Error during session handshake with {addr}: {e}")
            conn.close()
            return

        # Now that the session is established, process further messages.
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
        
        # Simulate processing at the upper layers (Network/Transport/Session Layers).
        print("[Network/Transport/Session Layers] Processing data...")
        
        # Use Presentation Layer to decode raw bytes into a string.
        decoded_str = self.presentation_layer.decode(raw_data)
        
        # Convert the JSON string into a message object.
        try:
            message_obj = json.loads(decoded_str)
        except Exception as e:
            print("Error decoding JSON message:", e)
            return

        # If the message is intended for forwarding (contains destination info), route it.
        if "destination" in message_obj:
            destination_ip = message_obj.pop("destination")
            dest_port = message_obj.pop("dest_port", self.port)
            print(f"[OSIServer] Received send command for destination {destination_ip}:{dest_port}")
            self.send_message(destination_ip, dest_port, message_obj)
        else:
            # Otherwise, pass it to the Application Layer for processing.
            self.app_layer.process_message(message_obj)

    def send_message(self, ip_address: str, dest_port: int, message_obj: object):
        # Pipeline for sending a message:
        # 1. Application Layer encapsulation: convert the message object to a JSON string.
        app_encapsulated = self.app_layer.encapsulate(message_obj)
        # 2. Presentation Layer encapsulation: encode the string to bytes.
        pres_encapsulated = self.presentation_layer.encapsulate(app_encapsulated)
        # 3. Session Layer encapsulation: attach the session header (operates on bytes).
        session_encapsulated = self.session_layer.encapsulate(pres_encapsulated)
        raw_data = session_encapsulated
        print("[PhysicalLayer] Final raw data to send:", raw_data)

        # Open a new socket connection to the destination and send the data.
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_address, dest_port))
                s.sendall(raw_data)
                print(f"[OSIServer] Message sent to {ip_address}:{dest_port} through OSI layers.")
        except Exception as e:
            print(f"[OSIServer] Error sending message to {ip_address}:{dest_port}: {e}")

if __name__ == "__main__":
    server = OSIServer()
    server.start()
