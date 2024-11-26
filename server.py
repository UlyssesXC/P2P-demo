import socket
import threading
import os
import signal
from datetime import datetime
import psutil  # 需要安装 psutil: pip install psutil

# 服务器设置
HOST = "0.0.0.0"  # 监听所有网络接口
PORT = 53000       # 端口号
LOG_FILE = "server_log.txt"
server_socket = None  # 全局服务器套接字

def log_activity(message):
    """记录活动日志"""
    print(message)  # 打印到控制台
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def handle_client(client_socket, client_address):
    """处理客户端连接"""
    log_activity(f"Client connected: {client_address}")
    try:
        # 接收文件名
        log_activity(f"Waiting for file name from {client_address}...")
        file_name = client_socket.recv(1024).decode('utf-8')

        if not file_name:
            log_activity(f"No file name received from {client_address}. Closing connection.")
            return

        log_activity(f"Receiving file: {file_name} from {client_address}")

        # 发送 ACK 确认
        log_activity(f"Sending ACK to {client_address}")
        client_socket.send("ACK".encode('utf-8'))

        # 接收文件数据
        log_activity(f"Waiting for file data for: {file_name}")
        with open(file_name, "wb") as f:
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                log_activity(f"Received {len(chunk)} bytes")
                f.write(chunk)
        log_activity(f"File {file_name} received successfully from {client_address}")
    except Exception as e:
        log_activity(f"Error: {e}")
    finally:
        client_socket.close()
        log_activity(f"Client disconnected: {client_address}")

def check_port_usage(port):
    """检查端口是否被占用"""
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port:
            return conn.pid, conn.laddr
    return None, None

def start_server():
    """启动服务器"""
    global server_socket
    log_activity("Initializing server...")
    
    # 检查端口是否被占用
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
            log_activity("Waiting for a new connection...")
            client_socket, client_address = server_socket.accept()
            log_activity(f"Accepted connection from {client_address}")

            # 为每个客户端启动一个线程
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
