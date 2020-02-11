# Non-replicated-Blockchain
"Non-replicated" simplistic blockchain model demonstrating 'mutually exclusive access' using Lamport's protocol.

Python 2.7.12 -- No external dependecies.

To run in terminal: (each instruction in new terminal window) 
  1. python blockchain_server.py  # will creat a centralized blockchain server in one window
  2. python network_server.py # will create a network server to keep track of clients in the system
  3. python handle_client_interactive # one per client; this will allow client to put transaction requests interactively

  
handle_client_interactive.py will creat a new process to take of communication in the network and execute transaction on blockchain server by obtaining mutualy exclusive access using Lamport's distributed protocol.
