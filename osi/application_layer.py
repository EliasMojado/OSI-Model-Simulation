class ApplicationLayer:
    def process_message(self, message: object):
        # For demonstration, simply print the processed message.
        print(f"[ApplicationLayer] Processed message: {message}")

    def send(self, ip_address: str, data: object) -> None:
        # In our simulation, the Application Layer's send function is used
        # by the OSI server's send_message method.
        print(f"[ApplicationLayer] Sending data to {ip_address}: {data}")
