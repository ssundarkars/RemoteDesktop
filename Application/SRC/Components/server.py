import socket
import time
from threading import *
import pyautogui as auto
from pynput.mouse import Listener


class ConnectionClosed(Exception):
    def __init__(self,message):
        super().__init__(message)
        
class MouseEvents(Thread):
    def __init__(self,name,clt):
        super().__init__()
        self.clt=clt
        self.name=name
    def run(self):
        print(self.name)
        with Listener(on_click=self.onClickListner) as listener:
            listener.join()
    def onClickListner(self,*args):
        self.clt.send(bytes(f'mouseEvents {args[0]} {args[1]} {str(args[-2]).split()[-1]} {args[-1]}','utf-8'))   


class Comunication(Thread):
    def __init__(self,machine,con):
        super().__init__(name=machine)
        self.con=con
        self.machine=machine
        self._stop_event=Event()
    def stop(self):
        print('Terminating ',self.name)
        self._stop_event.set()


    def stopped(self):
        return self._stop_event.is_set()

    def run(self) -> None:
        try:
            while True:
                if self.machine=='sender':
                    point=auto.position()
                    self.con.send(bytes(f'{point.x},{point.y}','utf-8'))
                    time.sleep(.2)
                elif self.machine=='reciever':
                    buffer=b''
                    try:
                        imgSize=int(self.con.recv(1048576).decode())
                    except:
                        continue
                    size=0
                    while size<imgSize:
                        buffer+=self.con.recv(1048576)
                        size=len(buffer)
                    
                    if buffer:
                        img=open('stream.png','wb+')
                        img.write(buffer)
                        img.close()
                else:
                    raise ConnectionClosed('Connection has been closed by client')
        except:
            try:
                self.con.send(bytes('exit','utf-8'))
            except:
                self.con.close()
         


def startScreen(start,clt,sender,reciever):
    if not start:
        start=(True if input('Type "start" to start Screenshare: ').lower()=='start' else False)
        if start:
            clt.send(bytes('True','utf-8'))
            print('Starting Screenshare...')
            time.sleep(.3)
            sender.start()
            reciever.start()
        else:
            startScreen(False)
    return start
def instructor(instruction,clt,sender,reciever):
    print(*instruction,sep="\n")
    start=input('Press instructions key or type "stop" to close Screenshare: ' ).lower()
    if start>'0' and start<'9':
        if int(start)<9 and int(start)>0:
            clt.send(bytes(f'instruction {instruction[int(start)-1]}','utf-8'))
        else:print('!!! Invalid instruction !!!')
        instructor(instruction,clt,sender,reciever)
    else:
        clt.send(bytes('False','utf-8'))
        print('Stopping Screenshare...')
        sender.stop()
        reciever.stop()
        clt.close()

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine=socket.gethostname()
server.bind(('127.0.0.1',36106))                #This machines IP address
server.listen(1)
clt,addr=server.accept()
print('Connection Stablished with, ',clt)
sender=Comunication('sender',clt)
reciever=Comunication('reciever',clt)
clickMngr=MouseEvents('clickManager',clt)
start=startScreen(False,clt,sender,reciever)
clickMngr.start()
instruction=["1: LiftUp","2: Down","3: MoveRight","4: MoveLeft",'5: Slow','6: Accelerate',"7: Move-Forward","8: Move-Backward"]
instructor(instruction,clt,sender,reciever)