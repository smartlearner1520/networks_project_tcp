import socket
import struct
import random
import time
from tcppacket import TcpPacket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 20468)
socket.bind(server_address)
expected_sequence_number = 0

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
    seq_num = 0
    ack_num = 0
    print(recv_ack, recv_syn, recv_fin)
    # SYN Packet
    if recv_syn > 0 and recv_ack == 0:
        seq_num = random.randint(0, 10000)
        ack_num = recv_seq_number + 1
        expected_sequence_number = ack_num
        packet = TcpPacket(syn=1, ack=1, sequence_number=seq_num, acknowledgement_number=ack_num)
        socket.sendto(packet.packet, address)
    # SYN + ACK Packet
    elif recv_syn > 0 and recv_ack > 0:
        if expected_sequence_number == seq_num:
            seq_num = recv_ack_number
            ack_num = recv_seq_number + 1
            expected_sequence_number = ack_num
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data='sending data')
            socket.sendto(packet.packet, address)
        else:
            seq_num = recv_ack_number
            ack_num = expected_sequence_number
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data='Missed Packet!')
    # ACK Packet
    elif recv_ack > 0:
        if expected_sequence_number == seq_num:
            seq_num = recv_ack_number
            ack_num = recv_seq_number + packet_length
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data="received...")
        else:
            seq_num = recv_ack_number
            ack_num = expected_sequence_number
            packet = TcpPacket()


