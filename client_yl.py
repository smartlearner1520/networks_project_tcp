from tcppacket import TcpPacket
import socket
import random
import struct

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)


# Connect the socket to the port where the server is listening

def connect(server_address, server_port, sock):
    server = (server_address, server_port)
    seq_number = random.randint(0, 10000)
    packet = TcpPacket(syn=1, ack=0, sequence_number=seq_number)
    sock.sendto(packet.packet, server)
    # SYN + ACK Packet
    data, address = sock.recvfrom(4096)
    header_content = struct.unpack('!LLHB', data[:11])
    recv_seq_number = header_content[0]
    recv_ack_number = header_content[1]
    recv_flag = header_content[3]
    recv_ack = recv_flag & 128
    recv_syn = recv_flag & 64
    if recv_syn > 0 and recv_ack > 0:
        seq_num = recv_ack_number
        ack_num = recv_seq_number + 1
        expected_sequence_number = ack_num
        next_acknowledgement_number = recv_ack_number + 1
        packet = TcpPacket(ack=1, sequence_number=seq_num, acknowledgement_number=ack_num, data='Sending data')
        sock.sendto(packet.packet, address)
        return expected_sequence_number, next_acknowledgement_number, packet


recv = connect('127.0.0.1', 20468, sock)
server = ('127.0.0.1', 20468)
while recv is None:
    print(recv)
    recv = connect('127.0.0.1', 20468, sock)
expected_sequence_number, next_acknowledgement_number, packet = recv
duplicate_counter = 0
cwnd_size = 1
congestion_state = 0
cache = [packet]
temp_ack_list = []
seq_number = next_acknowledgement_number
packet_size = 24
temp_seq_number = 0

while True:
    print(cwnd_size)
    temp_ack_list = []
    try:
        for i in range(cwnd_size):
            data, address = sock.recvfrom(4096)
            packet_length = len(data)
            header_content = struct.unpack('!LLHB', data[:11])
            recv_ack_number = header_content[1]
            temp_ack_list.append(recv_ack_number)
            recv_buffer = header_content[2]
        max_cwnd_size = recv_buffer // packet_size
        #print(data[11:])
        print (seq_number)
        print(max(temp_ack_list))
        if max(temp_ack_list) == seq_number:
            cache = cache[cwnd_size:]
            print("Cache size ", len(cache))
            if congestion_state:
                cwnd_size += 1
            else:
                cwnd_size *= 2
            #if cwnd_size > max_cwnd_size:
                #cwnd_size = max_cwnd_size
        else:
            print("------1-------", max(temp_ack_list))
            print(temp_ack_list)
            cache = cache[temp_ack_list.index(max(temp_ack_list)):]
            if cwnd_size == 1:
                cwnd_size = 1
            else:
                cwnd_size = cwnd_size // 2
            congestion_state = 1
            #print("-------4-------", seq_number)
            if len(temp_ack_list) ==1:
                temp_seq_number = max(temp_ack_list)-13
            else:
                temp_seq_number = temp_ack_list[temp_ack_list.index(max(temp_ack_list))-1]
            seq_number = max(temp_ack_list)
            print("-------2-------", temp_seq_number)
    except socket.timeout:
        if max(temp_ack_list) == seq_number:
            cache = cache[cwnd_size:]
        else:
            cache = cache[temp_ack_list.index(max(temp_ack_list)):]
            if len(temp_ack_list) ==1:
                temp_seq_number = max(temp_ack_list)-13
            else:
                temp_seq_number = temp_ack_list[temp_ack_list.index(max(temp_ack_list))-1]
            seq_number = max(temp_ack_list)
        cwnd_size = 1
        congestion_state = 0

    batch_size = 0
    for i in range(cwnd_size):
        if i < len(cache):
            packet = cache[i]
            if temp_seq_number == max(temp_ack_list):
                seq_number += len(packet.data)
            else:
                temp_seq_number += len(packet.data)
            print("----------3--------", temp_seq_number, seq_number)
            if len(cache) == 1:
                print("===================================")
                cache = []
        else:
            packet = TcpPacket(sequence_number=seq_number, data='random packet')
            cache.append(packet)
            seq_number = seq_number + len(packet.data)

        sock.sendto(packet.packet, server)
