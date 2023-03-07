from socket import *
import sys

# run this server using python3 200010003_webserver.py
# use keyboard interrupt to close server

print(gethostbyname(gethostname()))
print("Type the above address with port 7902, to find the website.")
print("<address>:7902/HelloWorld.html")
server_socket = socket(AF_INET, SOCK_STREAM)    # tcp socket creation
serverPort = 7902                               # server port number
server_socket.bind(('',serverPort))             # binding the port to the socket
server_socket.listen(1)                         # Waiting for a request from client side
print("Ready to serve . . .")

while True:
    connectionSocket, addr = server_socket.accept()                      # Accepting client's request
    print("Request accepted from (address, port) tuple: %s" % (addr,))

    try:
        message = connectionSocket.recv(2048).decode()
        filename = message.split()[1]
        file = open(filename[1:], 'r')                  # filename from the request
        outputdata = file.read()
        print("Running. use keyboard interrupt to close server.")
        print("File found.")                            # Returns header line informing that the file was found
        headerLine = "HTTP/1.1 200 OK\r\n"              # keep HTTP OK in header
        connectionSocket.send(headerLine.encode())
        connectionSocket.send("\n".encode())

        # Sends the file back to client, encoded
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\n".encode())
        print("File sent.")
        continue

    except IOError: # exception : file not present in server.
        print("Warning: file not found. (or this is a stray displaying error.)")
        errHeader = "HTTP/1.1 404 Not Found\r\n" # error header
        connectionSocket.send(errHeader.encode())
        connectionSocket.send("\n".encode())
        f_err = open("error.html", 'r')  # Opens and sends the error page to the browser
        outputerr = f_err.read()
        for i in range(0, len(outputerr)):
            connectionSocket.send(outputerr[i].encode())

# terminate connection, close application
connectionSocket.close()
server_socket.close()
sys.exit()