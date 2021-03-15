This program is simple chat program made by python 3.x

You should run the server first, than client
The server can hold total 20 clients
It works completly in localhost network,
but this program may not run if the server and client is conneted with internet.
However, it may be possible in running same network(LAN)

Command list
---------------------------
Server

/ls : list the roomlist

/kill [roomname] : destroy the room that has named [roomname]

/exit : shutdown server and end program

~~~~~~~~~~~~~~
Client
The client can only chat when the client is in the chatroom

/ls : list the roomlist

/create [roomname] : Create the room named [roomname], and the nickname will become 'host'

/join [roomname] [nickname] : join the room having nickname

/whisper [nickname] (msg) : send whisper message to [nickname]

/exit : if client is in the chatroom, exit the chatroom, if not, end program



