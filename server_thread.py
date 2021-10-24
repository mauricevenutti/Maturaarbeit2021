import functions, threading, copy, socket
from time import sleep
class Server(threading.Thread):

    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"
    start_message_for_alice = "go"

    def __init__(self, header, port, server):
        threading.Thread.__init__(self)
        self.HEADER = header
        self.PORT = port
        self.SERVER = server
        self.ADDR = (server, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.connections = []
        self.lock = threading.Lock()
        #print("[STARTING] server is starting...")


    def handle_client(self,conn, addr):
        #print(f"[NEW CONNECTON] {addr} conencted")
        connected = True

        while connected:
            #get message
            msg_length = conn.recv(self.HEADER).decode('utf-8')
            if msg_length:  # the connection-message will be some kind of blank message
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode('utf-8')

            #    print(f"[{addr}] {msg}")
                if msg == Server.DISCONNECT_MESSAGE:
                    if len(self.connections) == 3:
                        try:
                            self.connections[-1].send(Server.DISCONNECT_MESSAGE.encode(Server.FORMAT))
                        except:
                            print(self.connections)
                    connected = False
                else:
                    #sendmsg(conn, msg)
                    for c in self.connections:
                        if c is conn:
                            continue
                        try:
                            c.send(msg.encode(Server.FORMAT))
                        except:
                            print(msg)
            else:
                continue
        conn.close()
        self.connections.remove(conn)

    def run(self):
        self.server.listen() #server starts listening
        #print(f"[LISTENING] Server is listening on {self.SERVER}")

        while len(self.connections)<3:

            conn, addr = self.server.accept() #blocking line, wait for new connection,addr stores address, conn stores object
            self.connections.append(conn)

            threading.Thread(target= self.handle_client, args=(conn, addr)).start() #start thread, handle client

            #print(f"[ACTIVE CONNECTIONS] {len(self.connections)}")

        self.connections[0].send(Server.start_message_for_alice.encode(Server.FORMAT)) #alice muss als erstes verbinden? Problem später lösen


