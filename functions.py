import random, copy

class Functions:

    @staticmethod
    def create_rBS(n):
        lst = []
        for i in range(n):
            lst.append((random.getrandbits(1)))
        return lst

    @staticmethod
    def flaw_BS(lst, fq):
        for i in range(len(lst)):
            if random.random() < fq:
                lst[i] = int(not lst[i])
        msg = ""
        for i in lst:
            msg = msg + str(i)
        return msg

    @staticmethod
    def parity_check(a, b):
        if a + b == 1:
            return 1
        else:
            return 0


    @staticmethod
    def parity(lst):
        res = lambda lst: 0 if sum(lst) % 2 == 0 else 1
        return res(lst)

    @staticmethod
    def error_rate(lst1, lst2):
        f = 0
        for i in range(len(lst1)):
            if lst1[i] != lst2[i]:
                f += 1
        return [f, len(lst1), f/len(lst1)]

class Variables():
    #varibales
    print("ERROR RATE ALICE (0<0.5):")
    BIT_ERROR_RATE_ALICE = float(input())
    print("ERROR RATE BOB (0<0.5):")
    BIT_ERROR_RATE_BOB = float(input())
    print("ERROR RATE EVE (0<0.5):")
    BIT_ERROR_RATE_EVE = float(input())
    print("NUMBER OF ADVANTAGE DISTILLATION ROUNDS:")
    ADVANTAGE_ROUNDS = int(input())
    print("NUMBER OF INFORMATION RECONCILIATION ROUNDS:")
    RECONCILIATION_ROUNDS = int(input())
    print("LENGTH OF THE SATELLITE STREAM")
    flawless_random_Bitstream = Functions.create_rBS(int(input()))

class Testing():
    flawless_stream = Variables.flawless_random_Bitstream
    initial_alice = []
    initial_bob = []
    initial_eve = []

    parities_alice = []
    parities_bob = []

    advantage_alice = []
    advantage_bob = []

    positions_reco = []
    detected_positions_reco = []
    reco_alice = []
    reco_bob = []
