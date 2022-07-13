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
from tkinter import Menu

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
        self.client.send(bytes(msg, "utf8"))

    def send_file(self, filename):
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
                # we use sendall to assure transmission in
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
        current_size = 0
        # start receiving the file from the socket
        # and writing to the file stream
        with open(_filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.client.recv(BUFFER_SIZE)
                current_size += len(bytes_read)
                # write the bytes to the file
                f.write(bytes_read)
                # check if the file transmission is done
                if current_size == filesize:
                    # if done, break
                    break
        return _filename

    def sign_up(self,_name,_pass):
        #send info
        self.send_msg(_name)
        x = self.receive_msg()
        self.send_msg(_pass)
        #receive msg from Server
        check = self.receive_msg()
        if check == "False":
            messagebox.showinfo("showinfo", "Account is exist or size is smaller than required size.")
           # self.first_UI()
        else:
            messagebox.showinfo("showinfo","Successfully registered.")
        return check

    def sign_in(self, _name, _pass):
        self.send_msg(_name)
        x = self.receive_msg()
        self.send_msg(_pass)
        #receive msg from Server
        check = self.receive_msg()
        if check == "False":
           messagebox.showinfo("Error!", "Username or password is wrong.")
          #  self.first_UI()
        else:
            messagebox.showinfo("Success!","Successfully logged in.")
        return check

    def view_list_note(self):
        viewListNote= Tk()

        #send finish ping to server
        def close_window():
            end = "finish"
            self.send_msg(end)
            viewListNote.destroy()
        viewListNote.protocol("WM_DELETE_WINDOW", close_window)

        #initialize window
        viewListNote.title("View list note")
        viewListNote.geometry("700x500")
        frame = tkinter.Frame(viewListNote)

        #Check the file exists or not
        try:
            data = self.client.recv(1024).decode(FORMAT)
            data = json.loads(data)
        except:
            #viewListNote.destroy()
            messagebox.showinfo("Error!", "There are not data !")
            #self.main()
            return

        #Print data received from server 
        k = 1
        txt = tkinter.Text(frame)
        for i in data['Note']:
            txt.insert(tkinter.END, str(k),":")
            txt.insert(tkinter.END, i)
            txt.insert(tkinter.END, "\n")
            print(k,":", i)
            k += 1
        txt.grid()

        note = Label (frame, text ="Choose a note which you want to open:  ")
        note.grid()
        entryX = Entry(frame, width=20,bd=5)
        entryX.grid()
        frame.grid_rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.pack(side="top", fill="both", expand=True)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid()

        ##### THIRD UI #####
        thirdFrame = tkinter.Frame(viewListNote)
        thirdFrame.grid_rowconfigure(0, weight=1)
        thirdFrame.columnconfigure(0, weight=1)
        thirdFrame.grid(row=0, column=0, sticky="nsew")
        third_label = Label(thirdFrame, text="THIRD UI", font=("ROBOTO", 16), bd=5)
        third_label.grid()

        def return2_click():
            option = "3"
            self.send_msg(option)
            viewListNote.destroy()

        def viewImage_click():
            option = "1"
            self.send_msg(option)
            self.view_image()
            #frame.tkraise()

        def download_click():
            option = "2"
            self.send_msg(option)
            self.download()
            #frame.tkraise()

        viewImage_button = Button(thirdFrame, width=20, height=2, text="View Image", bd=5, command=viewImage_click)
        viewImage_button.grid()
        downloadImage_button = Button(thirdFrame, width=20, height=2, text="Download Image", bd=5, command=download_click)
        downloadImage_button.grid()
        return2_button = Button(thirdFrame, width=20, height=2, text="Back", bd=5, command=return2_click)
        return2_button.grid()

        fourthFrame = tkinter.Frame(viewListNote)
        fourthFrame.grid_rowconfigure(0, weight=1)
        fourthFrame.columnconfigure(0, weight=1)
        fourthFrame.grid(row=0, column=0, sticky="nsew")
        fourth_label = Label(fourthFrame, text="FOURTH UI", font=("ROBOTO", 16), bd=5)
        fourth_label.grid()

        def viewNote_click():
            option = "1"
            self.send_msg(option)
            self.view_note()
            #frame.tkraise()

        def downloadNote_click():
            option = "2"
            self.send_msg(option)
            self.download()
            #frame.tkraise()

        def return3_click():
            option = "3"
            self.send_msg(option)
            viewListNote.destroy()
            #frame.tkraise()

        viewNote_button = Button(fourthFrame, width=20, height=2, text="View Note", bd=5, command=viewNote_click)
        viewNote_button.grid()
        downloadFile_button = Button(fourthFrame, width=20, height=2, text="Download file", bd=5, command=downloadNote_click)
        downloadFile_button.grid()
        return3_button = Button(fourthFrame, width=20, height=2, text="Back", bd=5, command=return3_click)
        return3_button.grid()
        frame.tkraise()

        def click():
            option = entryX.get()
            self.send_msg(option)
            format = self.receive_msg()
            if format == "png" or format == "jpg":
                thirdFrame.tkraise()
            else:
                fourthFrame.tkraise()

        b = Button(frame, text="Enter", bd=5, command=click)
        b.grid()

    def create_note(self):
        createNote = Tk()

        #send finish ping to server
        def close_window():
            end = "finish"
            self.send_msg(end)
            createNote.destroy()
        createNote.protocol("WM_DELETE_WINDOW", close_window)

        createNote.title("Create Note")
        inputId_label = Label(createNote,text=" Input ID:")
        inputId_label.grid()
        inputId_entry = Entry(createNote, width=20, bd=5)
        inputId_entry.grid()
        inputType_label = Label(createNote, text=" Input type:")
        inputType_label.grid()
        inputType_entry = Entry(createNote, width=20, bd=5)
        inputType_entry.grid()
        inputFile_label = Label(createNote, text=" Input file name :")
        inputFile_label.grid()
        inputFile_entry = Entry(createNote, width=20, bd=5)
        inputFile_entry.grid()

        def create_click():
            id = inputId_entry.get()
            type = inputType_entry.get()
            file=inputFile_entry.get()
            self.send_msg(id)
            print(id)
            self.receive_msg()
            self.send_msg(type)
            self.receive_msg()
            print(type)
            self.send_msg(file)
            print(file)
            check = self.receive_msg()
            if check == "False":
                messagebox.showinfo("showinfo","ID has been used or wrong input.")
            else:
                messagebox.showinfo("showinfo", "Success!")

            try:
                self.send_file(file)
                createNote.destroy()
                print("send success")
            except:
                print("send fail")
                messagebox.showinfo("showinfo", "File {} not found".format(file))
                return

        enter_button = Button(createNote, height=2,width=20,text="Enter",bd=5,command=create_click)
        enter_button.grid()

    def view_note(self):
        _filename =self.receive_file()

        cmd = _filename
        subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

        cmd = "del/Q " + _filename
        subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

    def view_image(self):
        _filename =self.receive_file()

        img = Image.open(_filename)
        # Output Images
        img.show()

        cmd = "del/Q " + _filename
        subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

    def download(self):
        _filename = self.receive_file()
        print("File {} has been downloaded ".format( _filename))


    def main(self):
        window = Tk()
        window.geometry("500x200")
        window.title("Client")
        menubar= Menu(window)
        window.config(menu=menubar)
        file_menu= Menu(menubar)
        file_menu.add_command(
        label='Exit',
        command=window.destroy)
        menubar.add_cascade(
            label="File",
            menu=file_menu
        )

        ##### FIRST UI ####
        firstFrame = tkinter.Frame(window)
        secondFrame = tkinter.Frame(window)
        login_label = Label (firstFrame, text = "LOGIN PAGE", font=("ROBOTO",16))
        login_label.grid(row=0, column=2,)
        label_username = Label(firstFrame, text="User name: ")
        box_username = Entry(firstFrame,width=20,bg="pink",bd=5)
        label_username.grid(column = 2, row  = 1 )
        box_username.grid(column = 3 , row = 1 )
        label_password = Label(firstFrame, text ="Password")
        label_password.grid(column = 2, row = 2 )
        box_password = Entry(firstFrame, width=20, bg="pink",bd=5)
        box_password.grid(column = 3, row = 2)

        def login_click():
            option = "2"
            self.send_msg(option)
            _username = box_username.get()
            print(_username)
            _pass = box_password.get()
            print(_pass)
            check = self.sign_in(_username, _pass)
            if check == "True":
                secondFrame.tkraise()

        def register_click():
            option = "1"
            self.send_msg(option)
            _username = box_username.get()
            print(_username)
            _pass = box_password.get()
            print(_pass)
            check = self.sign_up(_username, _pass)
            if check == "True":
                secondFrame.tkraise()

        firstFrame.pack(side="top", fill="both", expand=True)
        firstFrame.grid_rowconfigure(0, weight=1)
        firstFrame.columnconfigure(0, weight=1)
        firstFrame.grid(row=0,column=0,sticky="nsew")

        ##### SECOND UI #####
        secondFrame.grid_rowconfigure(0, weight=1)
        secondFrame.columnconfigure(0, weight=1)
        secondFrame.grid(row=0, column=0, sticky="nsew")
        firstFrame.tkraise()
        login_button = Button(firstFrame, width=20, height=2, text="Login", command=login_click)
        login_button.grid(column = 3)
        register_button = Button(firstFrame, width=20, height=2, text="Register", bg="yellow", command=register_click)
        register_button.grid(column = 3)

        def return_click():
            option = "3"
            firstFrame.tkraise()
            self.send_msg(option)
        def viewNote_click():
            option="1"
            self.send_msg(option)
            self.view_list_note()
        def createNote_click():
            option="2"
            self.send_msg(option)
            self.create_note()

        second_label = Label(secondFrame, text="SECOND UI", font=("ROBOTO", 16),bd=5)
        second_label.grid()
        viewNote_button = Button(secondFrame,width=20,height=2,text="View Note",bd=5,command=viewNote_click)
        viewNote_button.grid()
        createNote_button = Button(secondFrame, width=20, height=2, text="Create Note",bd=5,command=createNote_click)
        createNote_button.grid()
        return_button = Button(secondFrame, width=20, height=2, text="Back",bd=5,command=return_click)
        return_button.grid()

        firstFrame.tkraise()
        window.mainloop()

C = Client()

C.main()
