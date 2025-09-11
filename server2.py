import socket
import os

# Listen on all network interfaces
HOST = "0.0.0.0"
PORT = 5002
FILE_DIR = os.path.expanduser("~/distributed_system/files/server2")

def handle_request(conn):
    try:
        data = conn.recv(1024).decode()
        if not data:
            return

        file_path = os.path.join(FILE_DIR, data)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_data = f.read()
            conn.sendall(b"FOUND|" + file_data)
        else:
            conn.sendall(b"NOT_FOUND")
    except Exception as e:
        print(f"[SERVER2] Error: {e}")
    finally:
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"SERVER2 running on {HOST}:{PORT}, serving files from {FILE_DIR}")
        while True:
            conn, addr = s.accept()
            print(f"[SERVER2] Connection from {addr}")
            handle_request(conn)

if __name__ == "__main__":
    main()
