import json

class ApplicationLayer:
    def process_message(self, message: object):
        # For demonstration, simply print the processed message.
        print(f"[ApplicationLayer] Processed message: {message}")

    def encapsulate(self, message_obj: object) -> str:
        """
        Simulate application-layer encapsulation:
        Convert the message object into a JSON string and add an application header.
        """
        json_str = json.dumps(message_obj)
        encapsulated = f"APP_HEADER|{json_str}"
        print(f"[ApplicationLayer] Encapsulated data: {encapsulated}")
        return encapsulated
