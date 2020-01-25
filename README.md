# Non-replicated-Blockchain
"Non-replicated" simplistic blockchain model demonstrating 'mutually exclusive access' using Lamport's protocol.

No external dependecies. Code only uses basic python libraries.

To run in terminal: (each instruction in new terminal window) 
  python blockchain_server.py  # will creat a centralized blockchain server in one window
  python network_server.py # will create a network server to keep track of clients in the system
  python handle_client_interactive # one per client; this will allow client to put transaction requests interactively

  
handle_client_interactive.py will creat a new process to take of communication in the network and execute transaction on blockchain server by obtaining mutualy exclusive access using Lamport's distributed protocol.
