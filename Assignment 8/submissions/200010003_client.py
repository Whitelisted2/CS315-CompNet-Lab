from socket import *
import ssl
from getpass import *
import base64
import sys

# Choose a mail server (e.g. Google mail server) and call it mailserver 
mailserver = ("smtp.gmail.com", 587)


# ############################ NOTE ############################
# Gmail requires the client to add TLS/SSL for authentication and security reasons, 
# before sending MAIL FROM command

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "220":
    print("220 Reply not received from server.")

# Send HELO command and print server response. 
heloCommand = "HELO Alice\r\n"
clientSocket.send(heloCommand.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "250":
    print("250 Reply not received from server.")

# Send request for TLS connection to mail server using socket
cmd = "STARTTLS\r\n"
clientSocket.send(cmd.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "220":
    print("220 Reply not received from server")
clientSocket = ssl.wrap_socket(clientSocket)

# Authentication details
print("Enter Authentication details of sender below:")
print("For default (smtplab23@gmail.com), hit [ENTER] for quick login.")
inputemail = input("Mail ID: ")
inputpwd = ""
if inputemail == "":
    inputemail = "smtplab23@gmail.com"
    inputpwd = "lmvgusmmhxkmzoti"
    print("Logging in ...")
else:
    inputpwd = getpass("Password: ")
    print("NOTE: If the entered ID doesn't have permissions for SMTP, then error may occur!")

# email = (base64.b64encode("smtplab23@gmail.com".encode()) + ("\r\n").encode())
email = (base64.b64encode(inputemail.encode()) + ("\r\n").encode())
password = (base64.b64encode(inputpwd.encode()) + ("\r\n").encode())

clientSocket.send("AUTH LOGIN\r\n".encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "334":
    print ("334 Reply not received from server")

clientSocket.send(email)
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "334":
    print ("334 Reply not received from server")
clientSocket.send(password)
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "235":
    print ("235 Reply not received from server")

# Send MAIL FROM command and print server response.
mailfrom = "MAIL FROM: <"+inputemail+">\r\n"
clientSocket.send(mailfrom.encode())
recv = clientSocket.recv(1024).decode()
if recv[:3] != "250":
    print ("250 Reply not received from server.")
    sys.exit(0)


# Send RCPT TO command and print server response.
recvid = "200010003@iitdh.ac.in"
inputrecvid = input("Enter recipient Email ID ([ENTER] for default): ")
if inputrecvid != "":
    recvid = inputrecvid
recvmsg = "RCPT TO: <"+recvid+">\r\n"
clientSocket.send(recvmsg.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "250":
    print ("250 Reply not received from server.")

# Send DATA command and print server response.
clientSocket.send("DATA\r\n".encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "354":
    print ("354 Reply not received from server.")

# Send message data.
subject = "Testing Testing 123"
inputsubject = input("Enter Email Subject ([ENTER] for default): ")
if inputsubject != "":
    subject = inputsubject
clientSocket.send(("Subject: "+subject+" \r\n").encode())
clientSocket.send(("To: "+recvid+" \r\n").encode())
msg = "\r\n "
inp = input("Enter Message: ")
msg = msg + inp
endmsg = "\r\n.\r\n"
clientSocket.send(msg.encode())

# Message ends with a single period.
clientSocket.send(endmsg.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "250":
    print("250 Reply not received from server.")

# Send QUIT command and get server response.
clientSocket.send("QUIT\r\n".encode())
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != "221":
    print("221 Reply not received from server.")

clientSocket.close()
print("Connection Closed ...")

