import socket
import select 
import sys

## python3 UnencryptedIM.py -s <portnum> | -c hostname <portnum>


args = sys.argv

## server side
if args[1] == '-s':

    # if no port provided, default to 9999
    if len(args) < 3:
        port = 9999
    else: 
        port = int(args[2])
    ## print("Server side")

    sock = socket.socket()
    ## overcome the "Address already in use"
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ##bind to IP with port
    sock.bind(('', port))
    sock.listen(10)
    conn, addr = sock.accept()

    while True:

         # list of possible input streams 
        sockets_list = [sys.stdin, conn]
        (read_sockets,_,_) = select.select(sockets_list,[],[])

        for socks in read_sockets:
            # user is receiving message
            if socks == conn: 
                message = conn.recv(2048)
                print(message.decode())
                sys.stdout.flush()
            # user is sending a message
            elif socks == sys.stdin:
                # read input and send
                message = sys.stdin.readline()
                conn.sendall(message.encode())
    conn.close()

# client side
elif args[1] == '-c':

    # if no port provided, default to 9999
    if len(args) < 4:
        port = 9999
    else: 
        port = int(args[3])

    server = socket.socket()
    server.connect((args[2], port))
    
    while True:
        # list of possible input streams 
        sockets_list = [sys.stdin, server]
        (read_sockets,_,_) = select.select(sockets_list,[],[])

        for socks in read_sockets:
            # user is receiving a message
            if socks == server:
                message = socks.recv(2048)
                print(message.decode())
            # user is sending a message  
            elif socks == sys.stdin:
                message = sys.stdin.readline()
                server.sendall(message.encode()) 
                
    server.close()
