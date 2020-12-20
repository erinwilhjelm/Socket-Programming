import socket
import select
import sys
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import hmac
## python3 UnencryptedIM.py -s <portnum> | -c hostname <portnum>
args = sys.argv

def toBytes(s):
    return bytearray([ord(c) for c in s])

def pad(message):
    length = 16 - (len(message) % 16)
    message += bytes([length])*length
    return message

def unpad(message):
    message = message[:-message[-1]]
    return message

def encrypt(plaintext, confkey, authkey):
    iv = Random.new().read(16)
    plaintext = pad(str.encode(plaintext))
    hmac = hmacGenerator(plaintext, authkey)
    encryptor = AES.new(confkey, AES.MODE_CBC, iv)
    ciphertext = iv + encryptor.encrypt(hmac + plaintext)
    return ciphertext

def decrypt(ciphertext, confkey, authkey):
    iv = ciphertext[:16]
    decryptor = AES.new(confkey, AES.MODE_CBC, iv)
    plaintext = decryptor.decrypt(ciphertext[16:])
    padded = plaintext[16:]
    compute_hmac = hmacGenerator(padded, authkey)
    if compute_hmac != plaintext[:16]:
        print("unauthenticated")
        exit(1)
    return unpad(padded)

def hmacGenerator(message,authkey):
    hmacc = hmac.new(authkey,pad(message), hashlib.sha1).digest()

    return hmacc[:16]

## server side
if args[1] == '-s':

    if len(args) < 7:
        port = 9999
        confkey = hashlib.sha1(toBytes(args[3])).digest()[:16]
        authkey = hashlib.sha1(toBytes(args[5])).digest()[:16]
    else:
        port = int(args[2])
        confkey = hashlib.sha1(toBytes(args[4])).digest()[:16]
        authkey = hashlib.sha1(toBytes(args[6])).digest()[:16]

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
               message = socks.recv(2048)
               if not message:
                   print("unauthenticated")
                   exit(1)
               else:
                   plaintext = decrypt(message, confkey, authkey)
                   print(plaintext.decode())
            # user is sending a message
            elif socks == sys.stdin:
                message = sys.stdin.readline()
                ciphertext = encrypt(message, confkey, authkey)
                conn.sendall(ciphertext)

    conn.close()
# client side
elif args[1] == '-c':

    if len(args) < 8:
        port = 9999
        confkey = hashlib.sha1(toBytes(args[4])).digest()[:16]
        authkey = hashlib.sha1(toBytes(args[6])).digest()[:16]
    else:
        port = int(args[3])
        confkey = hashlib.sha1(toBytes(args[5])).digest()[:16]
        authkey = hashlib.sha1(toBytes(args[7])).digest()[:16]
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
                if not message:
                   print("unauthenticated")
                   exit(1)
                else:
                    plaintext = decrypt(message, confkey, authkey)
                    print(plaintext.decode())
            # user is sending a message
            elif socks == sys.stdin:
                message = sys.stdin.readline()
                ciphertext = encrypt(message, confkey, authkey)
                server.sendall(ciphertext)

    server.close()



