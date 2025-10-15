import socket

HOST = '127.0.0.1'
PORT = 5050

def send_cmd(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(f"{cmd}\n".encode())
        response = s.recv(1024).decode()
        print(response)

if __name__ == '__main__':
    while True:
        cmd = input(">>")
        if cmd.lower() == "exit":
            break
        send_cmd(cmd)