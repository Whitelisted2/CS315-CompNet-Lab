from socket import *
from time import *

clientSocket = socket(AF_INET, SOCK_DGRAM) # UDP is used
server_addr = ("localhost", 12000)
clientSocket.settimeout(1) # assume packet loss if delay > 1s

try:
    tRTT = 0
    succ = 0
    for i in range(1, 11):
        start = time()
        message = "Ping " + str(i) + " " + ctime(start)
        try:
            # For Q3.1:
            sent = clientSocket.sendto(message.encode(), server_addr)
            print("Sent " + message)

            # For Q3.2:
            data, server = clientSocket.recvfrom(4096)
            print("Received " + data.decode())

            # For Q3.3:
            end = time()
            RTTv = end - start
            print("RTT: " + str(RTTv) + " seconds\n")
            tRTT += RTTv
            succ += 1

        except:
            # For Q3.4:
            print("Ping " + str(i) + " Request Timed out\n")
    print("Average RTT = ", RTTv/succ)

finally:
    print("Closing Socket ... ")
    clientSocket.close()