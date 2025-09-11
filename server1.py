import socket
import os

# Listen on all network interfaces
HOST = "0.0.0.0"
PORT = 5001

# Replace with SERVER2's actual IP address
SERVER2_HOST = "10.0.0.12"
SERVER2_PORT = 5002

FILE_DIR = os.path.expanduser("~/distributed_system/files/server1")

def request_from_server2(file_name):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER2_HOST, SERVER2_PORT))
            s.sendall(file_name.encode())
            data = s.recv(4096)
            return data
    except ConnectionRefusedError:
        print("[SERVER1] Could not connect to SERVER2.")
        return b"NOT_FOUND"

def handle_client(conn):
    try:
        file_name = conn.recv(1024).decode()
        file1_path = os.path.join(FILE_DIR, file_name)

        file1_data = None
        if os.path.exists(file1_path):
            with open(file1_path, "rb") as f:
                file1_data = f.read()

        server2_response = request_from_server2(file_name)
        file2_data = None
        if server2_response.startswith(b"FOUND|"):
            file2_data = server2_response.split(b"|", 1)[1]

        if file1_data and file2_data:
            if file1_data == file2_data:
                conn.sendall(b"SINGLE|" + file1_data)
            else:
                conn.sendall(b"DIFFERENT|SERVER1|" + file1_data + b"|SERVER2|" + file2_data)
        elif file1_data:
            conn.sendall(b"SINGLE|" + file1_data)
        elif file2_data:
            conn.sendall(b"SINGLE|" + file2_data)
        else:
            conn.sendall(b"NOT_FOUND")
    finally:
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"SERVER1 running on {HOST}:{PORT}, serving files from {FILE_DIR}")
        while True:
            conn, addr = s.accept()
            print(f"[SERVER1] Client connected from {addr}")
            handle_client(conn)

if __name__ == "__main__":
    main()
