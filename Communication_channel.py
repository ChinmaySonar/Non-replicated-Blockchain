import socket
import os
from multiprocessing import Process, Pipe
from time import sleep                    # to add delays for demonstration
import signal 
#from handle_client_interactive import *
import time
import math
import random


def server_message_format(server_msg):
    server_msg = server_msg[1:-1]    
    l = len(server_msg)
    number = int(math.ceil(l/22.0))
    clients_list = []
    for i in range(number):
        address = server_msg[:20]
        address = address[1:-1]
        ip = address[1:10]
        port = int(address[13:])
        clients_list.append((ip,port))
        if i < (number-1):
            server_msg = server_msg[22:]
    return clients_list




############# different version for now ##################

def communication(child_conn):
    # Create a TCP/IP socket for listening
    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    my_listen_address = None
    while True:
        port = random.randint(10001,65000)
        try:
            #print "trying to bind to", data_man_port
            sock_listen.bind(("localhost", port))
            my_listen_address = ("localhost", port)
            print("my_address: {}".format(my_listen_address))
            break
        except socket.error as err:
            if err.errno == 98:  # address already in use
                port = random.randint(10001, 65000)
                continue
            else:
                raise
    
    # this sock is sock_connect which'll be one time use per send communication
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ("localhost", 10000)
    print('connecting to {} port {}'.format(*server_address))

    # block_chain server address
    bc_address = ("localhost", 19000)

    # Registering connection with co-ordinate server 
    sock.connect(server_address)
    
    sock.sendall("connecting  {}".format(str([my_listen_address])))    
    #sock.sendall(str(my_listen_address))    

    data = sock.recv(2000)    #data contains information about all the connected servers
    
    print("Data from coordinator: ", data)    
    #child_conn.send(data)
    
    client_list = server_message_format(data) # this is for information of child
    print("Current clients in the network: ", client_list)
        
    
    print('START closing socket with co-ordinate')
    sock.close()

    
    #Queue (we'll maintein a sorted list here)  blue_print -- (local_lamport, pid, request_text) for all requests (own + others)
    queue = []
    
    #my_pid
    my_pid = os.getpid()    

    #while loop between listening to parent and taking messages from other clients for Lamport
    local_clock = 0

    ########### new to network connection -- notify everyone else ############
    print("Notifying all others that I'm in network too")
    for i in client_list:
        if i == my_listen_address:
            continue # break should also work
        else:
            print("Notifying: {}", i)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(i)
            sock.sendall("4  {}".format([my_listen_address]))
            #queue = []
            #queue_status = sock.recv(2000) ## may need to do some string processing here (take care while sending; send in a single doubly spaced string)  --- maybe done
            #queue_list = queue_status.strip().split("  ")            
            #for i in range(0, len(queue_list), 3):
            #    queue.append((int(queue_list[i]), int(queue_list[i+1]), queue_list[i+2])) 
            sock.close()
    
    all_replies = False
    number_of_replies = 0

    # while loop to iterate between network messages and requests from the user (parent process messages)
    while True:
        try:
            sock_listen.settimeout(0.2) # timeout for listening
            sock_listen.listen(1)
            connection, client_address = sock_listen.accept()
        except socket.timeout:
            pass
            if child_conn.poll():
                request = child_conn.recv()
                print("[Communication Client] Received and enqueued the request from client: ", request)
                local_clock += 1
                print("Local clock: ", local_clock)
                if request[0] == '4': #quit request
                    break
                    
                queue.append((local_clock, my_pid, request)) # bal or tran. request
                
                if len(client_list) == 1:
                    # received mutually exclusive access
                    time.sleep(3)
                    print("Received mutually exclusive access")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    query_bc = queue[0][2] + ' ' + 'localhost' + ' ' + str(my_listen_address[1]) #single spaced                        
                    sock.connect(bc_address)
                    sock.sendall(query_bc)
                    reply_bc = sock.recv(2000)
                    #print("reply_bc: ", reply_bc)
                    sock.close()
                    time.sleep(2)
                    local_clock += 1
                    print("Local clock: ", local_clock)
                    # no need to send release messages
                    queue = []
                    child_conn.send(reply_bc)
                        
                for i in client_list:
                    if i == my_listen_address:
                        continue
                    else: # sending request message to everyone
                        time.sleep(1)
                        print("Sending request message to {}", i)
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect(i)
                        sock.sendall("1  {}  {}  {}  {}".format(my_pid, local_clock, [my_listen_address], request))
                        sock.close()             
            continue        
        #except:
        #    raise
        else:
            #connection established
            
            try:
                network_message = connection.recv(2000)
                
                if network_message[0] == '1': # request
                    message_list = network_message.split("  ")
                    connection.close()                    
                    print("Received request message: ", message_list)
                    local_clock = max(local_clock, int(message_list[2]))+1  # Local lamport clock update
                    time.sleep(1)
                    print("Local clock: ", local_clock)
                    queue.append((int(message_list[2]), int(message_list[1]), message_list[-1]))
                    queue = sorted(queue)
                    print("queue: ", queue)
                    
                    reply_queue = '2    {}    {}    '.format(local_clock, [my_listen_address])
                    for i in queue:
                        reply_queue += str(i[0]) + "   " + str(i[1]) + "   " + i[2] + "   "  # triple spaced
                    # new connection for reply
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    requester_address = server_message_format(message_list[-2])                    
                    sock.connect(requester_address[0])
                    # adding delays for presentation
                    time.sleep(5)
                    sock.sendall(reply_queue)
                    print("Sent reply message")
                    sock.close()
    
                elif network_message[0] == '2': #reply                      
                    message_list = network_message.split("    ")
                    #print("Received reply message: ", message_list)
                    local_clock = max(local_clock, int(message_list[1]))+1  
                    time.sleep(1)
                    print("Local clock: ", local_clock)
                    connection.close()
                    if len(message_list) > 3:
                        print("Received reply from {}".format(message_list[2]))
                        
                        
                        queue = []
                        list_receive_queue = message_list[3].strip().split("   ")
                        #print("list_receive_queue: ", list_receive_queue)
                        for i in range(0,len(list_receive_queue),3):
                            queue.append((int(list_receive_queue[i]), int(list_receive_queue[i+1]), list_receive_queue[i+2]))
                    number_of_replies += 1
                    if number_of_replies == (len(client_list)-1): # checking for all replies condition
                        all_replies = True
                        number_of_replies = 0
                                                            
                    if all_replies and queue[0][1] == my_pid: # condition of mutual exclusion
                        time.sleep(5)
                        print("Received mutually exclusive access {}".format(my_listen_address))
                        print("Printing current queue: ",queue)
                        
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        query_bc = queue[0][2] + ' ' + 'localhost' + ' ' + str(my_listen_address[1]) #single spaced                        
                        sock.connect(bc_address)
                        sock.sendall(query_bc)
                        reply_bc = sock.recv(2000)
                        print("Heard back from Blockchain server")
                        sock.close()
                        all_replies = False
                        local_clock += 1
                        print("Local clock: ", local_clock)
                        # send release messages to all others
                        queue = queue[1:] 
                        rel_message = "3  {}".format(local_clock)
                        for i in client_list:
                            if i == my_listen_address:
                                continue
                            else: 
                                time.sleep(2)
                                print("Sending release message to {}", i)
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect(i)
                                sock.sendall(rel_message)
                                sock.close()   
                        child_conn.send(reply_bc)                     


                elif network_message[0] == '3': #release
                    message_list = network_message.split("  ")
                    print("Received release message: ", message_list)
                    #clock_list = message_list[1].split(" ")
                    #piggybacked_clock = int(clock_list[1])
                    local_clock = max(local_clock,  int(message_list[1]))+1
                    time.sleep(1) 
                    print("Local clock: ", local_clock) 
                    queue = queue[1:]
                    connection.close()
                    if all_replies and queue[0][1] == my_pid: # condition of mutual exclusion
                        time.sleep(5)
                        print("Received mutually exclusive access {}".format(my_listen_address))
                        print("Printing current queue: ",queue)
                        # need to slightly modify bc -- can't use pid's.. using sock_listen  (DONE)
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        query_bc = queue[0][2] + ' ' + 'localhost' + ' ' + str(my_listen_address[1])                        
                        sock.connect(bc_address)
                        sock.sendall(query_bc)
                        reply_bc = sock.recv()
                        print("Heard back from Blockchain server")
                        sock.close()
                        all_replies = False
                        local_clock += 1
                        print("Local clock: ", local_clock)
                        # send release messages to all others 
                        rel_message = "3  {}".format(local_clock)                        
                        for i in client_list:
                            if i == my_listen_address:
                                continue
                            else: 
                                time.sleep(2)
                                print("Sending release message to {}", i)
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect(i)
                                sock.sendall(rel_message)
                                print("Release message: ", rel_message)
                                sock.close()
                        child_conn.send(reply_bc)                        

                elif network_message[0] == '4': #new client
                    message_list = network_message.split("  ")
                    str_to_list = server_message_format(message_list[1])
                    client_list.append(str_to_list[0])
                    #s = ''
                    #for j in queue:
                    #    s += str(j[0])
                    #    s += "  "
                    #    s += str(j[1])
                    #    s += "  "
                    #    s += j[2]
                    #connection.sendall(s)
                    connection.close()
            finally:
                pass
   

    # de-registrering from server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    try:

        #send
        message_close = 'close'

        sock.sendall(message_close)

    finally:
        print('CLOSING socket with co-ordinate')
        sock.close() 
    sock_listen.close() # closing listen socket manually
    return True

