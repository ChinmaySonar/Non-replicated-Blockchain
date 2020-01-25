
import socket
import os
from multiprocessing import Process
from time import sleep                    # to add delays for demonstration
import signal                             # for SIGCHILD (know when child terminates)
import math
import time
import random

blockchain = []

# sender = ('ip', port)
# receiver = ('ip', port)

class Blockchain_element(object):
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount


#id for each node is their listen address

def print_bc(bc):
    for i in bc:
        print("sender: ", i.sender, " receiver: ", i.receiver, " amount: ", i.amount)
    

#balance code 1
def balance(client_address):
    bal = 10
    for i in blockchain:
        if i.sender == client_address:
            bal -= i.amount
        elif i.receiver == client_address:
            bal += i.amount
        else:
            continue
    print("Current Blockchain: ")
    print_bc(blockchain)
    s = '1 {}'.format(bal)    
    return bal


# transfer code 2
def transfer(sender, receiver, amount):
    sender_balance_before = balance(sender)
    print("sender before:", sender_balance_before)
    #sender_balance_before = sender_balance_before.split(" ")
    #print("sender balance before: ", int(sender_balance_before[1]))
    if sender_balance_before < amount:
        sender_balance_after = sender_balance_before # no change in sender's balance
        s = "0 {} {}".format(sender_balance_before, sender_balance_after)
        print("Current Blockchain: ")
        print_bc(blockchain)        
        return(s) # 0 represents transaction status fail    
    else:
        print("Entered Success condition: ")
        bc_element = Blockchain_element(sender, receiver, amount) # may have to make some changes in data types and signatures for sender and receiver
        blockchain.append(bc_element)
        sender_balance_after = sender_balance_before - amount
        s = "1 {} {}".format(sender_balance_before, sender_balance_after) 
        print("Current Blockchain: ")
        print_bc(blockchain)       
        return(s) # 1 represents transaction status success 
    # need to return invalid transaction and balance

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port 19000 
server_address = ('localhost', 19000)
sock.bind(server_address)

print('Starting up Blockchain on {} port {}'.format(*server_address))

# need to continuosly listen on the network and process requests


while True:
    sock.listen(1)
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        query = connection.recv(1000)  
         
        
        if int(query[0]) == 1:
            l = query.split(" ")
            cl_address = ('localhost', int(l[-1]))
            response = str(balance(cl_address))
            connection.sendall(response) # query already has string
        
        #int of data == 2
        else:
            l = query.split(" ")  
            sender = ('localhost', int(l[-1]))
            receiver = (str(l[1]), int(l[2])) # ('ip',port) pair
            amount = int(l[3])
            response = transfer(sender, receiver, amount)
            connection.sendall(response)
        

    finally:
        # Clean up the connection
        print("Closing current connection")
        connection.close()
    
