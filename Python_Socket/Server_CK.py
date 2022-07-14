import socket
import json
import os
from Func import *
import threading

FORMAT = "utf8"
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Server:
    #initialize socket connection
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = '10.123.0.130'  # Standard loopback interface address (localhost)
        PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
        self.server.bind((HOST, PORT))
        self.server.listen()
        print(f"[*] Listening as {HOST}:{PORT}")


S = Server()

#multithreading client socket
def handle(conn, addr):
    #receive message from client
    def receive_msg():
        data = conn.recv(1024).decode(FORMAT)
        print("Client: " + data)
        return data

    #send message to client
    def send_msg(msg):
        print("Server: " + msg)
        conn.sendall(bytes(msg, "utf8"))

    #send file to client
    def send_file(filename):
        # get the file size
        filesize = os.path.getsize(filename)
        # send the filename and filesize
        conn.send(f"{filename}{SEPARATOR}{filesize}".encode())
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
                conn.sendall(bytes_read)

    #receive file from client
    def receive_file():
        received = conn.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        _filename = "server_" + filename
        # convert to integer
        filesize = int(filesize)

        current_size = 0
        # start receiving the file from the socket
        # and writing to the file stream
        with open(_filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = conn.recv(BUFFER_SIZE)
                current_size += len(bytes_read)
                # write the bytes to the file
                f.write(bytes_read)
                # check if the file transmission is done
                if current_size == filesize:
                    # if done, break
                    break
        return _filename

    #first UI: sign up, sign in
    def first_UI():
        #receive option of user inputs
        option = receive_msg()
        if option == '1':
            username = sign_up()
            second_UI(username)
        elif option == '2':
            username = sign_in()
            second_UI(username)
        elif option == '3':
            print("Closing socket")

    #second UI: view list note, create note, back
    def second_UI(username):
        #receive option of user inputs
        option = receive_msg()
        if option == '1':
            view_list_note(username)
            second_UI(username)
        elif option == '2':
            create_note(username)
            second_UI(username)
        elif option == '3':
            first_UI()

    #third UI: view image, download, back
    def third_UI(_filename, username):
        while True:
            #receive option of user inputs
            option = receive_msg()
            if option == "1":
                view_image(_filename)
            elif option == '2':
                download(_filename)
            elif option == '3':
                second_UI(username)
                break
    
    #fourth UI: view note, download, back
    def fourth_UI(_filename, username):
        while True:
            #receive option of user inputs
            option = receive_msg()
            if option == "1":
                view_note(_filename)
            elif option == '2':
                download(_filename)
            elif option == '3':
                second_UI(username)
                break

    def sign_up():
        #receiver info of account
        username = receive_msg()
        send_msg("-------")
        password = receive_msg()
        # Read file
        list = read_json()
        # store info
        dict = {
            "user": "",
            "pass": ""
        }
        error = 0
        # check username
        if check_user(list, username) == False:
            error += 1
        else:
            dict["user"] = username
        # check password
        if check_pass(password) == False:
            error += 1
        else:
            dict["pass"] = password
        
        # send result after checking
        if error == 1 or error == 2:
            send_msg("False")
            first_UI()
        else:
            # store account into databases
            append_account(dict)
            # initialize database which contains notes of user
            filename = username + ".json"
            init_file(filename)
            send_msg("True")
        return username

    def sign_in():
        #receive info of account from client
        username = receive_msg()
        conn.send("-------".encode(FORMAT))
        password = receive_msg()

        # Read file
        list = read_json()
        error = 0

        # check username
        if check_user_1(list, username) == False:
            error += 1
        # check password
        if check_pass_1(list, password) == False:
            error += 1

        #send result after checking 
        if error == 1 or error == 2:
            send_msg("False")
            first_UI()
        else:
            send_msg("True")
        return username

    def view_list_note(username):
        filename = username + '.json'
        # Store data from file
        with open(filename, "r") as f:
            data = json.load(f)

        # Send data in file
        _data = json.dumps(data)
        conn.sendall(bytes(_data, "utf8"))

        # finish ping from client
        msg = receive_msg()
        if msg == "finish":
            return

        # identify file in database
        option = int(msg)
        k, _filename = 1, ""
        for i in data['Note']:
            if k == option:
                _filename = i["File name"]
                break
            k += 1
        # Get format of file
        format = _filename.split(".")
        print("--------")
        send_msg(format[1])   
        if format[1] == "png" or format[1] == "jpg":
            third_UI(_filename, username)
        else:
            fourth_UI(_filename, username)

    def create_note(username):
        filename = username + '.json'
        # receive data
        id = receive_msg()
        # finish ping from client
        if id == "finish":
            return

        send_msg("---------")
        option = receive_msg()
        send_msg("---------")
        _file = receive_msg()
        # check id and type are correct or not
        type = check_type(option)
        if check_id(filename, id) == False or type == "":
            send_msg("False")
        else:
            send_msg("True")

        # error ping from client
        msg = receive_msg()
        send_msg("---------")
        if msg == "error":
            return

        # receive file
        try:
            print("-------")
            file = receive_file()
            print("receive success")
        except: #program occurs error in receiving file
            print("File not found")
            return

        # Store a note
        listObj = {
            "Id": id,
            "Type": type,
            "File name": file
        }
        write_json(listObj, filename)

    def view_note(_filename):
        send_file(_filename)
        print("Success!")

    def view_image(_filename):
        view_note(_filename)

    def download(_filename):
        send_file(_filename)
        print("Success!")

    def main():
        first_UI()
        print(addr,"FINISH")

    main()

n = 0
#at most 3 clients connected to server
while (n<3):
    try:
        conn , addr = S.server.accept()
        #print ip of client
        print("connect ", addr)
        #multithreading
        thr = threading.Thread(target=handle,args=(conn,addr))
        thr.daemon = False
        thr.start()
    except:
        print("ERROR")
    n+=1

S.server.close()