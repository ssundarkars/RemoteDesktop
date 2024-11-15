import socket
from threading import *
import time
import pyautogui as auto



class ConnectionClosed(Exception): 
    def __init__(self,message):
        super().__init__(message)

class Comunication(Thread):
    def __init__(self,machine,con):
        super().__init__(name=machine)
        self.con=con
        self.machine=machine
        self.cursor=[]


    def run(self) -> None:
        pre=0
        
            
        while True:

            if self.machine=='sender':
                img=auto.screenshot()
                self.con.send(bytes(f'{img.size}','utf-8'))
                time.sleep(.2)
                self.con.sendall(img)

            elif self.machine=='reciever':
                try:
                    data=str(self.con.recv(1024).decode())
                    if data=='False' or data=='exit':
                        break
                    elif data.startswith('instruction'):
                        print(f'Performing {data.split()[2]}.....')

                    elif data.startswith('mouseEvent'):
                        _,x,y,click,status=map(str,data.split())
                        if click=='Button.left':
                            if status=='True':
                                auto.mouseDown(int(x),int(y),button='left')
                            else:
                                auto.mouseUp(int(x),int(y),button='left') 
                        elif click=='Button.middle':
                            if status=='True':
                                auto.mouseDown(int(x),int(y),button='middle')
                            else:
                                auto.mouseUp(int(x),int(y),button='middle')
                        elif click=='Button.right':
                            if status=='True':
                                auto.mouseDown(int(x),int(y),button='right')
                            else:
                                auto.mouseUp(int(x),int(y),button='right')
                        print(data)
                    else:
                        try:
                            x,y=data.split(',')
                            auto.moveTo(int(x),int(y))
                        except:
                            pass
                        

                except Exception as e:
                    print(e,'75')

    

if __name__=='__main__':
    client= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(('127.0.0.1',30008))            #server's IP address required 
    reciever=Comunication('reciever',client)
    sender=Comunication('sender',client)
    start=str(client.recv(1024).decode())
    if start=='True':
        sender.start()
        reciever.start()
    
