import socket
import json
import os
import subprocess
import tkinter
from tkinter import *
from tkinter import messagebox
from Func import *
from functools import partial
from PIL import Image

FORMAT = "utf8"
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Client:
    def __init__(self):
        HOST = '127.0.0.1'  # The server's hostname or IP address
        PORT = 65432        # The port used by the server
        # Create a TCP/IP socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (HOST, PORT)
        print('connecting to %s port ' + str(server_address))
        self.client.connect(server_address)

    def receive_msg(self):
        data = self.client.recv(1024).decode(FORMAT)
        print("Server: " + data)
        return data

    def send_msg(self, msg):
        self.client.sendall(bytes(msg, "utf8"))
    
    def send_file(self,filename):
        # get the file size
        filesize = os.path.getsize(filename)
        # send the filename and filesize
        self.client.send(f"{filename}{SEPARATOR}{filesize}".encode())
        # start sending the file
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                self.client.sendall(bytes_read)
            
    def receive_file(self):
        # receive the file infos
        # receive using client socket, not server socket
        received = self.client.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        format = filename.split("_")
        _filename = "client_" + format[1]
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        with open(_filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.client.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
        return _filename
    
    def first_UI(self):
        print("\n1. Sign up\n2. Sign in\n3. Exit")
        option = input("Choose option: ")
        self.send_msg(option)
        if option == "1":
            self.sign_up()
            self.second_UI()
        elif option == '2':
            self.sign_in()
            self.second_UI()
        elif option == '3':
            print("Closing socket")
    
    def second_UI(self):
        print("\n1. View note\n2. Create note\n3. Exit")
        option = input("Choose option: ")
        self.send_msg(option)
        if option == "1":
            self.view_list_note()
        elif option == '2':
            self.create_note()
            #self.first_UI()
        elif option == '3':
            self.first_UI()
    
    def third_UI(self):
        print("\n1. View image\n2. Download image\n3. Exit\n")
        option = input("Choose option: ")
        self.send_msg(option)
        if option == "1":
            self.view_image()
            #self.second_UI()
        elif option == '2':
            self.download()
            #self.second_UI()
        elif option == '3':
            self.second_UI()
    
    def fourth_UI(self):
        print("\n1. View note\n2. Download file\n2. Exit\n")
        option = input("Choose option: ")
        self.send_msg(option)
        if option == "1":
            self.view_note()
            #self.second_UI()
        elif option == '2':
            self.download()
            #self.second_UI()
        elif option == '3':
            self.second_UI()

    def sign_up(self):  
        _name = input("User name: ")
        _pass = input("Password: ")
        #send info 
        self.send_msg(_name)
        self.send_msg(_pass)
        #receive msg from Server
        check = self.receive_msg()
        if check == "False":
            print("Account is exist or size is smaller than required size.")
            self.first_UI()
        else:
            print("Successfully registered.")
    
    def sign_in(self):
        _name = input("User name: ")
        _pass = input("Password: ")
        #send info 
        self.send_msg(_name)
        self.send_msg(_pass)
        #receive msg from Server
        check = self.receive_msg()
        if check == "False":
            print("Username or password is wrong.")
            self.first_UI()
        else:
            print("Successfully logged in.")
    
    def view_list_note(self):
        data = self.client.recv(1024).decode(FORMAT)
        data = json.loads(data)
        k = 1
        for i in data['Note']:
            print(k,":", i)
            k +=1
        option = input("Choose a note which you want to open: ")
        self.send_msg(option)
        format = self.receive_msg()

        if format == "png" or format == "jpg":
            self.third_UI()
        else:
            self.fourth_UI()


    def create_note(self):
        id = input("ID:")
        self.send_msg(id)

        print("TYPE:\n1. Text\n2. Images\n3. Files\n")
        option = input("Choose one type: ")
        self.send_msg(option)

        file = input("File name: ")
        self.send_msg(file)
       
        #check
        check = self.receive_msg()
        if check == "False":
            print("ID has been used or wrong input.")
            self.create_note()
        # send file
        try:
            self.send_file(file)
        except:
            print("File {} not found".format(file))
            return
        print("Success!")
    
    def view_note(self):
        _filename =self.receive_file()

        """ img = Image.open(_filename)
        # Output Images
        img.show() """
        cmd = _filename
        subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

        cmd = "del/Q " + _filename
        subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    
    def view_image(self):
        self.view_note()

    def download(self):
        _filename = self.receive_file()
        print("File {} has been downloaded ".format( _filename))

    def main(self):
        self.first_UI()
        self.client.close()

C = Client()
C.main()