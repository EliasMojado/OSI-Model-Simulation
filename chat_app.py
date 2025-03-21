import socket
import json
import threading
import os
from datetime import datetime

# Global inbox list and a lock for thread safety
inbox = []
inbox_lock = threading.Lock()

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_own_ip():
    """Attempts to retrieve the host machine's IP address."""
    try:
        # Connect to an external host to get the actual IP.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    return ip

def register_with_osi(client_socket, listening_port):
    """
    Sends a registration message to the OSI server so it knows on which port
    to forward messages for this client.
    """
    reg_message = {
        "type": "register",
        "port": listening_port
    }
    reg_str = json.dumps(reg_message)
    client_socket.sendall(reg_str.encode('utf-8'))
    print(f"Registered with OSI server on port {listening_port}.")

def inbox_listener(listening_port):
    """
    Opens a listening socket on the given port to receive incoming messages.
    Each connection is handled in its own thread.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', listening_port))
    server_socket.listen(5)
    print(f"Inbox listener running on port {listening_port}...")
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_incoming_message, args=(conn, addr), daemon=True).start()

def handle_incoming_message(conn, addr):
    """
    Receives a message, decodes it, and appends it to the global inbox.
    """
    global inbox
    try:
        data = conn.recv(4096)
        if data:
            message_str = data.decode('utf-8')
            try:
                message_obj = json.loads(message_str)
            except Exception as e:
                print("Error decoding incoming message:", e)
                return
            with inbox_lock:
                inbox.append(message_obj)
    except Exception as e:
        print("Error in inbox listener:", e)
    finally:
        conn.close()

def send_message(client_socket, sender_name, listening_port):
    """
    Prompts the user for a destination IP and message content, then sends the message
    via the persistent connection to the OSI server.
    """
    dest_ip = input("Enter destination IP address: ").strip()
    content = input("Enter your message: ").strip()
    # Get current date and time in a readable format.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_obj = {
        "sender": sender_name,
        "content": content,
        "timestamp": timestamp,
        "destination": dest_ip,
        "dest_port": listening_port
    }
    message_str = json.dumps(message_obj)
    client_socket.sendall(message_str.encode('utf-8'))
    print("Message sent via OSI server.")

def view_inbox():
    """
    Displays messages stored in the inbox.
    """
    global inbox
    with inbox_lock:
        count = len(inbox)
        if not inbox:
            print("Inbox is empty.")
        else:
            print(f"\nInbox messages ({count}):")
            for idx, message in enumerate(inbox, start=1):
                sender = message.get('sender', 'Unknown')
                content = message.get('content', '')
                timestamp = message.get('timestamp', 'No timestamp')
                print(f"{idx}. [{timestamp}] From: {sender} - {content}")
            print("")  # blank line for readability

def home_page(sender_name, client_socket, osi_server_ip, osi_server_port, listening_port):
    """
    Displays a home page with a banner and a menu for sending messages or viewing the inbox.
    The user's own IP address is displayed at the top.
    """
    own_ip = get_own_ip()
    while True:
        clear_screen()
        # Show inbox count in the banner
        with inbox_lock:
            inbox_count = len(inbox)
        banner = r"""
 /$$$$$$$$ /$$                        /$$$$$$                  /$$                    
|__  $$__/| $$                       /$$__  $$                | $$                    
   | $$   | $$$$$$$   /$$$$$$       | $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ 
   | $$   | $$__  $$ /$$__  $$      | $$  | $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$
   | $$   | $$  \ $$| $$$$$$$$      | $$  | $$| $$  \__/| $$  | $$| $$$$$$$$| $$  \__/
   | $$   | $$  | $$| $$_____/      | $$  | $$| $$      | $$  | $$| $$_____/| $$      
   | $$   | $$  | $$|  $$$$$$$      |  $$$$$$/| $$      |  $$$$$$$|  $$$$$$$| $$      
   |__/   |__/  |__/ \_______/       \______/ |__/       \_______/ \_______/|__/      
          
Welcome to The Order {0}!
Your IP Address: {1}

An anonymous messaging app.
        """
        print(banner.format(sender_name, own_ip))
        print("1. Send Message")
        print(f"2. View Inbox ({inbox_count} messages)")
        print("3. Exit")
        choice = input("Select an option: ").strip()
        if choice == '1':
            send_message(client_socket, sender_name, listening_port)
            input("Press Enter to continue...")  # Pause for the user.
        elif choice == '2':
            view_inbox()
            input("Press Enter to continue...")  # Pause to let the user review.
        elif choice == '3':
            print("Exiting Chat App.")
            break
        else:
            print("Invalid option. Please choose again.")
            input("Press Enter to continue...")

def main():
    sender_name = input("Enter your name: ").strip()
    osi_server_ip = "localhost"
    osi_server_port = 5000
    listening_port = 3000  # Port for receiving messages

    # Start the inbox listener thread.
    threading.Thread(target=inbox_listener, args=(listening_port,), daemon=True).start()

    # Establish a persistent connection to the OSI server.
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((osi_server_ip, osi_server_port))
        print(f"Connected to OSI Server at {osi_server_ip}:{osi_server_port}\n")
    except Exception as e:
        print("Failed to connect to OSI Server:", e)
        return

    # Register with the OSI server so it knows where to send incoming messages.
    register_with_osi(client_socket, listening_port)

    # Display the home page for user choices.
    home_page(sender_name, client_socket, osi_server_ip, osi_server_port, listening_port)

    client_socket.close()

if __name__ == "__main__":
    main()
