# BITS_DS_ASSIGNMENT_1

## I am running this assignment on my 3 node Ubuntu VM's inside proxmox
![alt text](image.png)

## Server Details


| No  | Server Name | IP            | Files | Purpose                                                                                                 |
| --- | ----------- | ------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | server1     | 192.168.1.101 |       | Acts as the coordinator. Receives requests from the client. Checks its own files. Contacts server2 for comparison. Decides what to send back to client. |
| 2   | server2     | 192.168.1.102 |       | Acts as a replica server. Stores its own copy of the files. Returns file to server1 when asked.                                                                       |
| 3   | client     | 192.168.1.103 |       | This is client machine (runs client.py).Sends requests to server1. Receives responses.                                                                          |

## File Placements

- On server1: put some files in /home/ubuntu/BITS_DS_ASSIGNMENT_1

- On server2: put some files in /home/ubuntu/BITS_DS_ASSIGNMENT_1

```bash
# On server1
mkdir -p ~/BITS_DS_ASSIGNMENT_1/server1_files
echo "Hello from Server1" > ~/BITS_DS_ASSIGNMENT_1/server1_files/test.txt

# On server2
mkdir -p ~/BITS_DS_ASSIGNMENT_1/server2_files
echo "Hello from Server2" > ~/BITS_DS_ASSIGNMENT_1/server2_files/test.txt
```


server1.py (on 192.168.1.101)
```python
import socket
import os

HOST = "0.0.0.0"       # Listen on all interfaces
PORT = 6001            # Port for server1
SERVER2_HOST = "192.168.1.102"   # IP of server2
SERVER2_PORT = 6002
SERVER1_DIR = "server1_files/"

def get_file_from_server2(filepath):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER2_HOST, SERVER2_PORT))
        s.sendall(filepath.encode())
        data = s.recv(4096)
        return data

def handle_client(conn):
    filepath = conn.recv(1024).decode()
    print(f"[SERVER1] Request for {filepath}")

    file1_data = None
    file2_data = None

    fullpath = os.path.join(SERVER1_DIR, filepath)
    if os.path.exists(fullpath):
        with open(fullpath, "rb") as f:
            file1_data = f.read()

    file2_data = get_file_from_server2(filepath)

    if file1_data and file2_data != b"FILE_NOT_FOUND":
        if file1_data == file2_data:
            conn.sendall(b"SINGLE_FILE|" + file1_data)
        else:
            conn.sendall(b"DIFFERENT_FILES|SERVER1|" + file1_data + b"|SERVER2|" + file2_data)
    elif file1_data:
        conn.sendall(b"SINGLE_FILE|" + file1_data)
    elif file2_data != b"FILE_NOT_FOUND":
        conn.sendall(b"SINGLE_FILE|" + file2_data)
    else:
        conn.sendall(b"ERROR|File not found on both servers")

def start_server1():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER1] Listening on {HOST}:{PORT}")
        while True:
            conn, _ = s.accept()
            with conn:
                handle_client(conn)

if __name__ == "__main__":
    start_server1()

```

server2.py (on 192.168.1.102)
```python

import socket
import os

HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 6002
SERVER2_DIR = "server2_files/"

def handle_request(conn):
    filepath = conn.recv(1024).decode()
    fullpath = os.path.join(SERVER2_DIR, filepath)
    if os.path.exists(fullpath):
        with open(fullpath, "rb") as f:
            conn.sendall(f.read())
    else:
        conn.sendall(b"FILE_NOT_FOUND")

def start_server2():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER2] Listening on {HOST}:{PORT}")
        while True:
            conn, _ = s.accept()
            with conn:
                handle_request(conn)

if __name__ == "__main__":
    start_server2()
```

client.py (on 192.168.1.103)

```python
import socket

SERVER1_HOST = "192.168.1.101"  # IP of server1
SERVER1_PORT = 6001

def request_file(filepath):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER1_HOST, SERVER1_PORT))
        s.sendall(filepath.encode())
        data = s.recv(8192)

        if data.startswith(b"SINGLE_FILE|"):
            print("[CLIENT] Got file successfully.")
            with open("client_received.txt", "wb") as f:
                f.write(data.split(b"|", 1)[1])
        elif data.startswith(b"DIFFERENT_FILES|"):
            print("[CLIENT] Conflict! Got both versions.")
            parts = data.split(b"|")
            with open("server1_version.txt", "wb") as f:
                f.write(parts[2])
            with open("server2_version.txt", "wb") as f:
                f.write(parts[4])
        else:
            print(data.decode())

if __name__ == "__main__":
    filepath = input("Enter file name (e.g., test.txt): ")
    request_file(filepath)

```


## How to Run
Run the python scripts on each of the server instances.
The from the client to check various scenarios

**On server2 (192.168.1.102):**
```bash
python3 server2.py
```
Output


**On server1 (192.168.1.101):**
```bash
python3 server1.py
```
**On client (192.168.1.103):**
```bash
python3 client.py
```

---
## Scenarios

### 1 - Identical Files Test
File exists on both servers (with identical content)

#### Output
```bash
## Server 1 Content
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1/server1_files$ cat file1.txt
Hello!! Identical content test
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1/server1_files$
-- Run the script on server1
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1$ python3 server1.py
[SERVER1] Listening on 0.0.0.0:6001

## Server 2 Content
ubuntu@server2:~/BITS_DS_ASSIGNMENT_1$ cat file1.txt
Hello!! Identical content test
ubuntu@server2:~/BITS_DS_ASSIGNMENT_1$
-- Run the script on server2
ubuntu@server2:~/BITS_DS_ASSIGNMENT_1$ python3 server2.py
[SERVER2] Listening on 0.0.0.0:6002

## Client
--- There is no file received yet
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ ls -ll
total 4
-rw-rw-r-- 1 ubuntu ubuntu 985 Sep 11 02:44 client.py

-- Run the script 
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ python3 client.py
Enter file name (e.g., test.txt): file1.txt
[CLIENT] Got file successfully.

-- The request goes to Server1 
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1$ python3 server1.py
[SERVER1] Listening on 0.0.0.0:6001
[SERVER1] Request for file1.txt

---- Received file from Server1 with same content (file named client_received.txt)
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ ls -ll
total 8
-rw-rw-r-- 1 ubuntu ubuntu 985 Sep 11 02:44 client.py
-rw-rw-r-- 1 ubuntu ubuntu  31 Sep 11 03:54 client_received.txt
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ cat client_received.txt
Hello!! Identical content test
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$


```

### 2 – File exists on both servers (with different content)

#### Output
```bash
## Server 1 Content
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1/server1_files$ cat file2.txt
Hello from Server1
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1/server1_files$

-- Run the script on server1
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1$ python3 server1.py
[SERVER1] Listening on 0.0.0.0:6001


## Server 2 Content
ubuntu@server2:~/BITS_DS_ASSIGNMENT_1/server2_files$ cat file2.txt
Hello from Server2
ubuntu@server2:~/BITS_DS_ASSIGNMENT_1/server2_files$

-- Run the script on server2
ubuntu@server2:~/BITS_DS_ASSIGNMENT_1$ python3 server2.py
[SERVER2] Listening on 0.0.0.0:6002


## Client

--- There is no file received yet
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ ls -ll
total 8
-rw-rw-r-- 1 ubuntu ubuntu 985 Sep 11 02:44 client.py

-- Run the script on the client server

ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ python3 client.py
Enter file name (e.g., test.txt): file2.txt
[CLIENT] Conflict! Got both versions.
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$

-- Received files from both server with different contnent

ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ ls -ll
total 16
-rw-rw-r-- 1 ubuntu ubuntu 985 Sep 11 02:44 client.py
-rw-rw-r-- 1 ubuntu ubuntu  31 Sep 11 03:54 client_received.txt
-rw-rw-r-- 1 ubuntu ubuntu  19 Sep 11 04:05 server1_version.txt
-rw-rw-r-- 1 ubuntu ubuntu  19 Sep 11 04:05 server2_version.txt
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ cat server1_version.txt
Hello from Server1
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ cat server2_version.txt
Hello from Server2
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$


```


### 3 - File available only on 1 server


#### Output
```bash
## Server 1 Content 
ubuntu@server1:~/BITS_DS_ASSIGNMENT_1/server1_files$ cat file3.txt
File only on Server1

ubuntu@server1:~/BITS_DS_ASSIGNMENT_1$ python3 server1.py
[SERVER1] Listening on 0.0.0.0:6001

## Server 2 Content
-- File not present in Server 2

## Client
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ python3 client.py
Enter file name (e.g., test.txt): file3.txt
[CLIENT] Got file successfully.
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$


-- Received files from only Server1

ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ cat client_received.txt
File only on Server1
```

### 4 - File Missing on Both Servers

#### Output
```bash

## Client
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$ python3 client.py
Enter file name (e.g., test.txt): file4.txt
ERROR|File not found on both servers
ubuntu@client:~/BITS_DS_ASSIGNMENT_1$

```
