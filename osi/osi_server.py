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
        print(f"[SERVER START] OSI Server is running on port {self.port}")
        try:
            while True:
                conn, addr = self.server_socket.accept()
                print(f"\n[NEW CONNECTION] Accepted connection from {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("[SERVER SHUTDOWN] Shutting down OSI Server.")
        finally:
            self.server_socket.close()

    def handle_client(self, conn: socket.socket, addr):
        print(f"[CONNECTION] Handling client {addr}")
        # Session handshake phase:
        try:
            # Receive an initial message from the client.
            initial_data = conn.recv(1024)
            if not initial_data:
                print(f"[HANDSHAKE] No data received from {addr}. Closing connection.")
                conn.close()
                return
            # Attempt to let the Session Layer handle an incoming handshake.
            session_id = self.session_layer.handle_incoming_session(conn, initial_data)
            if session_id:
                print(f"[HANDSHAKE][RECV] Session established via incoming handshake; session_id: {session_id}")
            else:
                # If the client did not initiate the handshake, let the server initiate one.
                session_id = self.session_layer.initiate_session(conn)
                if session_id:
                    print(f"[HANDSHAKE][SEND] Session initiated with client; session_id: {session_id}")
                else:
                    print(f"[HANDSHAKE][FAIL] Session handshake failed with {addr}; closing connection.")
                    conn.close()
                    return
        except Exception as e:
            print(f"[HANDSHAKE][ERROR] Error during session handshake with {addr}: {e}")
            conn.close()
            return

        # Now that the session is established, process further messages.
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f"[CONNECTION] No more data from {addr}.")
                    break
                print(f"[RECV][PHYSICAL] Received raw data: {data}")
                self.process_received_data(data, conn)
        except Exception as e:
            print(f"[CONNECTION][ERROR] Error handling client {addr}: {e}")
        finally:
            conn.close()
            print(f"[CONNECTION] Connection closed with {addr}")

    def process_received_data(self, raw_data: bytes, conn: socket.socket):
        # Data Link Layer decapsulation.
        virtual_mac = self.data_link_layer.get_virtual_mac()
        print(f"[DATALINK][DECAPSULATION] Using virtual MAC: {virtual_mac}")
        
        print("[NETWORK/TRANSPORT/SESSION] Processing data...")
        
        # Presentation Layer decodes raw bytes into a string.
        decoded_str = self.presentation_layer.decode(raw_data)
        print(f"[PRESENTATION][DECODE] Decoded string: {decoded_str}")
        
        # Convert the JSON string into a message object.
        try:
            message_obj = json.loads(decoded_str)
        except Exception as e:
            print(f"[APPLICATION][ERROR] Error decoding JSON message: {e}")
            return

        # Check if the message is meant for routing.
        if "destination" in message_obj:
            destination_ip = message_obj.pop("destination")
            dest_port = message_obj.pop("dest_port", self.port)
            print(f"[ROUTING] Received command to send message to {destination_ip}:{dest_port}")
            self.send_message(destination_ip, dest_port, message_obj)
        else:
            print(f"[APPLICATION] Processing message locally: {message_obj}")
            self.app_layer.process_message(message_obj)

    def send_message(self, ip_address: str, dest_port: int, message_obj: object):
        print(f"[SEND][START] Preparing to send message to {ip_address}:{dest_port}")
        # 1. Application Layer encapsulation.
        app_encapsulated = self.app_layer.encapsulate(message_obj)
        print(f"[APPLICATION][ENCAPSULATE] {app_encapsulated}")
        # 2. Presentation Layer encapsulation.
        pres_encapsulated = self.presentation_layer.encapsulate(app_encapsulated)
        print(f"[PRESENTATION][ENCAPSULATE] {pres_encapsulated}")
        # 3. Session Layer encapsulation.
        session_encapsulated = self.session_layer.encapsulate(pres_encapsulated)
        print(f"[SESSION][ENCAPSULATE] {session_encapsulated}")
        raw_data = session_encapsulated
        print(f"[PHYSICAL][SEND] Final raw data to send: {raw_data}")

        # Open a new socket connection to the destination and send the data.
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_address, dest_port))
                s.sendall(raw_data)
                print(f"[SEND][SUCCESS] Message sent to {ip_address}:{dest_port}")
        except Exception as e:
            print(f"[SEND][ERROR] Error sending message to {ip_address}:{dest_port}: {e}")

if __name__ == "__main__":
    server = OSIServer()
    server.start()
