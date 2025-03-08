import json
import socket

class ApplicationLayer:
    def encapsulate(self, message_obj: object) -> str:
        json_str = json.dumps(message_obj)
        encapsulated = f"APP_HEADER|{json_str}"
        print(f"[ApplicationLayer] Encapsulated data: {encapsulated}")
        return encapsulated

    def decapsulate(self, data: str) -> str:
        if data.startswith("APP_HEADER|"):
            encapsulated = data[len("APP_HEADER|"):]
            print(f"[ApplicationLayer] Decapsulated data: {encapsulated}")
            return encapsulated
        return data

    def process_message(self, message_obj: object, transport_port: int = None):
        """
        Deliver the processed message to the chat app.
        If a transport_port is provided, this method opens a connection to localhost on that port
        and sends the JSON payload. Otherwise, it simply prints the message.
        """
        payload = json.dumps(message_obj).encode('utf-8')
        if transport_port:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(('localhost', transport_port))
                    s.sendall(payload)
                    print(f"[ApplicationLayer] Delivered message to applicaton on port {transport_port}: {message_obj}")
            except Exception as e:
                print(f"[ApplicationLayer] Error delivering message on port {transport_port}: {e}")
        else:
            print(f"[ApplicationLayer] Processed message (no transport port provided): {message_obj}")
