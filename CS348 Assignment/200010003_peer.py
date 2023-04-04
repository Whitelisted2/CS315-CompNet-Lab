from socket import *
from threading import *
import os
import re
import numpy as np
import time

server_tuple = ("0.0.0.0", 7902)
peer_addr = ""
sender_peer_port = -1
UDPSocket = socket(AF_INET, SOCK_DGRAM)
user_list = []
lock_user_list = Semaphore(1)
FRAG_SIZE = 1024
fragments = {}
lock_fragments = Semaphore(1)
disconnected = False
shareable_files = [i for i in os.listdir("./files_to_send/") if os.path.isfile("./files_to_send/" + i)]

def req_file(file_nm):
    global fragments
    users_with_file = []
    file_size = -1
    fragments.clear()
    # print("asking for file: " + file_nm)
    
    for user_addr in user_list:
        sock = socket()
        if user_addr == (peer_addr, int(sender_peer_port)):
            continue
        sock.connect(user_addr)
        sock.send(str.encode("PRESENT|"+file_nm))               ### Q2.5(a)
        recv_buffer_size = 1024
        msg = sock.recv(recv_buffer_size).decode()

        if msg.split("|")[0] == "PRESENT":
            users_with_file.append(user_addr)
            file_size = int(msg.split("|")[1])
            
        sock.shutdown(SHUT_RDWR)
        sock.close()
    if file_size == -1 :
        print("File not present at any peer!")
        return
    
    num_users_with_file = len(users_with_file)
    print("File size: ", str(file_size))
    print("Users with this file: ", num_users_with_file)

    # # To check the file transfer, where one of the peers goes down during transfer
    time.sleep(16)
    
    # Threads to fetch fragments
    num_fragments = int(np.floor((file_size + FRAG_SIZE - 1) / FRAG_SIZE))
    fragment_threads = []
    for fragment_index in range(num_fragments):                             ### Q2.5(b)
        fragment_start = fragment_index * FRAG_SIZE
        fragment_end = min(fragment_start + FRAG_SIZE - 1, file_size - 1)
        
        curr_user = users_with_file[fragment_index % len(users_with_file)]

        other_users = []
        for i in users_with_file:
            if i != curr_user:
                other_users.append(i)
        fragment_thread = Thread(target=get_fragment, args=(curr_user, file_nm, fragment_start, fragment_end, other_users))
        fragment_threads.append(fragment_thread)

    # Combine the file fragments into a single file
    file_content = b''
    
    for thread in fragment_threads:
        thread.start()
    for thread in fragment_threads:
        thread.join()

    # handling some transmitting host going offline midway
    if None in fragments.values() :
        print("Error in file download .......")
        return
    
    for fragment_index in range(num_fragments):
        # start and end byte offsets for the file fragment
        fragment_start = fragment_index * FRAG_SIZE
        end1 = fragment_start + FRAG_SIZE - 1
        end2 = file_size - 1
        fragment_end = min(end1, end2)

        # case of diff peers
        for addr in users_with_file:
            fragment_key = str(file_nm) + "-" + str(fragment_start) + "-" + str(fragment_end) + "-" + str(addr[0]) + "-" + str(addr[1])
            if fragment_key in fragments.keys():
                file_content += fragments[fragment_key]
                break
    
    new_path = "./inbox/received_"
    with open(new_path + file_nm, "wb") as f:
        f.write(file_content)

def get_fragment(peer_addresses, file_name, fragment_start, fragment_end, all_other_users):
    
    curr_socket = socket(AF_INET, SOCK_STREAM)
    fragment_key = str(file_name) + "-" + str(fragment_start) + "-" + str(fragment_end) + "-" + str(peer_addresses[0]) + "-" + str(peer_addresses[1])
    request = f"GET|{file_name}|{fragment_start}|{fragment_end}"

    # Receive file fragment from the peer
    data_found = False
    timeout_t = 2
    try:
        curr_socket.connect(peer_addresses)         ### Q2.4(a)
        curr_socket.send(request.encode())
        curr_socket.settimeout(timeout_t)
        data = curr_socket.recv(FRAG_SIZE)
        data_found = True
    except error:                                   ### Q2.4(c)
        curr_socket.close()
        for another_user in all_other_users:
            other_socket = socket(AF_INET, SOCK_STREAM)
            other_socket.connect(another_user)
            request = f"GET|{file_name}|{fragment_start}|{fragment_end}"
            other_socket.send(request.encode())
            other_socket.settimeout(timeout_t)
            try:
                data = other_socket.recv(FRAG_SIZE)
                data_found = True
                fragment_key = str(file_name) + "-" + str(fragment_start) + "-" + str(fragment_end) + "-" + str(another_user[0]) + "-" + str(another_user[1])
                break
            except timeout:
                other_socket.close()
                continue

    if not data_found:
        lock_fragments.acquire()
        fragments[fragment_key] = None
        lock_fragments.release()
        return "", b''
    
    file_fragment = b'' + data

    curr_socket.close()
    print("fragment info: " + fragment_key)
    
    lock_fragments.acquire()
    fragments[fragment_key] = file_fragment
    lock_fragments.release()

    return fragment_key, file_fragment


def handle_file_check():
    global shareable_files
    file_socket = socket(AF_INET, SOCK_STREAM)
    file_socket.bind((peer_addr, int(sender_peer_port)))
    file_socket.listen(15)

    while True:
        conn, _ = file_socket.accept()
        recv_buffer_size = 1024
        data = conn.recv(recv_buffer_size).decode()
        output = "ABSENT"
        curr_dir_str = "./files_to_send/"

        cmd_type = data.split("|")[0]
        filename = data.split("|")[1]
        if cmd_type == "PRESENT":
            shareable_files = []
            
            for i in os.listdir(curr_dir_str):                      ### Q2.2
                if os.path.isfile(curr_dir_str + i):
                    shareable_files.append(i)

            if filename in shareable_files:
                output = "PRESENT|" + str(os.path.getsize(curr_dir_str + filename))
            conn.send(str.encode(output))
            conn.close()
            continue

        elif cmd_type == "GET":
            # Parse the fragment start and end byte offsets
            fragment_start = int(data.split("|")[2])
            fragment_end = int(data.split("|")[3])

            # Read the requested file fragment from disk
            with open(curr_dir_str + filename, "rb") as file:
                file.seek(fragment_start)
                num_bytes = fragment_end - fragment_start + 1
                fragment_content = file.read(num_bytes)

            # Send the file fragment to the client
            conn.sendall(fragment_content)

def broadcast_onUpdate():
    global user_list
    while True:
        recv_buffer_size = 1024
        msg, server_addr = UDPSocket.recvfrom(recv_buffer_size)
        if server_addr[1] == 7903:
            if msg.decode() == "you_up?":
                UDPSocket.sendto(str.encode("up_and_running"), server_addr)
                continue
        if not disconnected:
            users = []
            broadcast_list = re.findall("(\'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\', [0-9]+)", msg.decode())
            for ipTuple in broadcast_list:
                portnum = ipTuple.split(", ")[1]
                portnum = int(portnum)
                ipaddr = re.findall("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ipTuple)
                ipaddr = ipaddr[0]
                users.append((ipaddr, portnum))
            lock_user_list.acquire()
            user_list = users.copy()
            # print("UserList", user_list)
            lock_user_list.release()
        else:
            print(msg.decode())
            break

if __name__ == "__main__":

    peer_addr = input("Enter a valid IP address: ")
    sender_peer_port = input("Enter a valid port number (3000-65535): ")
 
    bytesToGo = str.encode("connect|" + peer_addr + "|" + sender_peer_port) ### Q2.1(a)
    UDPSocket.sendto(bytesToGo, server_tuple)

    newUserDaemon = True
    new_users = Thread(target=broadcast_onUpdate)                           ### Q2.1(b) occurs in the target function of this
    new_users.setDaemon(newUserDaemon)
    new_users.start()

    
    reqFileDaemon = True
    file_req_handler = Thread(target=handle_file_check)                     ### Q2.4(b) is handled by virtue of the threading done here
    file_req_handler.setDaemon(reqFileDaemon)
    file_req_handler.start()


    while True:
        cmd = input("Enter command (h for help): ")
        if cmd == "h":
            print("+---------------+------------------------------------------+")
            print("| Command       | Use                                      |")
            print("+---------------+------------------------------------------+")
            print("| list_peers    | Lists all online peers                   |")
            print("+---------------+------------------------------------------+")
            print("| req_file      | Takes filename as input, gets if present |")
            print("+---------------+------------------------------------------+")
            print("| quit          | Quit; Terminate this Peer                |")
            print("+---------------+------------------------------------------+")
        elif cmd == "req_file":
            file_nm = input("Please enter the file name: ")
            req_file_to_peer = Thread(target=req_file, args=(file_nm,))
            req_file_to_peer.setDaemon(True)
            req_file_to_peer.start()
            req_file_to_peer.join()
        elif cmd == "quit":
            break
        elif cmd == "list_peers":
            lock_user_list.acquire()
            print(user_list)
            lock_user_list.release()
        else:
            print("Invalid Command!!!!")
    disconnected = True
    bytesToGo = str.encode("disconnect")                                ### Q2.3
    UDPSocket.sendto(bytesToGo, server_tuple)
