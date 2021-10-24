from functions import Functions as f, Variables as v, Testing as t
from server_thread import Server
from clients_thread import Alice, Bob, Client
import socket, threading, copy, time, hashlib




initial_alice = f.flaw_BS(copy.copy(v.flawless_random_Bitstream), v.BIT_ERROR_RATE_ALICE)
initial_bob = f.flaw_BS(copy.copy(v.flawless_random_Bitstream), v.BIT_ERROR_RATE_BOB)
initial_eve = f.flaw_BS(copy.copy(v.flawless_random_Bitstream), v.BIT_ERROR_RATE_EVE)
t.initial_eve = list(map(int, list(initial_eve)))

#create
server = Server(64, 5050, socket.gethostbyname(socket.gethostname()))
alice = Alice(initial_alice, 64,5050, socket.gethostbyname(socket.gethostname()))
bob = Bob(initial_bob, 64, 5050, socket.gethostbyname(socket.gethostname()))
eve = Client(initial_eve, 64, 5050, socket.gethostbyname(socket.gethostname()))

#start
server.start()
alice.start()
time.sleep(1) #fix
bob.start()
eve.start()

alice.join()
bob.join()
eve.join()

def testing():

    file = open('testing_output.txt', 'w')

    file.write(f"STREAM FROM THE SATELLITE" + '\n')
    file.write(str(t.flawless_stream) + '\n')
    file.write(f"STREAM ALICE" + '\n')
    file.write(str(t.initial_alice) + '\n')
    file.write(f"STREAM BOB" + '\n')
    file.write(str(t.initial_bob) + '\n')
    file.write(f"STREAM EVE" + '\n')
    file.write(str(t.initial_eve) + '\n')
    file.write('\n')
    file.write("INITIAL ERROR RATE: " + str(f.error_rate(t.initial_alice, t.initial_bob)[2]) +'\n')
    file.write("MISTAKES: " + str(f.error_rate(t.initial_alice, t.initial_bob)[0]) + '\n')
    file.write("OUT OF: " + str(f.error_rate(t.initial_alice, t.initial_bob)[1]) + '\n')
    file.write('\n')
    for i in range(v.ADVANTAGE_ROUNDS):

        file.write(f"ADVANTAGE DES ROUND {i+1}" + '\n')
        file.write(f"PARITY ALICE" + '\n')
        file.write(str(t.parities_alice[i]) + '\n')
        file.write(f"PARITY BOB" + '\n')
        file.write(str(t.parities_bob[i]) + '\n')
        file.write('\n')
        file.write(f"STREAM ALICE" + '\n')
        file.write(str(t.advantage_alice[i]) + '\n')
        file.write(f"STREAM BOB" + '\n')
        file.write(str(t.advantage_bob[i]) + '\n')
        file.write('\n')
        file.write("ERROR RATE AFTER ROUND " + str(i+1) +": "+ str(f.error_rate(t.advantage_alice[i], t.advantage_bob[i])[2]) + '\n')
        file.write("MISTAKES " + str(i + 1) + ": " + str(f.error_rate(t.advantage_alice[i], t.advantage_bob[i])[0]) + '\n')
        file.write("OUT OF " + str(i + 1) + ": " + str(f.error_rate(t.advantage_alice[i], t.advantage_bob[i])[1]) + '\n')
        file.write('\n')

    file.write('\n')
    file.write("AFTER RECONCILIATION" + '\n')
    file.write("RECO POSITIONS" + '\n')
    file.write(str(t.positions_reco) + '\n')
    file.write("DETECTED ERROR POS" + '\n')
    file.write(str(t.detected_positions_reco) + '\n')
    file.write('\n')
    file.write("STREAM ALICE" + '\n')
    file.write(str(t.reco_alice[0]) + '\n')
    file.write("STREAM BOB" + '\n')
    file.write(str(t.reco_bob[0]) + '\n')
    file.write('\n')
    file.write("ERROR RATE AFTER RECO: " + str(f.error_rate(t.reco_alice[0], t.reco_bob[0])[2]) + '\n')
    file.write("MISTAKES: " + str(f.error_rate(t.reco_alice[0], t.reco_bob[0])[0]) + '\n')
    file.write("OUT OF: " + str(f.error_rate(t.reco_alice[0], t.reco_bob[0])[1]) + '\n')
    file.write('\n')

    final_alice = ""
    alice_string = [str(int) for int in t.reco_alice[0]]
    final_alice= final_alice.join(alice_string)
    final_bob = ""
    bob_string = [str(int) for int in t.reco_bob[0]]
    final_bob = final_bob.join(bob_string)
    #hashing
    a = hashlib.new('SHA512')
    b = hashlib.new('SHA512')
    a.update(final_alice.encode('utf-8'))
    b.update(final_bob.encode('utf-8'))
    file.write("AFTER AMPLIFICATION" + '\n')
    file.write("KEY ALICE" + '\n')
    file.write(str(a.hexdigest()) + '\n')
    file.write("KEY BOB" + '\n')
    file.write(str(b.hexdigest()) + '\n')

    file.close()
    
    if final_alice != final_bob:
        print("NOT ENOUGH ROUNDS!")
        print(f"ERROR RATE = {str(f.error_rate(t.reco_alice[0], t.reco_bob[0])[2])}")
    
    print("KEY ALICE")
    print(str(a.hexdigest()))
    print("KEY BOB")
    print(str(b.hexdigest()))
testing()



