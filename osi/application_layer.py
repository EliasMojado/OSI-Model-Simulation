class ApplicationLayer:
    def send(self, ip_address: str, data: object) -> None:
        """
        Simulate sending data through the Application Layer.
        The data parameter is generic—it could be any object.
        """
        print(f"[ApplicationLayer] Sending data to {ip_address}: {data}")
