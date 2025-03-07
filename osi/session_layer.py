import socket
import uuid

class SessionLayer:
    def __init__(self, receiver_ip: str, port: int = 5000):
        """
        Initialize with the receiver's IP and port.
        """
        self.receiver_ip = receiver_ip
        self.port = port
        self.session_id = None

    def establish_session(self) -> bool:
        """
        Establish a session with the receiver by sending a session id.
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

    def encapsulate(self, data: str) -> str:
        """
        Encapsulate the data with the session id header.
        If the session hasn't been established yet, attempt to establish it first.
        """
        if not self.session_id:
            print("[SessionLayer] No active session. Establishing session now...")
            if not self.establish_session():
                raise Exception("Failed to establish session with the receiver.")

        # Attach the session id as a header to the data.
        encapsulated_data = f"SESSION_ID:{self.session_id}|{data}"
        print(f"[SessionLayer] Encapsulated data: {encapsulated_data}")
        return encapsulated_data