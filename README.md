# Reliable Transport Protocol over UDP

Experimental implementation of a reliable transport layer over UDP with custom packet handling, CRC-based error detection, ARQ mechanisms, and network fault simulation.

## Project Overview

UDP provides fast communication but does not guarantee:

* Packet delivery
* Packet ordering
* Error detection
* Retransmission
* Flow control

This project builds a reliability layer on top of UDP.

Implemented features:

* Custom packet format
* Sequence numbers
* ACK handling
* CRC error detection
* Stop-and-Wait ARQ
* Network fault injection

  * Packet loss
  * Corruption
  * Delay
  * Duplication

Implemented reliability protocols:

* Stop-and-Wait ARQ
* Go-Back-N Sliding Window
* Selective Repeat Sliding Window

Current focus:

* Performance evaluation and comparison

---

# Setup

## Requirements

* Python 3.10+
* Git

Check installation:

```bash
python --version
git --version
```

---

# Clone Repository

```bash
git clone https://github.com/adharsh0713/reliable-udp.git

cd reliable-udp
```

---

# Virtual Environment (Recommended)

Create environment:

```bash
python -m venv venv
```

Activate:

### Windows PowerShell

```powershell
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

---

# Install Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Current implementation mainly uses Python standard libraries.

---

# Project Structure

```
reliable-udp/

├── sender/
│   └── sender.py
│
├── receiver/
│   └── receiver.py
│
├── protocol/
│   ├── packet.py
│   ├── crc.py
│   └── timer.py
│
├── algorithms/
│   └── stop_wait.py
│
├── network/
│   ├── fault_injector.py
│   └── proxy.py
│
├── data/
│   ├── test_files/
│   └── results/
│
└── docs/
```

---

# Running the Project

The project uses Python modules, so commands should be executed from the project root.

Example:

```
reliable-udp/
```

---

## 1. Start Receiver

Open terminal 1:

```bash
python -m receiver.receiver
```

Receiver waits for incoming packets and reconstructs the transferred file.

---

## 2. Start Network Proxy

Open terminal 2:

```bash
python -m network.proxy
```

The proxy acts as the network layer between sender and receiver.

It can introduce:

* Packet loss
* Packet corruption
* Packet delay
* Packet duplication

---

## 3. Start Sender

Open terminal 3:

```bash
python -m sender.sender data/test_files/sample.txt
```

The sender transfers the file through the proxy.

---

# Architecture

```
              File
                |
                v

             Sender

                |
                |
              UDP

                |
                v

        Fault Injection Proxy

     Loss  Corruption  Delay  Duplicate

                |
                v

            Receiver

                |
                v

        Reconstructed File
```

---

# Implemented Phases

## Phase 1 — UDP Foundation

Completed.

Implemented:

* UDP socket communication
* Sender and receiver model
* Basic file transfer

Flow:

```
Sender
   |
 UDP
   |
Receiver
```

---

# Phase 2 — Custom Packet Layer

Completed.

Implemented custom packet format.

Packet structure:

```
+----------------+
| Sequence ID    |
+----------------+
| Packet Type    |
+----------------+
| Payload Length |
+----------------+
| CRC            |
+----------------+
| Payload        |
+----------------+
```

Packet types:

```python
DATA = 0
ACK  = 1
END  = 2
```

Implemented:

* Packet serialization
* Packet deserialization
* Header handling

---

# Phase 3 — CRC Error Detection

Completed.

Implemented CRC32 checksum verification.

Flow:

```
Sender

Payload
   |
CRC generation
   |
Packet


Receiver

Packet
   |
CRC verification
   |
Accept / Reject
```

Testing:

Normal packet:

```
Packet accepted
```

Corrupted packet:

```
CRC mismatch
Packet discarded
```

---

# Phase 4 — Stop-and-Wait ARQ

Completed.

Implemented reliability using:

* ACK packets
* Timeout detection
* Retransmission
* Retry limit

Working flow:

```
Send DATA(seq)

        |
        v

    Wait ACK

        |
  +-----+------+
  |            |
ACK received  Timeout

  |             |
Next packet   Resend
```

Example:

Successful transfer:

```
Sending packet 0
ACK received: 0
Sending packet 1
ACK received: 1
```

Timeout example:

```
Sending packet 0
Timeout
Resending packet 0
```

---

# Phase 5 — Fault Injection Proxy

Completed.

Implemented network simulation layer.

Architecture:

```
Sender

  |
  v

Proxy

  |
  v

Receiver
```

---

**# Phase 6 — Go-Back-N Sliding Window Protocol**

Completed.

Implemented Go-Back-N reliability using:

\* Sliding window mechanism

\* Multiple packets in transmission

\* Cumulative ACK handling

\* Timeout based window retransmission

\* Sequence number tracking


Working flow:

\`\`\`

Window size = N


Send:

[0][1][2][3]


Receive ACKs


Move window forward

\`\`\`


Example:

\`\`\`

Sending packet 0

Sending packet 1

Sending packet 2

Sending packet 3


ACK received 0

ACK received 1

\`\`\`


Timeout handling:

\`\`\`

Timeout. Resending window


Sending packet 2

Sending packet 3

\`\`\`


Receiver behavior:

\* Accepts packets in order

\* Sends cumulative acknowledgements

\* Rejects out-of-order packets

\* Requests retransmission from missing packet onwards

---

**# Phase 7 — Selective Repeat Sliding Window Protocol**

Completed.

Implemented Selective Repeat reliability using:

\* Individual packet ACK handling

\* Receiver buffering

\* Individual packet timers

\* Selective packet retransmission


Working flow:

\`\`\`

Window:

[0][1][2][3]


Packet 1 lost


Receiver:

0 received

2 buffered

3 buffered


Only packet 1 retransmitted

\`\`\`


Sender behavior:

\* Maintains timer for each packet

\* Tracks acknowledged packets individually

\* Retransmits only expired packets


Receiver behavior:

\* Accepts packets within receiver window

\* Stores out-of-order packets

\* Sends ACK for every received packet

\* Delivers packets in correct order


Example:

\`\`\`

Sending packet 0

Sending packet 1

Sending packet 2

Sending packet 3


Timeout packet 1

Resending packet 1


ACK received 1

\`\`\`

---

## Supported Faults

### Packet Loss

Drops packets randomly.

Example:

```
FAULT: packet dropped
```

---

### Packet Corruption

Modifies packet data.

CRC detects corruption.

Example:

```
FAULT: packet corrupted

Receiver:
CRC mismatch
```

---

### Packet Delay

Adds artificial latency.

Example:

```
FAULT: delaying packet by 0.8s
```

---

### Packet Duplication

Sends duplicate packets.

Example:

```
FAULT: packet duplicated
Sending duplicate packet
```

Receiver handles duplicates by:

* Ignoring repeated data
* Sending ACK again

---

# Testing Completed

## Loss Test

Configuration:

```
Loss rate > 0
```

Observed:

```
Packet dropped

Timeout

Retransmission

ACK received
```

Result:

File transferred correctly.

---

## Corruption Test

Configuration:

```
Corruption enabled
```

Observed:

```
Corrupted packet received

CRC mismatch

Packet rejected
```

Result:

Incorrect data was not accepted.

---

## Delay Test

Configuration:

```
Artificial delay enabled
```

Observed:

```
Delayed packet

Timeout handling

Retransmission
```

Important:

Timeout must be greater than expected RTT.

Example:

```
DATA delay = 0.8s
ACK delay  = 0.8s

RTT ≈ 1.6s
```

---

## Duplication Test

Configuration:

```
Duplicate rate enabled
```

Observed:

```
Received DATA 0

Received DATA 0 again

Duplicate packet ignored
```

Result:

File contents remained correct.

---

# Checking Results

## Verify Received File

After transfer:

Check:

```
data/results/
```

Compare:

```
Original file

vs

Received file
```

Linux/macOS:

```bash
cmp original.txt received.txt
```

Windows:

```powershell
fc original.txt received.txt
```

No difference means successful transfer.

---

# Viewing Runtime Behaviour

The terminal logs show:

## Sender

Example:

```
Sending packet 0
Waiting for ACK
ACK received
```

---

## Proxy

Example:

```
Proxy received type=0 seq=0

FAULT: packet duplicated

Sending duplicate packet
```

---

## Receiver

Example:

```
Received DATA 0

Duplicate packet 0 ignored

ACK sent
```