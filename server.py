import socket
import threading
import os
from datetime import datetime
import psutil  # For checking port usage (install with pip install psutil)

# Server configuration
HOST = "0.0.0.0"          # Listen on all network interfaces
PORT = 53000              # Port number
LOG_DIR = "logs"          # Directory for storing log files
FILES_DIR = "received_files"  # Directory for storing received files
LOG_FILE = os.path.join(LOG_DIR, "server_log.txt")
server_socket = None       # Global server socket

# Ensure the directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

def log_activity(message):
    """
    Log activity to both the log file and the command line.
    :param message: The message to log.
    """
    print(message)  # Print the message to the console
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def handle_client(client_socket, client_address):
    """
    Handle a single client connection.
    :param client_socket: The client socket.
    :param client_address: The client's address.
    """
    log_activity(f"Client connected: {client_address}")
    try:
        # Receive the file name
        file_name = client_socket.recv(1024).decode('utf-8')
        if not file_name:
            log_activity(f"No file name received from {client_address}. Closing connection.")
            return

        log_activity(f"Receiving file: {file_name} from {client_address}")

        # Send acknowledgment (ACK) to the client
        client_socket.send("ACK".encode('utf-8'))

        # Receive the file data and save it
        file_path = os.path.join(FILES_DIR, file_name)
        with open(file_path, "wb") as f:
            while True:
                chunk = client_socket.recv(4096)  # Read data in 4KB chunks
                if not chunk:  # End of file transfer
                    break
                f.write(chunk)
        log_activity(f"File {file_name} received successfully from {client_address}")
    except Exception as e:
        log_activity(f"Error: {e}")
    finally:
        client_socket.close()
        log_activity(f"Client disconnected: {client_address}")

def check_port_usage(port):
    """
    Check if a specific port is in use.
    :param port: The port to check.
    :return: (PID of the process using the port, address) or (None, None) if not in use.
    """
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port:
            return conn.pid, conn.laddr
    return None, None

def start_server():
    """
    Start the server to listen for incoming connections.
    """
    global server_socket
    log_activity("Initializing server...")
    
    # Check if the port is already in use
    pid, addr = check_port_usage(PORT)
    if pid:
        log_activity(f"Port {PORT} is already in use by process PID {pid} (address: {addr}). Exiting.")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        log_activity(f"Server bound to {HOST}:{PORT}")
        server_socket.listen(5)
        log_activity("Server started. Waiting for connections...")
    except Exception as e:
        log_activity(f"Server setup error: {e}")
        return

    try:
        while True:
            # Accept new client connections
            log_activity("Waiting for a new connection...")
            client_socket, client_address = server_socket.accept()
            log_activity(f"Accepted connection from {client_address}")

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        log_activity("Shutting down server due to keyboard interrupt.")
    finally:
        if server_socket:
            server_socket.close()
            log_activity("Server socket closed. Exiting.")

if __name__ == "__main__":
    start_server()
