# Import socket module
import socket

# Here we use localhost ip address
# and port number
LOCALHOST = "127.0.0.1"
PORT = 8080
# calling server socket method
server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)
server.bind((LOCALHOST, PORT))
server.listen(1)
print("Server started")
print("Waiting for client request..")
# Here server socket is ready for
# get input from the user
clientConnection, clientAddress = server.accept()
print("Connected client :", clientAddress)
msg = ''
# Running infinite loop
while True:
    data = clientConnection.recv(1024)
    msg = data.decode()
    if msg == 'Quit':
        print("Connection is Quit")
        clientConnection.close()
        break

    print("Equation is received")
    result = 0
    operation_list = msg.split()
    operand1 = operation_list[0]
    operation = operation_list[1]
    operand2 = operation_list[2]

    # here we change str to int conversion
    num1 = int(operand1)
    num2 = int(operand2)
    # Here we perform basic arithmetic operation
    if operation == "+":
        result = num1 + num2
    elif operation == "-":
        result = num1 - num2
    elif operation == "/":
        result = num1 / num2
    elif operation == "*":
        result = num1 * num2

    print("Send the result to client")
    # Here we change int to string and
    # after encode send the output to client
    output = str(result)
    clientConnection.send(output.encode())
clientConnection.close()
