import socket
import json

def register_with_osi(client_socket, listening_port):
    # Create a registration message.
    reg_message = {
        "type": "register",
        "port": listening_port
    }
    # Send the registration message.
    reg_str = json.dumps(reg_message)
    client_socket.sendall(reg_str.encode('utf-8'))
    print(f"Registered with OSI server on port {listening_port}.")

def main():
    # Ask for the sender's name.
    sender_name = input("Enter your name: ").strip()

    # Automatically use localhost since the OSI server is running on the same machine.
    osi_server_ip = "localhost"
    port = 5000
    listening_port = 3000

    # Display the welcome banner.
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

    # Secure a persistent connection to the OSI server.
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((osi_server_ip, port))
        print(f"Connected to OSI Server at {osi_server_ip}:{port}\n")
    except Exception as e:
        print("Failed to connect to OSI Server:", e)
        return
    
    # Immediately register this connection to receive messages on port 3000.
    register_with_osi(client_socket, listening_port)

    # Main chat loop using the persistent connection.
    try:
        while True:
            # Ask for the destination IP (this simulates the target; even if on the same machine, you can send to "localhost" or other virtual IPs).
            dest_ip = input("Enter destination IP address (or type 'exit' to quit): ").strip()
            if dest_ip.lower() == "exit":
                print("Exiting Chat App.")
                break

            content = input("Enter your message: ").strip()

            # Create a message object that includes sender, content, and destination.
            message_obj = {
                "sender": sender_name,
                "content": content,
                "destination": dest_ip,
                "dest_port": listening_port
            }

            # Serialize the message and send it over the persistent socket.
            message_str = json.dumps(message_obj)
            client_socket.sendall(message_str.encode('utf-8'))
            print("Message sent via OSI server.\n")
    except Exception as e:
        print("Error during communication:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
