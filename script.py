import paramiko

charzin = [
    "119.65.249.4",
    "33000",
    "",
    "0",
    "",
]

zevtron = [
    "wss://go.zevtron.com",
    "443",
    "/api/Ocpp16J",
    "1",
    "",
]

ev_initiative = [
    "ws.evinitiative.com",
    "8080",
    "/EVI",
    "0",
    "",
]

choose_list = [charzin, zevtron, ev_initiative]


editable_content = [
    "url = ",
    "port = ",
    "path = ",
    "ssl_on = ",
    "password = ",
]

content_start_position = [
    6,
    7,
    7,
    9,
    11,
]

lines = [5, 6, 7, 9, 10]


def change_file_content(hostname, username, password, file_path):
    print("""\n
  ===CHOOSE YOUR OCPP BACKEND===
          1. Charzin
          2. Zevtron
          3. EV_Initiative
          """)
    choice = int(input("Choose your OCPP back-end(#): "))
    if int(choice) > len(choose_list) or int(choice) < 1:
        print("Invalid input!\n")
        
        change_file_content("192.168.88.206", "root", "d1H3.s2C4", "/ubi/conf/ocpp/config.ini")


    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    sftp = ssh.open_sftp()

    with sftp.file(file_path, "r") as f:
        lines = f.readlines()
        lines[5] = str(editable_content[0] + choose_list[choice-1][0] + "\n")
        lines[6] = str(editable_content[1] + choose_list[choice-1][1] + "\n")
        lines[7] = str(editable_content[2] + choose_list[choice-1][2] + "\n")
        lines[9] = str(editable_content[3] + choose_list[choice-1][3] + "\n")
        lines[10]= str(editable_content[4] + choose_list[choice-1][4] + "\n")

    with sftp.file(file_path, "w") as f:
        f.writelines(lines)
    print("DONE")

        
change_file_content("192.168.88.206", "root", "d1H3.s2C4", "/ubi/conf/ocpp/config.ini")
