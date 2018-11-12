import socket
import struct
import random
import time
import queue
from tcppacket import TcpPacket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 20468)
socket.bind(server_address)
expected_sequence_number = 0
socket.settimeout(0.6)


def connect(socket):
    data, address = socket.recvfrom(4096)
    header_content = struct.unpack('!LLHB', data[:11])
    recv_seq_number = header_content[0]
    recv_ack_number = header_content[1]
    recv_flag = header_content[3]
    recv_ack = recv_flag & 128
    recv_syn = recv_flag & 64
    # SYN Packet
    if recv_syn > 0 and recv_ack == 0:
        seq_num = random.randint(0, 10000)
        ack_num = recv_seq_number + 1
        packet = TcpPacket(syn=1, ack=1, sequence_number=seq_num, acknowledgement_number=ack_num)
        expected_sequence_number = ack_num
        last_acknowledgement_number = recv_ack_number
        socket.sendto(packet.packet, address)
        return expected_sequence_number, last_acknowledgement_number

recv = connect(socket)
while recv is None:
    recv = connect(socket)
expected_sequence_number, last_acknowledgement_number = recv
# duplicate_couter = 0
# cwnd_size = 1
# cwnd_state = 0
# cache = []
print(recv)

while True:
    data, address = socket.recvfrom(4096)
    packet_length = len(data)
    header_content = struct.unpack('!LLHB', data[:11])
    recv_seq_number = header_content[0]
    recv_ack_number = header_content[1]
    recv_buffer = header_content[2]
    recv_flag = header_content[3]
    recv_ack = recv_flag & 128
    recv_syn = recv_flag & 64
    recv_fin = recv_flag & 32
    print(recv_seq_number, recv_ack_number, data[11:])
    if recv_ack == 0:
        if expected_sequence_number == recv_seq_number:
            seq_num = recv_ack_number
            ack_num = recv_seq_number + packet_length
            expected_sequence_number = ack_num
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data="received...")
        else:
            seq_num = recv_ack_number
            ack_num = expected_sequence_number
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data="missed...")
    socket.sendto(packet.packet, address)