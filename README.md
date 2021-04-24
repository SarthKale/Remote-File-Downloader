# Remote File Downloader
A network-based desktop application. It downloads the various files present in the store from the server to the client's download folder directly. This application has features like authentication and authorization. It also has multi-client support.

## Working
It is a network-based application that works on a multi-threaded server. It stores users' credentials and uses them for authorization and authentication. The files stored in the folder named "store" gets directly transferred via byte stream to the folder named "downloads" at the client-side.

## How to run?
* Clone the repository
* Open the server folder in a terminal and different terminals for separate clients.
* In the server terminal, execute
> python3 server.py
* In the clients' terminals, execute
> python3 client.py

## Output Expectations
A CLI application in which the server continuously executes once it starts. The clients can download the files present in the server's store. 
The commands help, get, quit, clear, dir.
The 'help' command is the reference for all the available commands.
The 'get' command takes a file name as an argument and thus downloads from the store or give respective error responses.
The 'dir' command lists all the files available in the store.
The 'clear' command clears the terminal.
The 'quit' command terminates the program.

### Language
* **Programming Language : Python 3.8**
* **Version Control : Git**

### Author
_Sarthak Kale_