import socket
import threading
import json
from application_layer import ApplicationLayer
from datalink_layer import DataLinkLayer
from presentation_layer import PresentationLayer
from session_layer import SessionLayer
from transport_layer import TransportLayer
from network_layer import NetworkLayer
from physical_layer import PhysicalLayer

def get_own_ip():
    """
    Determine the server's own IP address by creating a dummy connection.
    """
    try:
        # Connecting to an external host to get the proper IP address.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    return ip

class OSIServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.ip = get_own_ip()
        self.app_layer = ApplicationLayer()
        self.presentation_layer = PresentationLayer()
        self.session_layer = SessionLayer(port=port)
        self.transport_layer = TransportLayer()
        self.network_layer = NetworkLayer(src_ip=self.ip)
        self.data_link_layer = DataLinkLayer()
        self.physical_layer = PhysicalLayer()
        self.server_socket = None
        self.registered_clients = {}

    def start(self):
        print("OSI: [start]")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn: socket.socket, addr):
        print("OSI: [handle_client]")
        # Receive initial data
        initial_data = conn.recv(1024)
        if not initial_data:
            conn.close()
            return
        try:
            decoded = initial_data.decode('utf-8').strip()
        except Exception:
            conn.close()
            return

        # If data starts with '{', assume it's a registration message
        if decoded.startswith('{'):
            try:
                reg_msg = json.loads(decoded)
            except Exception:
                conn.close()
                return

            if reg_msg.get("type") != "register":
                conn.close()
                return

            listening_port = reg_msg.get("port")
            self.registered_clients[addr[0]] = {"conn": conn, "listening_port": listening_port}
            conn.sendall("ACK".encode('utf-8'))
        elif decoded.startswith("DL_HEADER("):
            # This is a fully encapsulated message coming from another OSI server.
            self.process_received_data(initial_data, conn)
        else:
            # Otherwise, treat it as a session handshake request.
            sender_ip = addr[0]
            self.session_layer.handle_incoming_session(conn, sender_ip, initial_data)
            conn.close()
            return

        # Now process further incoming messages on this registration connection.
        while True:
            data = conn.recv(1024)
            if not data:
                break
            self.process_received_data(data, conn)
        conn.close()
        self.registered_clients.pop(addr[0], None)

    def process_received_data(self, raw_data: bytes, conn: socket.socket):
        print("OSI: [process_received_data]")
        try:
            decoded_str = raw_data.decode('utf-8')
        except Exception as e:
            print(f"OSI: [decode error] {e}")
            return

        # If the raw data starts with the Data Link header, assume it is fully encapsulated.
        if decoded_str.startswith("DL_HEADER("):
            print("OSI: [process_received_data] - Starting decapsulation chain")
            # Step 1: Data Link Layer decapsulation.
            data = self.data_link_layer.decapsulate(raw_data)

            # Step 2: Network Layer decapsulation.
            data, sender_ip = self.network_layer.decapsulate(data)

            # Step 3: Transport Layer decapsulation.
            data, extracted_port = self.transport_layer.decapsulate(data)
            
            # Step 4: Session Layer decapsulation.
            data = self.session_layer.decapsulate(data, sender_ip)

            # Step 5: Presentation Layer decapsulation.
            data = self.presentation_layer.decapsulate(data)

            # Step 6: Application Layer decapsulation.
            data = self.app_layer.decapsulate(data)

            try:
                message_obj = json.loads(data)
            except Exception as e:
                print(f"OSI: [JSON decode error] {e}")
                return

            self.app_layer.process_message(message_obj, extracted_port)
        else:
            # Otherwise, assume data is already decapsulated (e.g., from a direct chat app message).
            try:
                message_obj = json.loads(decoded_str)
            except Exception as e:
                print(f"OSI: [JSON decode error] {e}")
                return

            if "destination" in message_obj:
                print("OSI: [sending message]")
                destination_ip = message_obj.pop("destination")
                dest_port = message_obj.pop("dest_port", self.port)
                self.send_message(destination_ip, dest_port, message_obj)
            else:
                print("OSI: [received message] - Delivering to chat app")
                print("     ", message_obj)
                self.app_layer.process_message(message_obj)


    def send_message(self, ip_address: str, dest_port: int, message_obj: object):
        print("OSI: [send message] - Start sending message")
        
        # Step 1: Application Layer encapsulation
        app_encapsulated = self.app_layer.encapsulate(message_obj)
        
        # Step 2: Presentation Layer encoding
        pres_encapsulated = self.presentation_layer.encapsulate(app_encapsulated)
        
        # Step 3: Session Layer encapsulation (establish session if needed)
        session_encapsulated = self.session_layer.encapsulate(pres_encapsulated, receiver_ip=ip_address)

        # Step 4: Transport Layer encapsulation, encapsulate it with the transport header
        transport_encapsulated = self.transport_layer.encapsulate(session_encapsulated, dest_port)

        # Step 5: Network Layer encapsulation, encapsulate it with the network header
        network_encapsulated = self.network_layer.encapsulate(transport_encapsulated, ip_address)

        # Step 6: Data Link Layer encapsulation, encapsulate it with the data link header
        data_link_encapsulated = self.data_link_layer.encapsulate(network_encapsulated, receiver_ip=ip_address)

        # Step 7: Physical Layer, send the data
        self.physical_layer.transmit(data_link_encapsulated, ip_address, self.port)        


if __name__ == "__main__":
    server = OSIServer()
    server.start()
