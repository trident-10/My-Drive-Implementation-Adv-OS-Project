import socket
import threading

HEADER = 64
PORT = 5051
# SERVER = "192.168.100.219"
# ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"import socket
import threading
import logging
import os

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADER = 64
PORT = 5051
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def send_file(conn, filename):
    with open(filename, 'rb') as file:
        # Send file size and filename
        filename_encoded = filename.encode(FORMAT)
        file_size = file.seek(0, 2)  # Move to end of file to get file size
        file.seek(0)  # Reset file pointer to the beginning
        file_info = f"{len(filename_encoded):<{HEADER}}" + f"{file_size:<{HEADER}}"
        conn.send(file_info.encode(FORMAT))
        conn.send(filename_encoded)

        # Send the file in chunks
        while True:
            data = file.read(4096)
            if not data:
                break
            conn.send(data)
        logging.info(f"Sent file: {filename}")

def receive_file(conn):
    file_info = conn.recv(HEADER * 2).decode(FORMAT)
    filename_length = int(file_info[:HEADER].strip())
    file_size = int(file_info[HEADER:].strip())

    filename = conn.recv(filename_length).decode(FORMAT)
    filename = os.path.basename(filename)  # Extracts only the filename from the path

    save_path = f"received_{filename}"  # You can adjust the directory as needed
    with open(save_path, 'wb') as file:
        while file_size > 0:
            data = conn.recv(4096)
            file.write(data)
            file_size -= len(data)
    logging.info(f"Received file: {filename}")

def handle_client(conn, addr):
    logging.info(f'[NEW CONNECTION] {addr} connected')
    connected = True
    while connected:
        command = conn.recv(HEADER).decode(FORMAT).strip()
        if not command:
            break
        if command == "send_file":
            send_file(conn, "example_server_file.txt")  # Specify your file to send
        elif command == "receive_file":
            receive_file(conn)
        elif command == DISCONNECT_MESSAGE:
            break
    conn.close()
    logging.info(f"[DISCONNECT] {addr} disconnected")

def start():
    server.listen()
    logging.info(f'[LISTENING] Server is listening on {SERVER}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        logging.info(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')

if __name__ == "__main__":
    logging.info("[STARTING] server is starting...")
    start()




def main():
    server_ip = input("Enter the server Local IP address: ")
    ADDR = (server_ip, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    def send_file(filename):
        command = "receive_file".encode(FORMAT)  # Tell server to prepare to receive
        command += b' ' * (HEADER - len(command))
        client.send(command)

        with open(filename, 'rb') as file:
            # Send file size and filename
            filename_encoded = filename.encode(FORMAT)
            file_size = file.seek(0, 2)
            file.seek(0)
            file_info = f"{len(filename_encoded):<{HEADER}}" + f"{file_size:<{HEADER}}"
            client.send(file_info.encode(FORMAT))
            client.send(filename_encoded)

            # Send the file in chunks
            while True:
                data = file.read(4096)
                if not data:
                    break
                client.send(data)
            print(f"Sent file: {filename}")

    def receive_file():
        command = "send_file".encode(FORMAT)  # Request file from server
        command += b' ' * (HEADER - len(command))
        client.send(command)

        file_info = client.recv(HEADER * 2).decode(FORMAT)
        filename_length = int(file_info[:HEADER].strip())
        file_size = int(file_info[HEADER:].strip())

        filename = client.recv(filename_length).decode(FORMAT)
        with open(f"received_{filename}", 'wb') as file:
            while file_size > 0:
                data = client.recv(4096)
                file.write(data)
                file_size -= len(data)
        print(f"Received file: {filename}")

    while True:
        cmd = input("Enter command (send_file, receive_file, exit): ")
        if cmd == "send_file":
            filename = input("Enter filename to send: ")
            send_file(filename)
        elif cmd == "receive_file":
            receive_file()
        elif cmd == "exit":
            break

    client.close()

if __name__ == "__main__":
    main()
