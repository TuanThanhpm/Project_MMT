import socket
import json
import os
from tkinter import *
from tkinter import messagebox
from Func import *

FORMAT = "utf8"
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
        self.server.bind((HOST, PORT))
        self.server.listen()
        print(f"[*] Listening as {HOST}:{PORT}")
        self.conn, addr = self.server.accept()
        print("Client ", addr, "Connected")

    def receive_msg(self):
        data = self.conn.recv(1024).decode(FORMAT)
        print("Client: " + data)
        return data

    def send_msg(self, msg):
        print("Server: " + msg)
        self.conn.sendall(bytes(msg, "utf8"))

    def send_file(self,filename):
        # get the file size
        filesize = os.path.getsize(filename)
        # send the filename and filesize
        self.conn.send(f"{filename}{SEPARATOR}{filesize}".encode())
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
                self.conn.sendall(bytes_read)
            
    def receive_file(self):
        # receive the file infos
        # receive using client socket, not server socket
        received = self.conn.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        _filename = "server_" + filename
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        with open(_filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.conn.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
        return _filename

    def first_UI(self):
        option = self.receive_msg()
        if option == '1':
            username = self.sign_up()
            self.second_UI(username)
        elif option == '2':
            username = self.sign_in()
            self.second_UI(username)
        elif option == '3': 
            print("Closing socket")

    def second_UI(self,username):
        option = self.receive_msg()
        if option == '1':
            self.view_note(username)
        elif option == '2':
            self.create_note(username)
            #self.first_UI()
        elif option == '3': 
            self.first_UI()

    def third_UI(self,_filename,username):
        option = self.receive_msg()
        if option == "1":
            self.view_image(_filename)
            #self.second_UI(username)
        elif option == '2':
            self.download(_filename)
            #self.second_UI(username)
        elif option == '3':
            self.second_UI(username)
    
    def fourth_UI(self,_filename,username):
        option = self.receive_msg()
        if option == "1":
            self.download(_filename)
            #self.second_UI(username)
        elif option == '2':
            self.second_UI(username)

    def sign_up(self):
        username = self.receive_msg()
        password = self.receive_msg()
        #Read file
        list = read_json()
        #store info
        dict={
            "user":"",
            "pass":""
        }
        error = 0
        #check username
        if check_user(list,username) == False:
            error +=1
        else:
            dict["user"] = username
        #check password
        if check_pass(password) == False:
            error +=1
        else:
            dict["pass"] = password 
        if error == 1 or error == 2:
            self.send_msg("False")
            self.first_UI()
        else:
            append_account(dict)
            self.send_msg("True")
        return username

    def sign_in(self):
        username = self.receive_msg()
        password = self.receive_msg()
        #Read file
        list = read_json()
        error = 0
        #check username
        if check_user_1(list,username) == False:
            error +=1
        #check password
        if check_pass_1(list,password) == False:
            error +=1
        if error == 1 or error == 2:
            self.send_msg("False")
            self.first_UI()
        else:
            self.send_msg("True")
        return username
    
    def view_note(self, username):
        filename = username + '.json'
        with open(filename, "r") as f:
            data = json.load(f)
        _data = json.dumps(data)
        self.conn.sendall(bytes(_data, "utf8"))
        option = int(self.receive_msg())
        k, _filename= 1,""
        for i in data['Note']:
            if k == option:
                _filename = i["File name"]
                break
            k+=1
        format = _filename.split(".")
        self.send_msg(format[1])
        if format[1] == "png" or format[1] == "jpg":
            self.third_UI(_filename, username)
        else:
            self.fourth_UI(_filename, username)

    def create_note(self, username):
        filename = username + '.json'
        #receive data 
        id = self.receive_msg()
        option = self.receive_msg()
        _file = self.receive_msg()
        #check 
        type = check_type(option)
        print(type)
        if check_id(filename,id) == False or type == "":
            self.send_msg("False")
            self.create_note(username)
        else:
            self.send_msg("True")
        #receive file
        try:
            file = self.receive_file()
        except:
            print("File not found")
            return
        print("Success!")
        #Store a note
        init_file(filename)
        listObj = {
            "Id": id,
            "Type": type,
            "File name": file
        }
        write_json(listObj, filename)

    def view_image(self,_filename):
        self.send_file(_filename)
        print("Success!")

    def download(self,_filename):
        self.send_file(_filename)
        print("Success!")

    def main(self):
        self.first_UI()
        self.server.close()

S = Server()
S.main()