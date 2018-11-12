import socket
import struct


#                      1 1 1 1 1 1 1 1 1 1 2 2 2 2 2 2 2 2 2 2 3 3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-------------------------------+-------------------------------+
# |          Source Port          |       Destination Port        |
# +-------------------------------+-------------------------------+
# |                       Sequence Number                         |
# +---------------------------------------------------------------+
# |                      Acknowledge Number                       |
# +-------+-----+-+-+-+-+-+-+-+-+-+-------------------------------+
# |  Data | RSV |N|C|E|U|A|P|R|S|F|                               |
# | Offset|0 0 0|S|W|C|R|C|S|S|Y|I|          Window Size          |
# |       |     | |R|E|G|K|H|T|N|N|                               |
# +-------+-----+-+-+-+-+-+-+-+-+-+-------------------------------+
# |           Checksum            |  Urgent Pointer (if URG set)  |
# +-------------------------------+-------------------------------+
# |                   Options (if data offset > 5)                |
# +---------------------------------------------------------------+

class TcpPacket:
    def __init__(self, sequence_number=0, acknowledgement_number=0, buffer_size=4096, data='', ack=0, syn=0, fin=0):
        self.raw = None
        self.sequence_number = sequence_number
        self.acknowledgement_number = acknowledgement_number
        self.buffer_size = buffer_size
        self.flag = (ack << 7) + (syn << 6) + (fin << 5)
        self.data = bytearray(data.encode('utf-8'))
        self.packet = None
        self.assemble_tcp_fields()

    def assemble_tcp_fields(self):
        self.raw = struct.pack('!LLHB',  # Data Structure Representation
                               self.sequence_number,  # Sequence
                               self.acknowledgement_number,  # Acknowledgement Sequence
                               self.buffer_size,  # TCP Windows
                               self.flag
                               )

        self.packet = self.raw + self.data
