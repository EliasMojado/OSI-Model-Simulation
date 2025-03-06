from osi import ApplicationLayer

def main():
    # Ask for the sender's name once at the beginning.
    sender_name = input("Enter your name: ").strip()

    # Create an instance of the ApplicationLayer once.
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
        print() 

if __name__ == "__main__":
    main()
