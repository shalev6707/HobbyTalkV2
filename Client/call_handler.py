from vidstream import *


import threading

receiver = AudioReceiver('19',9999)
receive_thread = threading.Thread(target=receiver.start_server())

sender = AudioSender('192.168.1.125',5555)
        


