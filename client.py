from tcppacket import TcpPacket
import socket
import random

# Create a TCP/IP socket
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Connect the socket to the port where the server is listening

def connect(server_address, port_number):
    server = (server_address, port_number)
    sequence_number = random.randint(0, 10000)
    packet = TcpPacket(syn=1, ack=0, sequence_number=sequence_number)
    socket.sendto(packet.packet, server)


connect('127.0.0.1', 20468)
