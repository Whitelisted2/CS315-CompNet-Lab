from socket import *
import random

def server():

    hostname = gethostname()                        # get host name
    port = 7902                                     # set socket port number
    server_socket = socket(AF_INET, SOCK_STREAM)    # create a socket of type TCP
    server_socket.bind((hostname, port))            # bind host address, port
    server_socket.listen(5)                         # configure max number of concurrent clients 
    
    conn, addr = server_socket.accept()                # accept new connection
    while True:
        data = conn.recv(1024).decode()             # receive message
        if not data:
            break
        client_name, client_num = data.split(" ")
        client_num = int(client_num)

        if client_num > 100 or client_num < 1 :
            break

        print("Client Name: " + str(client_name) 
            #   + " with address: " + str(addr)
            )
        print("Server Name: " + str(hostname))

        num = random.randint(1, 100)                # generate random number between 1 and 100
        sum = num + client_num
        print("Client's Number = " + str(client_num))
        print("Server's Number = " + str(num))
        print("Sum = " + str(sum))

        message = str(hostname) + " " + str(num)
        conn.send(message.encode())                 # send data to the client

        # note that the value sent by client to server will never be out of the given range
        # so the server will never terminate, based on the currently given info.

    conn.close()                                    # close the connection


if __name__ == '__main__':
    server()