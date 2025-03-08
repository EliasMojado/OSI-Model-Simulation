import uuid
import socket

class SessionLayer:
    def __init__(self, receiver_ip: str = None, port: int = 5000):
        self.receiver_ip = receiver_ip
        self.port = port
        self.session_id = None

    def establish_session(self) -> bool:
        self.session_id = str(uuid.uuid4())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.receiver_ip, self.port))
                sock.sendall(self.session_id.encode('utf-8'))
                print(f"[SessionLayer] Sent session id: {self.session_id}")
                ack = sock.recv(1024).decode('utf-8')
                if ack == "ACK":
                    print("[SessionLayer] Session established successfully.")
                    return True
                else:
                    print(f"[SessionLayer] Unexpected response: {ack}")
                    return False
            except Exception as e:
                print(f"[SessionLayer] Error establishing session: {e}")
                return False

    def handle_incoming_session(self, conn: socket.socket, initial_data: bytes) -> str:
        try:
            self.session_id = initial_data.decode('utf-8')
            conn.sendall("ACK".encode('utf-8'))
            print(f"[SessionLayer] Received session id: {self.session_id}. Sent ACK.")
            return self.session_id
        except Exception as e:
            print(f"[SessionLayer] Error during incoming session handshake: {e}")
            return None

    def initiate_session(self, conn: socket.socket) -> str:
        try:
            self.session_id = str(uuid.uuid4())
            conn.sendall(self.session_id.encode('utf-8'))
            print(f"[SessionLayer] Sent session id: {self.session_id} to client for handshake initiation.")
            ack = conn.recv(1024).decode('utf-8')
            if ack == "ACK":
                print("[SessionLayer] Session initiated successfully.")
                return self.session_id
            else:
                print(f"[SessionLayer] Unexpected ACK response: {ack}")
                return None
        except Exception as e:
            print(f"[SessionLayer] Error initiating session: {e}")
            return None

    def encapsulate(self, data: bytes, receiver_ip: str = None) -> bytes:
        if not self.session_id:
            if receiver_ip is not None:
                self.receiver_ip = receiver_ip
            print("[SessionLayer] No active session. Establishing session now...")
            if not self.establish_session():
                raise Exception("Failed to establish session with the receiver.")
        header = f"SESSION_ID:{self.session_id}|".encode('utf-8')
        encapsulated_data = header + data
        print(f"[SessionLayer] Encapsulated data: {encapsulated_data}")
        return encapsulated_data

    def decapsulate(self, data: bytes) -> bytes:
        decoded = data.decode('utf-8')
        if decoded.startswith("SESSION_ID:") and "|" in decoded:
            header_end = decoded.find("|")
            inner = decoded[header_end+1:]
            return inner.encode('utf-8')
        return data
