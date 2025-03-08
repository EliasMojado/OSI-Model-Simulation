import uuid
import socket

class SessionLayer:
    def __init__(self, port: int = 5000):
        self.port = port
        # A dictionary mapping sender (or connection) identifiers to session ids.
        self.sessions = {}  # { sender_ip: session_id }

    def establish_session(self, receiver_ip: str) -> bool:
        """Client-side: Initiate a session with the receiver."""
        session_id = str(uuid.uuid4())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((receiver_ip, self.port))
                sock.sendall(session_id.encode('utf-8'))
                print(f"[SessionLayer] Sent session id: {session_id} to {receiver_ip}")
                ack = sock.recv(1024).decode('utf-8')
                if ack == "ACK":
                    print("[SessionLayer] Session established successfully.")
                    # Store session using receiver_ip as key
                    self.sessions[receiver_ip] = session_id
                    return True
                else:
                    print(f"[SessionLayer] Unexpected response: {ack}")
                    return False
            except Exception as e:
                print(f"[SessionLayer] Error establishing session: {e}")
                return False

    def handle_incoming_session(self, conn: socket.socket, sender_ip: str, initial_data: bytes) -> str:
        """Server-side: Handle an incoming handshake initiated by a client."""
        try:
            session_id = initial_data.decode('utf-8')
            conn.sendall("ACK".encode('utf-8'))
            print(f"[SessionLayer] Received session id: {session_id} from {sender_ip}. Sent ACK.")
            # Store the session id keyed by the sender's IP
            self.sessions[sender_ip] = session_id
            return session_id
        except Exception as e:
            print(f"[SessionLayer] Error during incoming session handshake: {e}")
            return None

    def encapsulate(self, data: bytes, receiver_ip: str) -> bytes:
        """Encapsulate data with the session header for the session established with receiver_ip."""
        if receiver_ip not in self.sessions:
            print("[SessionLayer] No active session for receiver. Establishing session now...")
            if not self.establish_session(receiver_ip):
                raise Exception("Failed to establish session with the receiver.")
        header = f"SESSION_ID:{self.sessions[receiver_ip]}|".encode('utf-8')
        encapsulated_data = header + data
        print(f"[SessionLayer] Encapsulated data: {encapsulated_data}")
        return encapsulated_data

    def decapsulate(self, data: bytes, sender_ip: str) -> bytes:
        """
        Decapsulate the session header. Validate that the session id matches the stored session for sender_ip.
        """
        decoded = data.decode('utf-8')
        if decoded.startswith("SESSION_ID:") and "|" in decoded:
            header_end = decoded.find("|")
            header = decoded[:header_end]
            inner = decoded[header_end+1:]
            received_session_id = header.split("SESSION_ID:")[1]
            expected_session_id = self.sessions.get(sender_ip)
            if expected_session_id is None:
                raise Exception("No active session for sender; cannot validate incoming session id.")
            if expected_session_id != received_session_id:
                raise Exception(f"Session ID mismatch: expected {expected_session_id}, got {received_session_id}")
            else:
                print(f"[SessionLayer] Session ID validated: {received_session_id}")
                print(f"[SessionLayer] Decapsulated data: {inner}")
            return inner.encode('utf-8')
        return data
