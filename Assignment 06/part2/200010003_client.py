from socket import *
import random

def client():

    num = random.randint(1, 100)                    # generate random number between 1 and 100
    hostname = gethostname()                        # get host name
    port = 7902                                     # set server's socket port number
    client_socket = socket(AF_INET, SOCK_STREAM)    # create a socket of type TCP
    client_socket.connect((hostname, port))         # connect to the server

    payload = str(hostname) + " " + str(num)        # join the reqd payload together
    print("Client Number = " + str(num))
    client_socket.send(payload.encode())            # send the payload

    data = client_socket.recv(1024).decode()        # receive server message

    # IMPORTANT: the assignment does not say what the client should do after it receives message from the server.
    # If we were to do something with the message, code for the same would be here.

    client_socket.close()                           # close the connection


if __name__ == '__main__':
    client()