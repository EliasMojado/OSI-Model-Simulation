import socket
import uuid

class SessionLayer:
    def __init__(self, receiver_ip: str = None, port: int = 5000):
        """
        Initialize with the receiver's IP and port.
        The receiver_ip is only used for client-side session establishment.
        """
        self.receiver_ip = receiver_ip
        self.port = port
        self.session_id = None

    def establish_session(self) -> bool:
        """
        Client-side: Establish a session with the receiver by sending a session id.
        Returns True if the session is established (i.e., if an ACK is received), otherwise False.
        """
        # Generate a unique session id.
        self.session_id = str(uuid.uuid4())
        
        # Create a TCP socket.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # Connect to the receiver.
                sock.connect((self.receiver_ip, self.port))
                # Send the session id.
                sock.sendall(self.session_id.encode('utf-8'))
                print(f"[SessionLayer] Sent session id: {self.session_id}")

                # Wait for confirmation (ACK).
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
        """
        Server-side: Handles an incoming handshake initiated by the client.
        Decodes the client's session id from the initial data, sends an ACK, and returns the session id.
        """
        try:
            self.session_id = initial_data.decode('utf-8')
            conn.sendall("ACK".encode('utf-8'))
            print(f"[SessionLayer] Received session id: {self.session_id}. Sent ACK.")
            return self.session_id
        except Exception as e:
            print(f"[SessionLayer] Error during incoming session handshake: {e}")
            return None

    def initiate_session(self, conn: socket.socket) -> str:
        """
        Server-side: Initiates the handshake if the client hasn't sent a session id.
        Generates a session id, sends it to the client, waits for an ACK, and returns the session id if successful.
        """
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
        # Convert session header to bytes and concatenate with the already encoded data.
        header = f"SESSION_ID:{self.session_id}|".encode('utf-8')
        encapsulated_data = header + data
        print(f"[SessionLayer] Encapsulated data: {encapsulated_data}")
        return encapsulated_data


