import socket
import threading

HOST = '0.0.0.0'
PORT = 5050
VERSION = "KV/1.0"

store = {}  # simple key-value memory
stats = {"puts": 0, "gets": 0, "dels": 0, "connections": 0}

def handle_client(conn, addr):
   print(f"[Connected] {addr}")
   stats["connections"] += 1
   with conn:
       while True:
           try:
               data = conn.recv(1024).decode("utf-8")
               if not data:
                   break
               line = data.strip()
               if not line:
                   continue
               parts = line.split()
               if len(parts) < 2:
                   conn.sendall(b"400 BAD_REQUEST\n")
                   continue
               version, command = parts[0], parts[1]
               if version != VERSION:
                   conn.sendall(b"426 UPGRADE_REQUIRED\n")
                   continue
               if command == "PUT":
                   if len(parts) < 4:
                       conn.sendall(b"400 BAD_REQUEST\n")
                       continue
                   key, value = parts[2], parts[3]
                   created = key not in store
                   store[key] = value
                   stats["puts"] += 1
                   msg = "201 CREATED\n" if created else "200 OK\n"
                   conn.sendall(msg.encode())
               elif command == "GET":
                   if len(parts) < 3:
                       conn.sendall(b"400 BAD_REQUEST\n")
                       continue
                   key = parts[2]
                   stats["gets"] += 1
                   if key in store:
                       conn.sendall(f"200 OK {store[key]}\n".encode())
                   else:
                       conn.sendall(b"404 NOT_FOUND\n")
               elif command == "DEL":
                   if len(parts) < 3:
                       conn.sendall(b"400 BAD_REQUEST\n")
                       continue
                   key = parts[2]
                   stats["dels"] += 1
                   if key in store:
                       del store[key]
                       conn.sendall(b"204 NO_CONTENT\n")
                   else:
                       conn.sendall(b"404 NOT_FOUND\n")
               elif command == "STATS":
                   data = " ".join([f"{k}:{v}" for k,v in stats.items()])
                   conn.sendall(f"200 OK {data}\n".encode())
               elif command == "QUIT":
                   conn.sendall(b"200 OK Bye\n")
                   break
               else:
                   conn.sendall(b"400 BAD_REQUEST\n")
           except Exception as e:
               conn.sendall(b"500 SERVER_ERROR\n")
               print("Error:", e)
               break
   print(f"[Disconnected] {addr}")

def main():
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
       s.bind((HOST, PORT))
       s.listen()
       print(f"[Server listening on {HOST}:{PORT}]")
       while True:
           conn, addr = s.accept()
           threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
   main()