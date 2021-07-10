import sys,socket,threading,os,pyDes,hashlib,pyDH
from des import DesKey
MAX_CLIENTS = 20
buffer_size = 4096
MSG_LEN = 4096
key_flag=False
file_flag=False
shared_key=""

def tripleDes_encrypt(key,value):
    data = str.encode(value)
    k = pyDes.triple_des(str.encode(key), pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    return d

def tripleDes_decrypt(key,value):
    data = value
    k = pyDes.triple_des(str.encode(key), pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.decrypt(data)
    return d

def tripleDes_encrypt_file(key,value):
    key0 = DesKey(key.encode())
    d=key0.encrypt(value, padding=True)
    return d

def tripleDes_decrypt_file(key,value):
    key0 = DesKey(key.encode())
    d=key0.decrypt(value, padding=True)
    return d


def generate_key(key):
    d = hashlib.sha1(str.encode(key))
    return (d.hexdigest()[0:24])


def keyExachange(to_ip,to_port):
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    temp_socket.connect((to_ip, to_port))
    d1 = pyDH.DiffieHellman()
    d1_pubkey = d1.gen_public_key()
    key_message="#KEY:"+str(d1_pubkey)
    temp_socket.send(str(key_message).encode())
    message=temp_socket.recv(buffer_size)
    d1_sharedkey = d1.gen_shared_key(int((message.decode())))
    key=generate_key("{}".format(d1_sharedkey))
    temp_socket.close()
    return key
def groupkeyExachange(to_ip,to_port,groupkey):
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    temp_socket.connect((to_ip, to_port))
    # d1 = pyDH.DiffieHellman()
    # d1_pubkey = d1.gen_public_key()
    key_message="#GROUP_KEY:"+str(groupkey)
    temp_socket.send(str(key_message).encode())
    # message=temp_socket.recv(buffer_size)
    # d1_sharedkey = d1.gen_shared_key(int((message.decode())))
    key=generate_key("{}".format(groupkey))
    temp_socket.close()
    # print("sending to ",to_ip,to_port ,key)
    return key

def groupfilekeyExachange(to_ip,to_port,groupkey):
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    temp_socket.connect((to_ip, to_port))
    # d1 = pyDH.DiffieHellman()
    # d1_pubkey = d1.gen_public_key()
    key_message="#GROUP_FILE_KEY:"+str(groupkey)
    temp_socket.send(str(key_message).encode())
    # message=temp_socket.recv(buffer_size)
    # d1_sharedkey = d1.gen_shared_key(int((message.decode())))
    key=generate_key("{}".format(groupkey))
    temp_socket.close()
    print("sending to ",to_ip,to_port ,key)
    return key



def send_file(socket, file_path,to_ip,to_port,key_encrypt): #SEND_FILE U ~/Desktop/IIITH
    try:
        # with open(file_path, 'rb') as fd
        fd = open(file_path, 'rb')
    except FileNotFoundError:
        print("ERROR IN FILE PATH")
        socket.close()
        return
    
    with fd:
        # key_encrypt=keyExachange(to_ip,to_port)
        c = fd.read(buffer_size)
        count=0
        while(c):
            encrypted_data=tripleDes_encrypt_file(key_encrypt,c)
            socket.send(encrypted_data)
            print("PROCESSING CHUNK NO.",count)
            count=count+1
            c = fd.read(buffer_size)
        fd.close()
    socket.close()

def server_log(socket, address):

    # while True:
    message = socket.recv(MSG_LEN)
    global key_flag,shared_key
    # my name is shiv
    # SEND_FILE:filename
    if(key_flag==True):
        if(len(message)%8 != 0):
            print(len(message))
            return
        message=tripleDes_decrypt(shared_key,message)
    if(message.decode().split(':')[0] == "SEND_FILE"):                      #SEND_FILE:FILENAME
        file_path = './Downloads/' + message.decode().split(':')[1]
        print("Recieving file at", file_path)
        
        fd = open(file_path,"wb")
        fd.close()
        l = socket.recv(buffer_size+8)
        count=0
        fd = open(file_path,"wb")
        while(l):
            decrypt_data=tripleDes_decrypt_file(shared_key,l)                                        
            fd.write(decrypt_data)
            print("RECEIVING CHUNK NO. ",count)                                                     
            count=count+1
            l = socket.recv(buffer_size+8)
        fd.close()
        print("FILE DOWNLOADED AT " + file_path)
        key_flag=False
        shared_key=""
    elif (message.decode().split(':')[0] == "#KEY"):          # At B
        public_key_r=int(message.decode().split(':')[1])
        d2 = pyDH.DiffieHellman()
        d2_pubkey = d2.gen_public_key()
        socket.send(str(d2_pubkey).encode())
        d2_sharedkey = d2.gen_shared_key(public_key_r)
        key=generate_key("{}".format(d2_sharedkey))
        key_flag=True
        shared_key=key
        #print("public key recieved")
    elif (message.decode().split(':')[0] == "#GROUP_FILE_KEY"):          # At B
        group_key=int(message.decode().split(':')[1])
        # d2 = pyDH.DiffieHellman()
        # d2_pubkey = d2.gen_public_key()
        # socket.send(str(d2_pubkey).encode())
        # d2_sharedkey = d2.gen_shared_key(public_key_r)
        key=generate_key("{}".format(group_key))
        # key_flag=True
        shared_key=key
        print("public key recieved",key)
    elif (message.decode().split(':')[0] == "#GROUP_KEY"):          # At B
        group_key=int(message.decode().split(':')[1])
        # d2 = pyDH.DiffieHellman()
        # d2_pubkey = d2.gen_public_key()
        # socket.send(str(d2_pubkey).encode())
        # d2_sharedkey = d2.gen_shared_key(public_key_r)
        key=generate_key("{}".format(group_key))
        key_flag=True
        shared_key=key
        print("public key recieved",key)

    else:
        print("Received message: " + message.decode() )
        key_flag=False
        shared_key=""
        #print("Received message: " + message.decode() )
   
    socket.close()    

def server_main(client_server_ip, client_server_port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    serversocket.bind((client_server_ip, client_server_port))
    serversocket.listen(MAX_CLIENTS)
    global key_flag,shared_key
    key_flag=False
    while True:
        (clientsocket, address) = serversocket.accept()
        #thread with function  
        t1 = threading.Thread(target=server_log, args=(clientsocket,address,))  
        t1.start()
          
    serversocket.close() 

def client_main(server_ip, server_port, client_server_ip, client_server_port):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    clientsocket.connect((server_ip,server_port))
    global key_flag,shared_key,file_flag
    key_flag=False
    file_flag=False
    signed_in = False
    username = ""
    while True:
        command = input() #str
        
        if(command.split(" ")[0] == "SIGNUP" or command.split(" ")[0] == "SIGNIN"):
            if(signed_in):
                print("A USER IS ALREADY SIGNED IN")
                continue
            command = command + " " + client_server_ip +":"+str(client_server_port)
            print('Command sending to server')
            clientsocket.send(command.encode())
            if(command == 'EXIT'):
                break
            reply_from_server = clientsocket.recv(MSG_LEN)
            if(reply_from_server.decode() == "LOGIN SUCCESSFUL"):
                signed_in = True
                username = command.split(" ")[1]
            print(reply_from_server.decode())
        
        elif(command.split(" ")[0] == "CREATE_GROUP" or command.split(" ")[0] == "JOIN_GROUP"):
            if(signed_in):
                
                if(len(command.split())!=2):
                    print("Invalid command")
                    continue
                
                command = command+" "+username
                clientsocket.send(command.encode())
                reply_from_server = clientsocket.recv(MSG_LEN)
                print(reply_from_server.decode())
            
            else:
                print("No user signed in")
                continue
        elif(command.split(" ")[0] == "LIST_GROUP"):
            if(signed_in):
                
                if(len(command.split())!=1):
                    print("Invalid command")
                    continue
                
                clientsocket.send(command.encode())
                reply_from_server = clientsocket.recv(MSG_LEN)
                print(reply_from_server.decode())
            
            else:
                print("No user signed in")
                continue
        
        elif(signed_in):
            print('Command sending to server')
            if (command.split(" ")[0] == "SEND_GROUP" or command.split(" ")[0] == "SEND_GROUP_FILE"):
                command+=" "+username
            
            clientsocket.send(command.encode())
            if(command == 'EXIT'):
                break
            reply_from_server = clientsocket.recv(1024)
            # print(command)
            # print(reply_from_server.decode())
            
            if(command.split(" ")[0] == "SEND" and reply_from_server.decode().split()[0] == "TRUE"):
                to_ip, to_port = reply_from_server.decode().split()[1].split(':')
                to_port = int(to_port)
                print(command.split(" ", 2)[2]) 
                key_shared_r=keyExachange(to_ip,to_port)
                temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
                temp_socket.connect((to_ip, to_port))
                # send to the other peer and recieve from it to create the shared key
                # encrypt the message
                encrypted_data=tripleDes_encrypt(key_shared_r,command.split(" ", 2)[2])
                #print("length of data",(encrypted_data))
                temp_socket.send(encrypted_data)
                # temp_socket.send("EXIT".encode())
                temp_socket.close()
                #print("key_flag resetted")
                key_flag=False
                shared_key=""
            
            
            elif(command.split(" ")[0] == "SEND_FILE" and reply_from_server.decode().split()[0] == "TRUE"):
                to_ip, to_port = reply_from_server.decode().split()[1].split(':')
                to_port = int(to_port)
                file_path = command.split(" ", 2)[2] 
                try:
                    fd = open(file_path, 'rb')
                except FileNotFoundError:
                    print("ERROR IN FILE PATH")
                    continue

                with fd:
                    fd.close()
                    file_name = file_path.split('/')[-1]
                    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
                    temp_socket.connect((to_ip, to_port))
                    temp_socket.send(("SEND_FILE:"+file_name).encode())
                    # send_file filename
                    file_flag=True
                    # key exchange
                    key_encrypt=keyExachange(to_ip,to_port)

                    temp_thread = threading.Thread(target=send_file, args=(temp_socket, file_path,to_ip,to_port, key_encrypt,))  
                    temp_thread.start()
                    key_flag=False
                    shared_key=""
                    file_flag=False
            
            
            elif(command.split(" ")[0] == "SEND_GROUP" and reply_from_server.decode().split()[0] == "TRUE"):
                # SEND_GROUP GROUPNAME MESSAGE 
                # TRUE IP:PORT IP:PORT
                group_members = reply_from_server.decode().split()[2:]
                group_key = reply_from_server.decode().split()[1]
                # encrypt_key = generate_key(group_key)
                # shared_key=encrypt_key
                # key_flag=True
                            
                for member in  group_members:
                    to_ip, to_port = member.split(':')
                    to_port = int(to_port)
                    if (to_ip , to_port) != (client_server_ip,client_server_port):
                        encrypt_key = groupkeyExachange(to_ip,to_port,group_key)

                        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
                        temp_socket.connect((to_ip, to_port))
                        print(command)
                        PARTS =command.split(" ")
                        i=2
                        message = ""
                        while i < (len(PARTS)-1):
                            message+=" " + PARTS[i]
                            i=i+1
                        print((to_ip , to_port),(server_ip,server_port))
                        print(message)
                        encrypted_data=tripleDes_encrypt(encrypt_key,message)
                        temp_socket.send(encrypted_data)
                        temp_socket.close()    
            
            elif(command.split(" ")[0] == "SEND_GROUP_FILE" and reply_from_server.decode().split()[0] == "TRUE"):
                group_members = reply_from_server.decode().split()[2:]
                group_key = reply_from_server.decode().split()[1]
                
                
                            
                for member in  group_members:
                    to_ip, to_port = member.split(':')
                    to_port = int(to_port)
                    if (to_ip , to_port) != (client_server_ip,client_server_port):
                        encrypt_key = groupfilekeyExachange(to_ip,to_port,group_key)
                        file_path = command.split()[2]
                        
                        # key_flag=True 
                        # print(file_path)
                        try:
                            fd = open(file_path, 'rb')
                        except FileNotFoundError:
                            print("ERROR IN FILE PATH")
                            continue

                        with fd:
                            fd.close()
                            file_name = file_path.split('/')[-1]
                            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
                            temp_socket.connect((to_ip, to_port))
                            temp_socket.send(("SEND_FILE:"+file_name).encode())
                            # send_file filename
                            temp_thread = threading.Thread(target=send_file, args=(temp_socket, file_path,to_ip,to_port, encrypt_key,))  
                            # temp_thread = threading.Thread(target=send_file, args=(temp_socket, file_path,encrypt_key, ))  
                            temp_thread.start()

                    shared_key = ""
                    key_flag=False            
            print(reply_from_server.decode())
                
        else:
            print("UNABLE TO PROCESS COMMAND")    
    clientsocket.close()    


def main():
    #python client.py serverip:port clientip:port

    if(len(sys.argv) != 3):
        print("INCORRECT ARGUMENTS")
        exit()
    arg = sys.argv[1].split(':')  # server's IP:PORT colon separated 
    server_ip, server_port = arg[0], int(arg[1]) 
    #clientip:port
    arg = sys.argv[2].split(':')  # client's IP:PORT colon separated 
    client_server_ip, client_server_port = arg[0], int(arg[1])
    
    t1 = threading.Thread(target=client_main, args=(server_ip,server_port,client_server_ip, client_server_port, ))  
    t2 = threading.Thread(target=server_main, args=(client_server_ip,client_server_port, ))
    
    t1.start()
    t2.start()
     


if __name__ == "__main__":
    main()

#NOTE: CLIENT SERVER NEEDS TO BE TESTED.
