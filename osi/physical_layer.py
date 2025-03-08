import socket

class PhysicalLayer:
    def __init__(self):
        pass

    def transmit(self, data: bytes, ip_address: str, dest_port: int):
        """
        Transmit the data to the destination IP and port.
        """
        print("[PhysicalLayer] Transmitting data: ", data)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print("[PhysicalLayer] Connecting to {}:{}".format(ip_address, dest_port))
                print()
                s.connect((ip_address, dest_port))
                s.sendall(data)
                print("[PhysicalLayer] Data transmitted successfully.", end="\n\n")
        except Exception as e:
            print("[PhysicalLayer] Error transmitting data:", e)
