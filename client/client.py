import socket
import sys
import pathlib
import os

# Remote File Manager


class SKClient:
    def __init__(self, server_config):
        self.server_config = server_config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.assigned_id = None
        self.autherized = False

    def connect(self):
        try:
            self.socket.connect(self.server_config)
        except ConnectionRefusedError:
            print(
                f"Could not connect to the server on host {self.server_config[0]} port {self.server_config[1]}")
            sys.exit()

    def close(self):
        self.socket.close()

    def credentials_validation(self):
        username = input("Enter Username : ")
        password = input("Enter Password : ")
        credentials = str((username, password))
        request_header = str(("authenticate",))
        request_header_length = str(len(request_header)).ljust(1024)
        self.socket.sendall(bytes(request_header_length, "utf-8"))
        self.socket.sendall(bytes(request_header, "utf-8"))

        request = bytes(credentials, "utf-8")
        length_of_request = bytes(str(len(request)).ljust(1024), "utf-8")
        self.socket.sendall(length_of_request)
        self.socket.sendall(request)

        response_length = int(self.socket.recv(1024).decode("utf-8").strip())
        data_bytes = b''
        while len(data_bytes) < response_length:
            b = self.socket.recv(response_length - len(data_bytes))
            data_bytes += b
        response = data_bytes.decode("utf-8").strip()
        decider = eval(response)
        if decider[0] == "Correct":
            self.assigned_id = decider[1]
            self.autherized = True

    def get(self, filename):
        request = str(("get", self.assigned_id))
        request_length = bytes(str(len(request)).ljust(1024), "utf-8")
        self.socket.sendall(request_length)
        self.socket.sendall(bytes(request, "utf-8"))
        filename_length = bytes(str(len(filename)).ljust(1024), "utf-8")
        self.socket.sendall(filename_length)
        self.socket.sendall(bytes(filename, "utf-8"))

        data_bytes = b''
        response_length = 1024
        while len(data_bytes) < response_length:
            b = self.socket.recv(response_length - len(data_bytes))
            data_bytes += b
        response = data_bytes.decode("utf-8").strip()

        if response == "No":
            print(f"The file named '{filename}' is not present in the store.")
        if response == "Yes":
            print("Client waiting for download to begin")
            data_bytes = b''
            response_length = 1024
            while len(data_bytes) < response_length:
                b = self.socket.recv(response_length - len(data_bytes))
                data_bytes += b
            response = data_bytes.decode("utf-8").strip()
            filesize = int(response)
            bytes_remaining = filesize
            new_filename = ""
            while len(new_filename) == 0:
                new_filename = input("Save As: ")
            path = f"{pathlib.Path.cwd()}{os.path.sep}downloads{os.path.sep}{new_filename}"
            buffer_size = 4096
            print(f"Recieving file {filename} as {new_filename}")
            with open(path, "wb") as file:
                count = 1
                while bytes_remaining > 0:
                    print(f"Packet {count} is being recieved")
                    if bytes_remaining < buffer_size:
                        dataBytes = b''
                        while len(dataBytes) < bytes_remaining:
                            recieved = self.socket.recv(
                                bytes_remaining - len(dataBytes))
                            dataBytes += recieved
                        data = dataBytes
                        file.write(data)
                        break
                    dataBytes = b''
                    while len(dataBytes) < buffer_size:
                        recieved = self.socket.recv(
                            buffer_size - len(dataBytes))
                        dataBytes += recieved
                    data = dataBytes
                    file.write(data)
                    bytes_remaining -= buffer_size
                    count += 1
            print("Download Complete : ", filename)

    def dir(self):
        request = str(("dir", self.assigned_id))
        request_length = bytes(str(len(request)).ljust(1024), "utf-8")
        self.socket.sendall(request_length)
        self.socket.sendall(bytes(request, "utf-8"))

        response_length = int(self.socket.recv(1024).decode("utf-8").strip())
        data_bytes = b''
        while len(data_bytes) < response_length:
            b = self.socket.recv(response_length - len(data_bytes))
            data_bytes += b
        response = data_bytes.decode("utf-8").strip()
        register = eval(response)
        for key, value in register.items():
            filename = key
            size = value
            print(f"{filename}: {size}")

    def quit(self):
        request = str(("quit", self.assigned_id))
        request_length = bytes(str(len(request)).ljust(1024), "utf-8")
        self.socket.sendall(request_length)
        self.socket.sendall(bytes(request, "utf-8"))

    def clear(self):
        if os.name == 'nt':
            os.system("cls")
        else:
            os.system("clear")


if __name__ == "__main__":
    with open("srv.cfg", "r") as file:
        data = file.read().strip()
        server_config = eval(data)
    sk_client = SKClient(server_config)
    sk_client.connect()
    sk_client.credentials_validation()

    if sk_client.autherized:
        while True:
            arguments = input(
                f"skclient {sk_client.socket.getsockname()}> ").split()
            if len(arguments) == 1:
                operation = arguments[0]
                if operation == "quit":
                    sk_client.quit()
                    break
                elif operation == "dir":
                    sk_client.dir()
                elif operation == "clear":
                    sk_client.clear()
                elif operation == "help":
                    print(
                        "_____________________________________________________________________________________\n| Operation | Arguments     | Functionality                                         |\n-------------------------------------------------------------------------------------\n|    help   |    [-----]    |           the basic manual for commands               |\n|   clear   |    [-----]    |             clears the client screen                  |\n|    get    |  [file_name]  | downloads the file with file_name if present in store |\n|    dir    |    [-----]    |       list all the files present in the store.        |\n|   quit    |    [-----]    |                  Shutdown the client                  |\n-------------------------------------------------------------------------------------\n")
                else:
                    print(f"Invalid input: {operation}")
                    continue
            elif len(arguments) == 2:
                operation = arguments[0]
                filename = arguments[1]
                if operation == "get":
                    sk_client.get(filename)
            else:
                print(f"Invalid input: {arguments}")
                continue
    else:
        print("Invalid Username or Password")
    sk_client.close()
