## Distributing Computing Assignment -1
## Group Number: GROUP-2

| **Sl. No.** | **Name (as appears in Canvas) / ID NO** | **Contribution**                                                                                                                                                                                                                                                               |
| ----------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1           | Anurag Vaishnava / 2024mt03544          | Worked on Server1<br>which manages incoming client requests, forwards queries to Server2, and performs file comparison logic. <br>Setup AWS LAB with required security policies and ports for incoming and outgoing traffic<br>Deployment and testing use cases (Together)<br> |
| 2           | R, Adithiya / 2024MT03577               | Worked on Server1<br>which manages incoming client requests, forwards queries to Server2, and performs file comparison logic. <br>Setup AWS LAB with required security policies and ports for incoming and outgoing traffic<br>Deployment and testing use cases (Together)     |
| 3           | Jinu George / 2024mt03559               | Worked on Server2<br>Responsible for storing files, serving requests from Server1, and handling error cases such as missing files.<br>Deployed to github and prepared Readme file<br>Deployment and testing use cases (Together)                                               |
| 4           | Amulya Nrusimhadri/ 2024MT03522         | Worked on Server2<br>Responsible for storing files, serving requests from Server1, and handling error cases such as missing files.<br>Deployed to github and prepared Readme file<br>Deployment and testing use cases (Together)                                               |
| 5           | BALAMURUGAN. E / 2024mt03542            | Worked on Client Code<br>Independently developed and deployed the Client Code.<br>This component initiates file requests, receives responses from Server1, and manages version conflicts on the client side.<br>Reviewed test cases and final verification.                    |


## GitHub (shared git repo):
https://github.com/jinugeorge2290/BITS_PILANI_DS_Assignment1_Group2.git


## Language used for Implementation:

- Python
- OS (Red hat Linux) on BITS Lab Nodes

## Prerequisites Before Running the Scripts
Before executing the scripts, ensure the following steps are completed on all nodes (Server 1, Server 2, and Client):
#### **Step 1** – Install pip
Since Python is already installed on all machines, verify that pip is available.
If not, install it using the following command on each server and the client machine:
sudo dnf install python3-pip
#### **Step 2** – Create Required Directories
Create the directories for storing files on both Server 1 and Server 2:
mkdir -p ~/distributed_system/files/server1
mkdir -p ~/distributed_system/files/server2
These directories will be used to store the files that the servers will serve.
#### **Step 3** – Identify IP Addresses
Retrieve the IP addresses of Server 1, Server 2, and the Client machine.
This is required to configure network communication between them.
#### **Step 4** – Update IP Addresses in Scripts 
Open server1.py, server2.py, and client.py and update the IP address on 
Also use the below commands to open ports on nodes 
•	sudo firewall-cmd --zone=public --add-port=5001/tcp --permanent
o	Opens TCP port 5001 for SERVER1.
•	sudo firewall-cmd --zone=public --add-port=5002/tcp --permanent
o	Opens TCP port 5002 for SERVER2.


**SERVER2**
Listens on: Port 5002 (0.0.0.0:5002)
Only SERVER1 connects to SERVER2 on this port to request files.
**SERVER1**
Listens on: Port 5001 (0.0.0.0:5001)
Only CLIENT connects to SERVER1 on this port to request files.
**CLIENT**
Connects to: SERVER1 on port 5001 to request files.



**SERVER1 Code:**

```bash

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

```



SERVER2 Code:

```bash

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

```

 
CLIENT Code:
```bash
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
```

 
## Test Case	

### 1  - File exists on both servers (with identical content)

| Test Case                                             | Pre-Condition / Setup                                                        | Input (File Request) | Expected SERVER1 Behavior                                                                              | Expected CLIENT Output                    |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| Test case 1 – File exists on both servers (identical) | Same file with identical content present in server1 and server2 directories. | file1.txt            | SERVER1 finds local file, requests from SERVER2, compares contents → identical → sends SINGLE\|<file>. | Client receives single copy of file1.txt. |

### 2 - File exists on both servers (with different content)

| Test Case                                   | Pre-Condition / Setup                                                                 | Input (File Request) | Expected SERVER1 Behavior                                                                                                             | Expected CLIENT Output                         |
| ------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 2 – File exists on both servers (different) | File with same name but different content present in server1 and server2 directories. | File1.txt            | SERVER1 finds local file, requests from SERVER2, compares contents → different → sends DIFFERENT\|SERVER1\|<data1>\|SERVER2\|<data2>. | Client receives both versions and can compare. |
### 3 - File exists only on SERVER1

| Test Case                       | Pre-Condition / Setup                   | Input (File Request) | Expected SERVER1 Behavior                                                     | Expected CLIENT Output                    |
| ------------------------------- | --------------------------------------- | -------------------- | ----------------------------------------------------------------------------- | ----------------------------------------- |
| 3 – File exists only on SERVER1 | File present only in server1 directory. | File1.txt            | SERVER1 finds file locally, SERVER2 returns NOT_FOUND → sends SINGLE\|<file>. | Client receives single copy from SERVER1. |


### 4 - File missing on both servers

| Test Case                        | Pre-Condition / Setup                 | Input (File Request) | Expected SERVER1 Behavior                                                 | Expected CLIENT Output                                  |
| -------------------------------- | ------------------------------------- | -------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------- |
| 4 – File missing on both servers | File not present in either directory. | File1.txt            | SERVER1 finds no local file, SERVER2 returns NOT_FOUND → sends NOT_FOUND. | Client displays 'File not found on any server' message. |



 






