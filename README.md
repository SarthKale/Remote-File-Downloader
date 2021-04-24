# Remote File Downloader
This is a network based desktop application which can download the various files present in the store from the server to the client's download folder directly. This application has features like authentication and authorization. It also has multi-client support.

## Working
It is a network based application which works on multi-threaded server. It stores users' credentials and uses it for authorization and authentication. The files stored in the folder named "store" gets directly transfered via bytestream to the folder named "downloads" at the client-side.

## How to run?
* Clone the repository
* Open the server folder in a terminal and different terminals for separate clients.
* In the server terminal, execute....
> python3 server.py
* In the clients' terminals, execute....
> python3 client.py

## Output Expectations
This is a CLI application in which the server executes continueously once it starts. The clients can download the files present in the server's store. The user has few commands which are used to access the application.
The commands are help, get, quit, clear, dir.
The 'help' command is used as the reference for all the available commands.
The 'get' command takes file name as an argument and thus downloads from store or give respective error responses.
The 'dir' command lists all the files available in the store.
The 'clear' command clears the terminal.
The 'quit' command is used to terminate the program.

### Language
* **Programming Language : Python 3.8**
* **Version Control : Git**

### Author
_Sarthak Kale_