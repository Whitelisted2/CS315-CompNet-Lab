from socket import *
from threading import *
import time

port = 7902
server_addr = "0.0.0.0"
all_users = []
link_addrs_peers = {}
check_time = 10
sem_lock = Semaphore(1)
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_addr, port))
print("Server Address: " + server_addr + ":7902")


def manage_users():
    while True:                                         ### By virtue of this loop, Q1.1
        message, address = server_socket.recvfrom(1024)

        sem_lock.acquire()
        is_present = False
        if address in all_users:
            is_present = True
        if message.decode()[:10] == "disconnect":           ### Q1.4(a)
            if is_present:
                print("User Disconnected: ", link_addrs_peers[address])
                del link_addrs_peers[address]
                all_users.remove(address)
                server_socket.sendto(str.encode("Disconnected"), address)
            else:
                print("User", link_addrs_peers[address], " is offline :(")
           
                
        elif message.decode()[:7] == "connect":             ### Q1.2(a)
            if is_present:
                print("User", link_addrs_peers[address], "is online :)")
            else:
                ipaddr = message.decode().split("|")[1]
                portno = message.decode().split("|")[2]
                portno = int(portno)
                print("New User: ", (ipaddr, portno))
                all_users.append(address)
                link_addrs_peers[address] = (ipaddr, portno)

        for addr in all_users:                              ### Q1.2(b) and Q1.4(b)
            dict_to_list = str(list(link_addrs_peers.values()))
            server_socket.sendto(str.encode(dict_to_list), addr)

        sem_lock.release()


def check_users():
    checker_socket = socket(AF_INET, SOCK_DGRAM)
    checker_socket.bind(("0.0.0.0", 7903))
    print("Checker Server Address: 0.0.0.0:7903")
    while True:
        time.sleep(check_time)
        
        sem_lock.acquire()

        to_remove = []
        for addrs in all_users:
            try:
                timeout_t = 1
                checker_socket.sendto(str.encode("you_up?"), addrs) ### Q1.3(a)
                checker_socket.settimeout(timeout_t)
                msg, _ = checker_socket.recvfrom(1024)
                if msg.decode() != "up_and_running":                ### Q1.3(b)
                    to_remove.append(addrs)
                else:
                    pass
            except timeout:
                to_remove.append(addrs)
        
        for i in to_remove:
            all_users.remove(i)
            del link_addrs_peers[i]
        
        if len(to_remove) > 0:
            print("[NOTE: Some user missing, broadcasting new users' list]")
            for addr in all_users:
                dict_to_list = str(list(link_addrs_peers.values()))
                server_socket.sendto(str.encode(dict_to_list), addr) ### Q1.3(c)
        sem_lock.release()


if __name__ == "__main__":
    in_out_users = Thread(target=manage_users)
    in_out_users.start()
    verify_active_users = Thread(target=check_users)

    verify_active_users.start()
    
    
