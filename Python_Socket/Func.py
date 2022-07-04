
import json
def read_json(filename = "account.json"):
    with open(filename,'r') as file:
        data = json.load(file)
        list = []
        for i in data['Account']:
            dict={
                "user":"",
                "pass":""
            }
            dict["user"] = i.get("user")
            dict["pass"] = i.get("pass")
            list.append(dict)
    return list

#check username when user signs up
def check_user(list, user):
    is_valid = True
    #Size must be smaller than 6
    if len(user) < 5:
        return False
    #Username must be unique
    for acc in list:
        if acc.get("user") == user:
            is_valid = False
            break
    return is_valid

#check username when user signs in
def check_user_1(list, user):
    is_valid = False
    #Size must be smaller than 6
    if len(user) < 5:
        return is_valid
    #Username must be suitable
    for acc in list:
        if acc.get("user") == user:
            is_valid = True
            break
    return is_valid

#check password when user signs up
def check_pass(_pass):
    is_valid = True
    #Size must be smaller than 4
    if len(_pass) < 3:
        is_valid = False
    return is_valid

#check password when user signs in
def check_pass_1(list, _pass):
    is_valid = False
    #Size must be smaller than 4
    if len(_pass) < 3:
        return is_valid
    #password must be suitable
    for acc in list:
        if acc.get("pass") == _pass:
            is_valid = True
            break
    return is_valid

def check_id(filename, id):
    if len(id) < 3:
        return False
    error = 0
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except:
        error = 1
    if error == 0:
        for i in data['Note']:
            if id == i['Id']:
                return False
    return True

def check_type(option):
    type = ""
    if option == "1":
        type = "Text"
    elif option == "2":
        type = "Images"
    elif option == "3":
        type = "Files"
    return type

def append_account(new_data, filename='account.json'):
    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["Account"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def init_file(filename):
    #check file is exist or not
    error = 0
    try:
        with open(filename,"r") as file:
            data = json.load(file)
    except:
        error = 1

    var = {
        "Note":[
            {
            "Id": "smaller than 8",
            "Type": "must be a positive number",
            "File name": "must be exist"
            }
        ]
    }
    if error == 1:
        with open(filename, "w") as f:
            json.dump(var, f, indent=4)

def write_json(new_data, filename):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["Note"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

