import socket

# Replace with SERVER1's actual IP address
HOST = "10.0.0.11"
PORT = 5001

def main():
    file_name = input("Enter file name to request: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(file_name.encode())
        response = s.recv(8192)

        if response.startswith(b"SINGLE|"):
            data = response.split(b"|", 1)[1]
            print(f" File received: {file_name}")
            with open(f"client_{file_name}", "wb") as f:
                f.write(data)
        elif response.startswith(b"DIFFERENT|"):
            parts = response.split(b"|")
            server1_data = parts[2]
            server2_data = parts[4]
            print(f"⚠️ File contents differ between SERVER1 and SERVER2.")
            with open(f"client_SERVER1_{file_name}", "wb") as f:
                f.write(server1_data)
            with open(f"client_SERVER2_{file_name}", "wb") as f:
                f.write(server2_data)
            print(f"Saved both versions locally.")
        else:
            print("File not found on any server.")

if __name__ == "__main__":
    main()
