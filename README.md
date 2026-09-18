# Python Socket-Based Remote Shell

A Python networking project demonstrating how a TCP client and server can communicate using sockets and a custom length-prefixed JSON protocol.

The project consists of two components:

* **Server** — listens for incoming TCP connections and provides an interactive command interface.
* **Client / Backdoor** — connects to the server, receives commands, executes them locally, and sends the output back.

> **Warning:** This project is intended strictly for authorized cybersecurity labs, virtual machines, CTFs, and systems you own or have explicit permission to test. Do not deploy it on other people's systems or networks.

## Project Structure

```text
.
├── server.py
├── backdoor.py
└── README.md
```

## How It Works

The project uses a TCP connection between the server and client.

```text
             TCP Connection
       ┌────────────────────────┐
       │                        │
       ▼                        │
┌─────────────┐          ┌──────────────┐
│   Server    │◄────────►│    Client    │
│             │          │  / Backdoor  │
└──────┬──────┘          └──────┬───────┘
       │                        │
       │ Sends command          │
       ├───────────────────────►│
       │                        │
       │                        │ Executes
       │                        │ command
       │                        │
       │ Command output         │
       ◄───────────────────────┤
       │                        │
       ▼                        ▼
    Terminal               Subprocess
```

### Server

The server:

1. Creates a TCP socket.
2. Binds it to the configured IP address and port.
3. Starts listening for connections.
4. Accepts a client connection.
5. Sends commands entered by the operator.
6. Receives the command output.
7. Displays the result in the terminal.

### Client

The client:

1. Creates a TCP socket.
2. Connects to the configured server.
3. Waits for commands.
4. Executes received commands through Python's `subprocess` module.
5. Sends the command output back to the server.
6. Automatically attempts to reconnect if the connection is lost.

---

## Custom Communication Protocol

One of the main learning points of this project is that TCP is a **byte stream**, not a message-based protocol.

For that reason, the project implements a simple application-layer framing system.

Every message is structured as:

```text
[ 8-byte message length ][ JSON data ]
```

For example:

```text
8-byte length
      +
JSON encoded message
```

### Sending Data

The sender converts the Python object into JSON:

```python
raw = json.dumps(data).encode()
```

It then sends the size of the message followed by the actual data:

```python
len(raw).to_bytes(8, 'big') + raw
```

### Receiving Data

The receiver first reads exactly 8 bytes to determine the message size:

```python
length = int.from_bytes(recv_exact(8), 'big')
```

It then reads exactly that many bytes and decodes the JSON.

This prevents the application from incorrectly assuming that one `recv()` call always contains one complete message.

---

## `recv_exact()`

The project includes a helper function for reliably receiving a specific number of bytes.

```python
def recv_exact(conn, n):
    buf = b''

    while len(buf) < n:
        chunk = conn.recv(n - len(buf))

        if not chunk:
            raise ConnectionError('connection closed')

        buf += chunk

    return buf
```

The important idea is:

```text
TCP
 │
 ├── recv() → might receive only part of the data
 ├── recv() → more data
 └── recv() → remaining data
```

`recv_exact()` keeps receiving until the expected number of bytes has arrived.

---

## JSON Communication

Instead of sending raw Python objects, the project serializes messages using JSON.

```python
json.dumps(data)
```

And converts them back using:

```python
json.loads(data)
```

This creates a simple and understandable application-layer protocol on top of TCP.

---

## Connection Flow

The overall connection process looks like this:

```text
Server starts
     │
     ▼
Bind IP + Port
     │
     ▼
Listen
     │
     ▼
Wait for connection
     │
     ▼
Client connects
     │
     ▼
Server accepts connection
     │
     ▼
Command entered
     │
     ▼
Command sent using
length-prefixed JSON
     │
     ▼
Client receives command
     │
     ▼
Command executed locally
     │
     ▼
Output returned
     │
     ▼
Server displays output
```

Entering:

```text
exit
```

terminates the current shell session.

---

## Configuration

Both programs contain:

```python
HOST = '192.168.0.103'
PORT = 5445
```

`HOST` should correspond to the IP address of the machine running the server, while `PORT` specifies the TCP port used by the application.

For a local cybersecurity lab, both machines should be systems you control, such as:

```text
Windows VM
     │
     │ TCP
     ▼
Linux VM
```

Make sure the virtual machines are configured with appropriate isolated networking.

---

## Requirements

The project uses Python's standard library.

No external Python packages are required.

Main modules:

```python
socket
json
subprocess
time
```

Python 3 is recommended.

---

## Running the Lab

### 1. Start the Server

Run the server on your controlled lab machine:

```bash
python server.py
```

You should see:

```text
[*] Listening on 192.168.0.103:5445
```

### 2. Start the Client

Run the client on the other controlled lab machine:

```bash
python backdoor.py
```

Once connected, the server should report the incoming connection.

You can then enter commands through the server's terminal and observe the returned output.

---

## Key Concepts Demonstrated

This project was built to understand several important cybersecurity and networking concepts:

* TCP socket programming
* Client-server architecture
* IP addresses and ports
* TCP connection establishment
* `bind()`
* `listen()`
* `accept()`
* `connect()`
* Sending and receiving bytes
* TCP stream behavior
* Application-layer message framing
* JSON serialization
* Exception handling
* Python subprocess execution
* Connection handling
* Automatic reconnection
* Basic remote-shell architecture

---

## Security Limitations

This project is intentionally simple and **should not be considered a secure remote administration system**.

It currently lacks:

* Authentication
* Encryption
* TLS
* Authorization
* Command restrictions
* Integrity verification
* Secure key exchange
* Logging
* Access control
* Certificate validation

The client also uses:

```python
subprocess.Popen(..., shell=True)
```

which means received commands are passed to the system shell. This is one of the reasons the program should only be executed inside an isolated environment you control.

---

## What I Learned

Building this project helped me understand the difference between simply opening a socket and building an actual communication protocol on top of TCP.

The most important part was implementing message framing because TCP does not preserve application-level message boundaries.

I also learned how a basic remote-shell architecture works:

```text
Network
   ↓
TCP Socket
   ↓
Protocol
   ↓
Command
   ↓
Local Process
   ↓
Command Output
   ↓
Protocol
   ↓
TCP Socket
```

This provides a foundation for understanding both **offensive security techniques** and how defenders can identify and analyze command-and-control traffic.

---

## Future Improvements

Possible improvements for a controlled security lab include:

* Add authenticated connections
* Implement encrypted communication
* Add structured message types
* Add proper logging
* Implement connection timeouts
* Replace unrestricted shell execution with a controlled command set
* Build a packet-analysis component
* Detect the protocol using Wireshark
* Create IDS/IPS detection rules
* Analyze the traffic from a defensive-security perspective

---

## Disclaimer

This repository is for **educational and authorized security research purposes only**.

Only run the software on systems and networks where you have explicit permission to perform security testing.

The author is not responsible for misuse or unauthorized deployment of this software.
