from tcppacket import TcpPacket
import socket
import random
import struct

# Create a TCP/IP socket
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Connect the socket to the port where the server is listening

def connect(server_address, server_port, socket):
    server = (server_address, server_port)
    sequence_number = random.randint(0, 10000)
    packet = TcpPacket(syn=1, ack=0, sequence_number=sequence_number)
    socket.sendto(packet.packet, server)
    # SYN + ACK Packet
    data, address = socket.recvfrom(4096)
    header_content = struct.unpack('!LLHB', data[:11])
    recv_seq_number = header_content[0]
    recv_ack_number = header_content[1]
    recv_flag = header_content[3]
    recv_ack = recv_flag & 128
    recv_syn = recv_flag & 64
    print(recv_ack, recv_syn)
    if recv_syn > 0 and recv_ack > 0:
        seq_num = recv_ack_number
        ack_num = recv_seq_number + 1
        expected_sequence_number = ack_num
        last_acknowledgement_number = recv_ack_number
        packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data='Sending data')
        socket.sendto(packet.packet, address)
    return expected_sequence_number, last_acknowledgement_number


recv = connect('127.0.0.1', 20468, socket)
while recv is None:
    recv = connect(socket)
expected_sequence_number, last_acknowledgement_number = recv
print(recv)
duplicate_counter = 0
cache = []

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
    if recv_ack > 0:
        if last_acknowledgement_number == recv_ack_number:
            duplicate_couter += 1
        else:
            duplicate_couter = 0
            if len(cache) != 0:
                cache.pop(0)
        if duplicate_couter == 3:
            seq_num = last_acknowledgement_number
            packet = cache[0]
            socket.sendto(packet.packet, address)
            continue
        if expected_sequence_number == recv_seq_number:
            seq_num = recv_ack_number
            ack_num = recv_seq_number + packet_length
            expected_sequence_number = ack_num
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data="received...")
            cache.append(packet)
        else:
            seq_num = recv_ack_number
            ack_num = expected_sequence_number
            packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data="missed...")
        socket.sendto(packet.packet, address)