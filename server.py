import sys,socket,threading
from random import randint
MAX_CLIENTS = 20
MSG_LEN = 1024

class group_class:
    # groups = []
    def __init__(self):
        self.__groups = {}

    def add_user_in_group(self, groupname, username):
        if groupname not in self.__groups:
            self.__groups[groupname] = {
                'users':{
                    username: USERS.get_ip_port(username)
                },
                'encrypt_key':randint(1,9999)
            }
        else:
            self.__groups[groupname]["users"][username]=USERS.get_ip_port(username)
        for user in self.__groups[groupname]['users']:
            print(user)

    def get_group(self, groupname):
        return self.__groups[groupname]
    
    def get_group_key(self,groupname):
        return self.__groups[groupname]["encrypt_key"]
    
    def get_group_list(self):
        groups =""
        for group in self.__groups:
            groups=groups+group+"\n"
        return groups
    
    def group_exist(self,groupname):
        return groupname in self.__groups
    def user_in_group(self,groupname,username):
        if groupname in self.__groups:
            return username in self.__groups[groupname]["users"]
        else:
            return False
    def get_group_members(self,groupname):
        
        group_members = ""
        for user in self.__groups[groupname]["users"]:
            group_members+=self.__groups[groupname]["users"][user]+" "
        return group_members
class user_class:

    def __init__(self):
        self.__users = {}

    def add_user(self, username, password, user_ip, user_port, active):
        self.__users[username] = {
            'password': password,
            'user_ip': user_ip,
            'user_port': user_port,  #str type
            'active' : active
        }
    def get_user(self, username):
        return self.__users[username]
    
    def in_dict(self, username):
        return username in self.__users

    def check_passwd(self, username, password):
        return self.__users[username]['password'] == password
    
    def update_user(self, username, ip, port):
        self.__users[username]['user_ip']= ip
        self.__users[username]['user_port']=port

    def change_status(self, username):
        self.__users[username]['active'] = (self.__users[username]['active'] == False)

    def get_ip_port(self, username):
        return str(self.__users[username]['user_ip']+':'+self.__users[username]['user_port'])
    

USERS = user_class()
GROUPS= group_class()     
def command_processing(command):
    command = command.split(" ")
    if(command[0] == "SIGNUP"):
        #SIGNUP USERNAME PASSWD IP_PORT
        if(len(command) != 4):
            return "INVALID COMMAND"
        if(USERS.in_dict(command[1])):
            return "USERNAME ALREADY EXIST"
        USERS.add_user(command[1],command[2],command[3].split(":")[0],command[3].split(":")[1],False)
        print(USERS.get_user(command[1]))
        return "SIGN UP SUCCESSFUL"
    elif (command[0] == "SIGNIN"):
        if(len(command) != 4):
            return "INVALID COMMAND"
        if(not USERS.in_dict(command[1])):
            return "USERNAME DOES NOT EXIST"
        else:
            if(not USERS.check_passwd(command[1], command[2])):
                return "INCORRECT PASSWORD"
            else:
                USERS.update_user(command[1],command[3].split(":")[0],command[3].split(":")[1] )
                USERS.change_status(command[1])
                print(USERS.get_user(command[1]))
                return "LOGIN SUCCESSFUL"
    elif (command[0]== "SEND"):
        if(len(command) <= 2):
            return "MESSAGE CANNOT BE EMPTY"
        if(not USERS.in_dict(command[1])):
            return "USERNAME DOES NOT EXIST"
        else:
            return "TRUE " + USERS.get_ip_port(command[1])
    elif(command[0]== "SEND_FILE"):
        if(len(command) <= 2):
            return "MESSAGE CANNOT BE EMPTY"
        if(not USERS.in_dict(command[1])):
            return "USERNAME DOES NOT EXIST"
        else:
            return "TRUE " + USERS.get_ip_port(command[1])
    elif(command[0]== "SEND_GROUP" or command[0]== "SEND_GROUP_FILE" ):
        
        if(len(command) <= 3):
            return "MESSAGE CANNOT BE EMPTY"
        groupname = command[1]
        username = command[-1]
        print(groupname+" " + username)
        if(not GROUPS.group_exist(groupname)):
            return "GROUP DOES NOT EXIST"
        else:
            if(not GROUPS.user_in_group(groupname,username)):
                return "USER NOT IN THE GROUP"
            else:
                group_key = GROUPS.get_group_key(groupname)
                group_members=GROUPS.get_group_members(groupname)
                return "TRUE "+str(group_key)+" " + group_members
    elif(command[0]== "CREATE_GROUP"):
        # CREATE_GROUP GROUPNAME USERNAME
        if(len(command) != 3):
            return "INVALID FORMAT"
        
        groupname = command[1]
        username = command[2]
        if(GROUPS.group_exist(groupname)):
            return "GROUP ALREADY EXISTS: USE JOIN GROUP"
        else:
            GROUPS.add_user_in_group(groupname,username)
            return "GROUP CREATED"
    elif(command[0]== "JOIN_GROUP"):
        # JOIN_GROUP GROUPNAME USERNAME
        if(len(command) != 3):
            return "INVALID FORMAT"
        
        groupname = command[1]
        username = command[2]
        if(GROUPS.user_in_group(groupname,username)):
            return "USER ALREADY IN GROUP"
        else:
            GROUPS.add_user_in_group(groupname,username)
            print(GROUPS)
            return "GROUP JOINED"
    elif(command[0]== "LIST_GROUP"):
        # LIST_GROUP 
        if(len(command) != 1):
            return "INVALID FORMAT"
        groups = GROUPS.get_group_list()
        if(groups == ""): groups = "NO GROUPS CURRENTLY AVAILABLE"        
        print(groups)
        return groups
    return "INVALID COMMAND"    



def server_log(socket, address):

    while True:
        command = socket.recv(MSG_LEN)
        print("Received command " + command.decode('utf8') )
        if(command.decode('utf8') == 'EXIT'):
            break
        reply = command_processing(command.decode('utf8'))
        # reply = "CONCERNED IP:PORT"
        socket.send(reply.encode('utf8'))
    socket.close()      

def main():
    if(len(sys.argv) != 2):
        print("INCORRECT ARGUMENTS")
        exit()
    arg = sys.argv[1].split(':')  #colon separated 
    ip, port = arg[0], int(arg[1]) 
    
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4, TCP
    serversocket.bind((ip, port))
    serversocket.listen(MAX_CLIENTS)

    while True:
        (clientsocket, address) = serversocket.accept()
        #thread with function  
        t1 = threading.Thread(target=server_log, args=(clientsocket,address, ))  
        t1.start()
          
    serversocket.close() 


if __name__ == "__main__":
    main()

# user_info {
#     "user_name": {
#         "pass": "abc",
#         "IP": "",
#         "port": "",
#         "active": true/false,
#         "groups": [group1, group2]
#     }
# }    
