
from TCP_client import*


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



############# Actions #####################

# part for pipe communication between parent process

parent_conn, child_conn = Pipe()
child_process  = Process(target = communication, args=(child_conn,))


child_process.start()
time.sleep(10)


def print_menu(d):
    print "Menu:"
    for item, itemnum in sorted(d.items(), key=lambda x: x[1]):
        print "{}: {}".format(itemnum, item)


#menu1 = {"Balance": 1, "Transfer": 2, "User Log": 3, "Disconnect": 4}
menu1 = {"Balance": 1, "Transfer": 2, "Disconnect": 4}
menu2 = {"Wait for logs": 1, "Register another transaction": 2}


# part for continuous while loop to iterate over user input / communication pipe signals

def handle_client_interactive(parent_conn):
    # first character in query message to child conveys information to child about query type
    while True:
        print_menu(menu1)
        user_command = int(raw_input("Your option: "))
        #(Transfer)        
        if user_command == 2:
            #asking for receiver id and amount
            # if no transactions in the blockchain for this server, still bc will return 10 since person is on initial balance
            print("Following input is space sensitive")
            receiver_id = raw_input("Enter receiver id:") #input ip address without quotes + " " + portnumber, input is whitespace sensitive
            amount = raw_input("Enter amount:")
            query_string = "2 "+ receiver_id + " " + amount
            # send query through network and wait
            parent_conn.send(query_string)
            print("Parent sent the query string: ", query_string)
            while True:
                response = parent_conn.recv()
                if response == '':
                    continue
                else:
                    print("Response from BC: ", response)
                    l = response.split(" ")
                    if int(response[0]) == '0':
                        print("Transaction failed :(, not enough balance")
                        print("Balance: {}".format(l[1]))
                    else:
                        print("Transaction Successful")
                        print("Balance before: {}, Balance_after: {}".format(l[1],l[2]))
                    break
                
            
        elif user_command == 1:
            query_string = str(1)
            # send query through network and wait
            parent_conn.send(query_string)
            print("Parent sent the query string: ", query_string)
            while True:
                #response = parent_conn.recv()
                #if response == '':
                #    continue
                if parent_conn.poll():
                    #print('I am here')
                    response = parent_conn.recv()
                    print(response)
                    break
                else:
                    continue
                #else:
                #    response = parent_conn.recv()
                #    print(response)
                #    break
        elif user_command == 4:
            print("Disconnecting the server")
            query_string = str(4)
            parent_conn.send(query_string)
            print("Parent sent the query string: ", query_string)
            break        
        
        else:
            print("Invalid command :(, please try again")
            continue

handle_client_interactive(parent_conn)

child_process.join()

