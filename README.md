## IIITH-Whatsapp
***

### About the Project
IIIH-Whatsapp, a Multi-client chat application with an end-to-end encrypted messaging system. In this, one can chat to indivisual peer, or can chat in a group. He can also send different types of files to peers. All the messaging and files are Triple DES(3DES) encrypted with key generation through Diffie-Hellman key exchange Algo.

### Pre-requisites
1. Python compiler (prefereably python3) should be installed on the machine.
2. Create a 'Downloads' folder, before running any send file command in the same folder where client.py is present.

### Libraries Used
Below are the libraries that are in the project and some are need to be installed first on the system before running the program:-
1. sys
2. socket
3. threading
4. random
5. os
6. hashlib
7. pyDes - pip install pyDes
8. pyDH - pip install pyDH
9. des (DesKey) - pip install des 
(for python then pip ... , if python3 then pip3 ...)


### Features/Commands Implemented
1. SIGNUP <_username_> <_password_>		  	: Need to signup first before working
2. SIGNIN <_username_> <_password_>		 	: first login into any user
3. SEND <_username_> <_message_>		  	: to send message to indivisual
4. SEND_FILE <_username_> <_filepath_>	  		: to send file to an indivisual
5. CREATE_GROUP <_groupname_>			    	: to create a group
6. JOIN_GROUP <_groupname_>		 		: to join particular group
7. LIST_GROUP				  		: to list all the groups existing
8. SEND_GROUP <_groupname_> <_message_>	  		: to send a message in a group
9. SEND_GROUP_FILE <_groupname_> <_filepath_> 		: to send a file in a group

* Error Handling done throughout the system
* It is an Object-Oriented system

### How to run the application-
1. Open multiple terminals where both the files(server.py and client.py) are stored.
2. On one terminal, run server.py by:
	$ python3 server.py <server_ip:server_port>
3. On other terminals, run client.py by:
	$ python3 client.py <server_ip:server_port> <client's_ip:client's_port>
4. Now run the above commands and enjoy our Whatsapp!

