import socket

class PhysicalLayer:
    def __init__(self):
        pass

    def transmit(self, data: bytes, ip_address: str, dest_port: int):
        """
        Transmit the data to the destination IP and port.
        """
        print("OSI: [physical layer] Transmitting data:")
        print("     ", data)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print("OSI: [physical layer] Connecting to {}:{}".format(ip_address, dest_port))
                s.connect((ip_address, dest_port))
                s.sendall(data)
                print("OSI: [physical layer] Data transmitted successfully.")
        except Exception as e:
            print("OSI: [physical layer] Error transmitting data:", e)
