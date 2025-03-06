import socket
from osi import ApplicationLayer, DataLinkLayer

def get_local_ip() -> str:
    """
    Determine the real IP address of the current machine.
    This method creates a dummy connection to a public DNS server to fetch the local IP.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public server (Google's DNS server here); no data is sent.
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

def main():
    # Ask for the sender's name once at the beginning.
    sender_name = input("Enter your name: ").strip()

    # Display the user's real IP address.
    real_ip = get_local_ip()
    print(f"Your real IP address is: {real_ip}")
    
    # Create an instance of the Data Link Layer to generate a virtual MAC address.
    data_link_layer = DataLinkLayer()
    virtual_mac = data_link_layer.get_virtual_mac()
    print(f"Your virtual MAC address is: {virtual_mac}\n")
    
    # Create an instance of the ApplicationLayer.
    app_layer = ApplicationLayer()

    banner = r"""
 /$$$$$$$$ /$$                        /$$$$$$                  /$$                    
|__  $$__/| $$                       /$$__  $$                | $$                    
   | $$   | $$$$$$$   /$$$$$$       | $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ 
   | $$   | $$__  $$ /$$__  $$      | $$  | $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$
   | $$   | $$  \ $$| $$$$$$$$      | $$  | $$| $$  \__/| $$  | $$| $$$$$$$$| $$  \__/
   | $$   | $$  | $$| $$_____/      | $$  | $$| $$      | $$  | $$| $$_____/| $$      
   | $$   | $$  | $$|  $$$$$$$      |  $$$$$$/| $$      |  $$$$$$$|  $$$$$$$| $$      
   |__/   |__/  |__/ \_______/       \______/ |__/       \_______/ \_______/|__/      
          
Welcome to The Order {}! We are a secret society of hackers who communicate through a secret chat application. 
    """

    print(banner.format(sender_name))

    while True:
        # Ask for the receiver's IP address.
        ip_address = input("Enter the IP address of the receiver (or type 'exit' to quit): ").strip()
        if ip_address.lower() == 'exit':
            print("Exiting ChatApp.")
            break

        # Ask for the message content.
        content = input("Enter your message: ").strip()

        # Create a generic message object (a dictionary in this case).
        message_obj = {
            "sender": sender_name,
            "content": content
        }

        # Use the Application Layer to send the generic object.
        app_layer.send(ip_address, message_obj)
        print()  # Blank line for readability.

if __name__ == "__main__":
    main()
