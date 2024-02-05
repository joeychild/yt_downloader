#CLIENT.PY

import socket
import base64
 
csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
csFT.connect((input("enter host ip: "), 8756))
print("connected")

filename = csFT.recv(1024).decode()
csFT.send(filename.encode())
#Receive file
print("Receiving " + filename + "...")
fh = open('/storage/emulated/0/Documents/Pydroid3/playlist downloads/' + filename, "wb")
# sent = 0
while True:
    data = csFT.recv(102400)
    if not data:
            # print("not data")
            break 
        # sent += 1
        # print(f"Package {sent}: {len(data)} bytes")
    fh.write(base64.b64decode(data))
    csFT.send(b"Package received")
fh.close()
print("Received..")

 
csFT.close()
