import socket
from threading import Thread, Semaphore
import pathlib
import os
from uuid import uuid1

# Remote File Manager


class Model:
    _register = dict()
    _credentials = dict()
    _sessions = dict()


class FileServer(Thread):
    _sep = os.path.sep
    _store_path = f"{pathlib.Path.cwd()}{_sep}store{_sep}"

    def __init__(self, rsocket, socket_name):
        print(f"Socket connected: {socket_name}")
        self.socket = rsocket
        self.socket_name = socket_name
        self._populate_register()
        self._populate_credentials()
        print(Model._credentials)
        print()
        print(Model._register)
        Thread.__init__(self)
        self.start()

    def _populate_register(self):
        for entry in pathlib.Path(FileServer._store_path).iterdir():
            metadata = dict()
            metadata["size"] = entry.stat().st_size
            metadata["semaphore"] = Semaphore(5)
            Model._register[entry.name] = metadata

    def _populate_credentials(self):
        with open("./credentials.txt") as file:
            while True:
                data = file.readline().strip()
                if len(data) == 0:
                    break
                name, password = eval(data)
                Model._credentials[name] = (name, password)

    def run(self):
        while True:
            client_header = self.socket.recv(1024).decode("utf-8").strip()
            request_length = int(client_header)
            data_bytes = b''
            while len(data_bytes) < request_length:
                b = self.socket.recv(request_length - len(data_bytes))
                data_bytes += b
            request = data_bytes.decode("utf-8").strip()
            request = eval(request)
            operation = request[0]

            if operation == "authenticate":
                request_length = int(self.socket.recv(
                    1024).decode("utf-8").strip())
                data_bytes = b''
                while len(data_bytes) < request_length:
                    b = self.socket.recv(request_length - len(data_bytes))
                    data_bytes += b
                request = data_bytes.decode("utf-8").strip()
                data = eval(request)
                username, password = data
                if (username in Model._credentials) and (data == Model._credentials[username]):
                    unique_id = str(uuid1())
                    Model._sessions[unique_id] = data
                    response = str(("Correct", unique_id))
                    response_length = str(len(response)).ljust(1024)
                    self.socket.sendall(bytes(response_length, "utf-8"))
                    self.socket.sendall(bytes(response, "utf-8"))
                else:
                    response = str(("Incorrect",))
                    response_length = str(len(response)).ljust(1024)
                    self.socket.sendall(bytes(response_length, "utf-8"))
                    self.socket.sendall(bytes(response, "utf-8"))
                    break

            if operation == "quit":
                if request[1] in Model._sessions:
                    Model._sessions.pop(request[1])
                print("'quit' request is recieved")
                print(f"Closing socket: {self.socket_name}")
                break

            if operation == "dir":
                if request[1] not in Model._sessions:
                    print("The client with credentials : ",
                          Model._sessions[request[1]], "is not active.")
                    break
                print("'dir' request is recieved")
                files_list = dict()
                for key in Model._register:
                    files_list[key] = Model._register[key]["size"]
                response = str(files_list)
                response_length = bytes(
                    str(len(response)).ljust(1024), "utf-8")
                self.socket.sendall(response_length)
                self.socket.sendall(bytes(response, "utf-8"))

            if operation == "get":
                if request[1] not in Model._sessions:
                    print("The client with credentials : ",
                          Model._credentials[request[1]], "is not active.")
                    break
                print("'get' request is recieved")
                filename_length_in_bytes = self.socket.recv(
                    1024).decode("utf-8").strip()
                filename_length = int(filename_length_in_bytes)
                data_bytes = b''
                while len(data_bytes) < filename_length:
                    b = self.socket.recv(filename_length - len(data_bytes))
                    data_bytes += b
                filename = data_bytes.decode("utf-8").strip()
                if filename not in Model._register:
                    self.socket.sendall(bytes("No".ljust(1024), "utf-8"))
                else:
                    product = Model._register[filename]["semaphore"]
                    self.socket.sendall(bytes("Yes".ljust(1024), "utf-8"))
                    response = Model._register[filename]["size"]
                    response_file_size = bytes(
                        str(response).ljust(1024), "utf-8")
                    self.socket.sendall(response_file_size)
                    product.acquire()
                    with open(FileServer._store_path + filename, "rb") as file:
                        count = 1
                        while True:
                            data = file.read(4096)
                            if len(data) == 0:
                                break
                            self.socket.sendall(data)
                            print(f"Packet {count} sent")
                            count += 1
                    product.release()
                    print("File Completely Sent to the Client")
        print(f"Socket {self.socket_name} is about to close.")
        self.socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 5500))
server_socket.listen()

while True:
    print("Server is ready and listening at localhost on port 5500")
    rsocket, socket_name = server_socket.accept()
    fs = FileServer(rsocket, socket_name)
