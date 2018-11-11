import socket
import struct
import random
from tcppacket import TcpPacket as tcp_packet

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 20468)
socket.bind(server_address)


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
    if recv_syn > 0 and recv_ack == 0:  # If it's a SYN packet
        seq_num = random.randint(0, 10000)
        ack_num = recv_seq_number + 1
        packet = tcp_packet(syn=1, ack=1, sequence_number=seq_num, acknowledgement_number=ack_num)
        socket.sendto(packet.packet, address)
    elif recv_syn > 0 and recv_ack > 0:
        seq_num = recv_ack_number
        ack_num = recv_seq_number + 1
        packet = tcp_packet(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data='sending data')
        socket.sendto(packet.packet, address)
    elif recv_ack > 0:
        seq_num = recv_ack_number
        ack_num = recv_seq_number + packet_length
        packet = tcp_packet(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data="received...")
    elif recv_ack < 0:

