# OSI Model Simulation

This project simulates a simplified OSI network model using Python, implementing all seven layers: Application, Presentation, Session, Transport, Network, Data Link, and Physical.

## Prerequisites

- Python 3.6+
- Required packages:
  ```sh
  pip install cryptography
  ```

## Running the Application

### 1. Start the OSI Server

First, start the OSI server which handles all network communication:

```sh
python osi/osi_server.py
```

You should see output indicating the server is running and listening for connections.

### 2. Launch the Chat Application

Next, start the chat application which provides a user interface for sending and receiving messages:

```sh
python chat_app.py
```

## Using the Chat Application

The chat application is your main interaction point with the system:

- **Enter your name** when prompted
- **Connect to other users** by providing their IP address
- **Send messages** that will be processed through all seven OSI layers
- **View received messages** from other connected users

## Architecture Overview

- **OSI Server**: Handles network protocols and message routing
- **Chat Application**: User interface for communication
- **Layer Implementation**: Each OSI layer encapsulates/decapsulates data:
  - Application Layer: Handles high-level protocols
  - Presentation Layer: Handles encryption, compression, and encoding
  - Session Layer: Manages connections between applications
  - Transport Layer: Ensures complete data transfer
  - Network Layer: Manages IP addressing and routing
  - Data Link Layer: Handles data framing
  - Physical Layer: Simulates physical transmission

## Troubleshooting

- If connections fail, verify both servers are running
- Check firewall settings to ensure ports are open
- Verify IP addresses are correct