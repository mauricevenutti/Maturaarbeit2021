from functions import Functions as f, Variables, Testing as t
import socket, threading, copy
from time import sleep
from random import randint
from server_thread import Server

#import server as s #variables from server
import sys
sys.setrecursionlimit(2000)
#testing

class Client(threading.Thread):
    bs_list = []
    errors_from_reconciliation_detected = 0

    advantage_begin_messagae = "ADVANTAGE BEGIN"
    reconciliation_begin_message = "RECONCILIATION BEGIN"

    def __init__(self,bitstream,  header = 64, port = 5050, server = socket.gethostbyname(socket.gethostname())):
        threading.Thread.__init__(self)
        self.bitstream = bitstream
        self.HEADER = header
        self.PORT = port
        self.SERVER = server
        self.ADDR = (server, port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()


    def run(self):
        self.lock.acquire()
        self.client.connect(self.ADDR)
        self.lock.release()
        lst = []
        while True:
            msg = self.listen()
            lst.append(msg)
            if msg == Server.DISCONNECT_MESSAGE:
                self.send(Server.DISCONNECT_MESSAGE)
                break



    def send(self, msg):
        message = msg.encode('utf-8')  # messages need to be sent in bits
        msg_length = len(message)
        send_length = str(msg_length).encode('utf-8')
        # the first message we're gonna send is send_length, now we need to make sure that this is HEADER long (pad)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

    def listen(self):
        return self.client.recv(3000).decode('utf-8')




class Alice(Client):

    def run(self):
        self.lock.acquire()
        self.client.connect(self.ADDR)
        self.lock.release()

        t.initial_alice = list(map(int, list(self.bitstream)))

        if self.listen() == Server.start_message_for_alice:

            self.bitstream = self.advantage_Destillation(list(map(int, list(self.bitstream))), Variables.ADVANTAGE_ROUNDS)
            print("finish advantage")
            self.bitstream = self.information_Reconciliation(self.bitstream, Variables.RECONCILIATION_ROUNDS)
            print("finsih reco")
        self.send(Server.DISCONNECT_MESSAGE)

    def advantage_Destillation(self, bitstream, rounds):

        self.lock.acquire()
        self.send(Client.advantage_begin_messagae)
        self.lock.release()
        lst = []
        for i in range(0, len(bitstream), 2):
            lst.append(f.parity_check(bitstream[i], bitstream[i + 1]))
        #testing
        t.parities_alice.append(lst)

        i_lst = 0
        i_bitstream = 0
        while i_lst < len(lst):
            self.lock.acquire()
            self.send(str(lst[i_lst]))
            self.lock.release()
            if int(self.listen()) == 1:
                del bitstream[i_bitstream + 1]
                i_bitstream += 1
            else:
                del bitstream[i_bitstream: i_bitstream + 2]
            i_lst += 1
        #testing
        t.advantage_alice.append(copy.copy(bitstream))
        #testing
        if rounds > 1:
            if len(bitstream)%2 == 0:
                return self.advantage_Destillation(bitstream, rounds-1)
            else:
                return self.advantage_Destillation((bitstream[0:-1]), rounds -1)

        self.lock.acquire()
        self.send("ADVANTAGE END")
        self.lock.release()
        return bitstream

    def information_Reconciliation(self, bitstream, k):
        self.lock.acquire()
        self.send(Client.reconciliation_begin_message)
        self.lock.release()

        while k > 0:
            #create substring
            a = randint(0,len(bitstream))
            b = randint(0,len(bitstream))
            while a == b:
                b = randint(0,len(bitstream))
            if a > b:
                sub = bitstream[b:a+1]
                pos = (b,a)
            else:
                sub = bitstream[a:b+1]
                pos = (a,b)

            self.lock.acquire()
            self.send(str(pos[0]))
            sleep(0.001)
            self.send(str(pos[1]))
            sleep(0.001)
            self.lock.release()

            #testing
            t.positions_reco.append(pos)
            #parity
            parity = f.parity(sub)
            self.lock.acquire()
            self.send(str(parity))
            self.lock.release()
            #listen and recursion
            if int(self.listen()) == 0: #there's a mistake 0 = False
                position = self.reco_recursion(sub,pos)
                #testing
                t.detected_positions_reco.append(position)

            k = k-1
        t.reco_alice.append(copy.copy(bitstream))
        return bitstream

    def reco_recursion(self, lst, pos ):
        if len(lst) == 1:
            return pos[0]

        s1 = lst[0:len(lst) // 2]
        s2 = lst[len(lst) // 2: len(lst)]
        self.lock.acquire()
        self.send(str(f.parity(s1)))
        self.lock.release()
        if int(self.listen()) == 0: #mistake is in s1
            return self.reco_recursion(s1, (pos[0],pos[0] + len(s1)-1))
        else:
            return self.reco_recursion(s2, (pos[0]+len(s1), pos[1]))



class Bob(Client):

    def run(self):
        self.lock.acquire()
        self.client.connect(self.ADDR)
        self.lock.release()
        t.initial_bob = list(map(int, list(self.bitstream)))

        if self.listen()== Client.advantage_begin_messagae:
            self.bitstream = self.advantage_Destillation(list(map(int, list(self.bitstream))))

        if self.listen() == Client.reconciliation_begin_message:
            self.bitstream = self.information_Reconciliation(self.bitstream, Variables.RECONCILIATION_ROUNDS)

        self.send(Server.DISCONNECT_MESSAGE)


    def information_Reconciliation(self, bitstream, k):
        if k == 0:
            t.reco_bob.append(copy.copy(bitstream))
            return bitstream
        a = int(self.listen())
        b = int(self.listen())

        pos = (a,b)
        sub = bitstream[pos[0]:pos[1]+1]

        if int(self.listen()) == f.parity(sub):
            self.lock.acquire()
            self.send("1")
            self.lock.release()
        else:
            self.lock.acquire()
            self.send("0")
            self.lock.release()

            position = self.reco_recursion(sub, pos)

            bitstream[position] = 0 if bitstream[position] == 1 else 1 #error correction by Bob

        return self.information_Reconciliation(bitstream, k-1)


    def reco_recursion(self, lst, pos ):
        #print(f"pos: {pos}")
        if len(lst) == 1:
            return pos[0]

        s1 = lst[0:len(lst) // 2]
        s2 = lst[len(lst) // 2: len(lst)]

        if int(self.listen()) != f.parity(s1): #mistake is in s1
            self.lock.acquire()
            self.send("0")
            self.lock.release()
            return self.reco_recursion(s1, (pos[0],pos[0] + len(s1)-1))
        else:
            self.lock.acquire()
            self.send("1")
            self.lock.release()
            return self.reco_recursion(s2, (pos[0]+len(s1), pos[1]))

    def advantage_Destillation(self, bitstream):
        lst = []
        for i in range(0, len(bitstream), 2):
            lst.append(f.parity_check(bitstream[i], bitstream[i + 1]))
        t.parities_bob.append(copy.copy(lst))
        i_lst = 0
        i_bitstream = 0
        while i_lst < len(lst):

            if int(self.listen()) == lst[i_lst]:
                del bitstream[i_bitstream + 1]
                self.lock.acquire()
                self.send("1")
                self.lock.release()
                i_bitstream += 1

            else:
                del bitstream[i_bitstream: i_bitstream + 2]
                self.lock.acquire()
                self.send("0")
                self.lock.release()
            i_lst += 1

        #testing
        t.advantage_bob.append(copy.copy(bitstream))
        #testing end
        msg = self.listen()
        if msg == Client.advantage_begin_messagae:
            if len(bitstream)%2 == 0:
                return self.advantage_Destillation(bitstream)
            else:
                return self.advantage_Destillation(bitstream[0:-1])
        return bitstream


