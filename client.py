import socket
import os

# Server configuration
SERVER_HOST = "127.0.0.1"  # Replace with the server's address
SERVER_PORT = 52001        # Port number

def test_connection():
    """
    Test connection to the server.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connection to server successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client_socket.close()

def send_file(file_path):
    """
    Send a file to the server.
    :param file_path: The local path of the file to send.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.settimeout(10)  # Set timeout for server response

        # Send the file name to the server
        file_name = os.path.basename(file_path)
        client_socket.send(file_name.encode('utf-8'))

        # Wait for the server's acknowledgment (ACK)
        try:
            ack = client_socket.recv(1024).decode('utf-8')
            if ack != "ACK":
                print("Server response unexpected. Transfer aborted.")
                return
        except socket.timeout:
            print("Error: Server did not respond in time.")
            return

        # Send the file data in chunks
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):  # Read and send 4KB chunks
                client_socket.send(chunk)
        print(f"File '{file_name}' sent successfully.")

        # Indicate the end of transmission
        client_socket.shutdown(socket.SHUT_WR)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    while True:
        # Display the client menu
        print("\nClient Menu:")
        print("1. Test server connection")
        print("2. Send a file")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            test_connection()
        elif choice == "2":
            # Prompt the user to enter the file path
            file_path = input("Enter the path of the file to send: ")
            if os.path.isfile(file_path):
                send_file(file_path)
            else:
                print("Invalid file path.")
        elif choice == "3":
            print("Exiting the client...")
            break
        else:
            print("Invalid choice. Please try again.")
