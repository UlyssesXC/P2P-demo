import socket
import os

# 服务器设置
SERVER_HOST = "127.0.0.1"  # 替换为服务器地址
SERVER_PORT = 52000

def test_connection():
    """测试与服务器的连接"""
    try:
        print("Attempting to connect to the server...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client_socket.close()

def send_file(file_path):
    """发送文件到服务器"""
    try:
        print(f"Connecting to server {SERVER_HOST}:{SERVER_PORT}...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.settimeout(10)  # 设置超时时间
        print("Connection established.")

        # 发送文件名
        file_name = os.path.basename(file_path)
        print(f"Sending file name: {file_name}")
        client_socket.send(file_name.encode('utf-8'))
        print("File name sent.")

        # 等待服务器的 ACK 确认
        print("Waiting for ACK from server...")
        try:
            ack = client_socket.recv(1024).decode('utf-8')
            if ack == "ACK":
                print("ACK received.")
            else:
                print("Unexpected server response:", ack)
                return
        except socket.timeout:
            print("Error: Server did not respond in time.")
            return

        # 发送文件数据
        print(f"Sending file data for '{file_name}'...")
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                client_socket.send(chunk)
                print(f"Sent {len(chunk)} bytes.")
        print(f"File '{file_name}' sent successfully.")

        # 明确告知发送结束
        client_socket.shutdown(socket.SHUT_WR)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
if __name__ == "__main__":
    while True:
        print("\nClient Menu:")
        print("1. Test server connection")
        print("2. Send a file")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            test_connection()
        elif choice == "2":
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
