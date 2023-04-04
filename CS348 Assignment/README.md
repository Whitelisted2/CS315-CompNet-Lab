### Description of Assignment 


#### Code Files
- 200010003_manager.py 
    - check_users(): This function regularly checks if users are running or not, and adjusts user_list as necessary.
    - manage_users(): If users send connect/disconnect requests, this function adjusts user_list as necessary.
- 200010003_peer.py
    - req_file(): This function handles the case where a peer requests a file from another peer, checking if the file is present at other peers or not. Threading is used to fetch fragments.
    - get_fragment(): If file is present, this function fetches the file in fragments. Fragment info is also printed.
    - handle_file_check(): This checks if file is present at the current peer device.
    - broadcast_onUpdate(): This notifies manager of the presence of current peer. Then, it populates the current peer's user_list.

#### Demo Instructions
- In one terminal, run `python3 200010003_manager.py`.
    - This tab will function like a network console
- In two other terminals, run `python3 200010003_peer.py`.
    - Follow the instructions, enter valid IP address and port number. An example set is (127.0.0.1, 45454).
    - Make sure the ordered pair is different for each terminal, for identification sake.
    - Follow instructions, use `h' to check possible commands, and request files as necessary
    - Note that file request success is contingent on some factors:
        - Another peer is available.
        - The requested file is available.
        - The requested-from peer doesn't go down during the file transfer.
- Use `Ctrl+C` to terminate the peers first, after operations are completed.
- Finally, terminate the manager with a kill signal by `Ctrl+C`.

#### Link To Demo Video

The demo video is available at https://drive.google.com/file/d/1pSZhWZXQqo3ggTcw6VpLLVgQa15_kPzU/view?usp=sharing

