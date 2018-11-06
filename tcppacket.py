import socket
import struct


class TcpPacket:
    def __init__(self, source_port=1024, destination_port=80, source_ip="192.168.0.1", destination_ip="127.0.0.1",
                 sequence_number=0, acknoledgement_number=0, buffer_size=4096, data='Empty'):
        self.source_port = source_port
        self.destination_port = destination_port
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.data = data
        self.raw = None
        self.create_tcp_fields(sequence_number, acknoledgement_number, buffer_size)

    def create_tcp_fields(self, sequence_number, acknoledgement_number, buffer_size):
        # ---- [ Source Port ]
        self.tcp_src = self.source_port

        # ---- [ Destination Port ]
        self.tcp_dst = self.destination_port

        # ---- [ TCP Sequence Number]
        self.tcp_seq = sequence_number

        # ---- [ TCP Acknowledgement Number]
        self.tcp_ack_seq = acknoledgement_number

        # ---- [ Header Length ]
        self.tcp_hdr_len = 80

        # ---- [ TCP Flags ]
        tcp_flags_rsv = (0 << 9)
        tcp_flags_noc = (0 << 8)
        tcp_flags_cwr = (0 << 7)
        tcp_flags_ecn = (0 << 6)
        tcp_flags_urg = (0 << 5)
        tcp_flags_ack = (0 << 4)
        tcp_flags_psh = (0 << 3)
        tcp_flags_rst = (0 << 2)
        tcp_flags_syn = (1 << 1)
        tcp_flags_fin = (0)

        self.tcp_flags = tcp_flags_rsv + tcp_flags_noc + tcp_flags_cwr + \
                         tcp_flags_ecn + tcp_flags_urg + tcp_flags_ack + \
                         tcp_flags_psh + tcp_flags_rst + tcp_flags_syn + tcp_flags_fin

        # ---- [ TCP Window Size ]
        self.tcp_wdw = buffer_size

        # ---- [ TCP CheckSum ]
        self.tcp_chksum = 0

        # ---- [ TCP Urgent Pointer ]
        self.tcp_urg_ptr = 0

        return

    def assemble_tcp_fields(self):
        self.raw = struct.pack('!HHLLBBHHH',  # Data Structure Representation
                               self.tcp_src,  # Source IP
                               self.tcp_dst,  # Destination IP
                               self.tcp_seq,  # Sequence
                               self.tcp_ack_seq,  # Acknownlegment Sequence
                               self.tcp_hdr_len,  # Header Length
                               self.tcp_flags,  # TCP Flags
                               self.tcp_wdw,  # TCP Windows
                               self.tcp_chksum,  # TCP cheksum
                               self.tcp_urg_ptr  # TCP Urgent Pointer
                               )

        self.calculate_chksum()  # Call Calculate CheckSum
        return

    def calculate_chksum(self):
        # src_addr = socket.inet_aton(self.source_ip)
        # dest_addr = socket.inet_aton(self.destination_ip)
        # placeholder = 0
        # protocol = socket.IPPROTO_TCP
        # tcp_len = len(self.raw) + len(self.data)
        #
        # psh = struct.pack('!4s4sBBH',
        #                   src_addr,
        #                   dest_addr,
        #                   placeholder,
        #                   protocol,
        #                   tcp_len
        #                   )

        psh = self.raw + bytes(self.data, encoding='utf-8')

        self.tcp_chksum = self.chksum(psh)

        self.reassemble_tcp_fields()

        return

    def chksum(self, msg):
        s = 0  # Binary Sum

        # loop taking 2 characters at a time
        for i in range(0, len(msg) - 2, 2):
            a = msg[i]
            b = msg[i + 1]
            s = s + (a + (b << 8))

        # One's Complement
        s = s + (s >> 16)
        s = ~s & 0xffff
        return s

    def reassemble_tcp_fields(self):
        self.raw = struct.pack('!HHLLBBH',
                               self.tcp_src,
                               self.tcp_dst,
                               self.tcp_seq,
                               self.tcp_ack_seq,
                               self.tcp_hdr_len,
                               self.tcp_flags,
                               self.tcp_wdw
                               ) + struct.pack("H", self.tcp_chksum) + struct.pack('!H', self.tcp_urg_ptr)
        return



if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    tcp = TcpPacket()
    tcp.assemble_tcp_fields()
    print(tcp.tcp_wdw)
    s.sendto(tcp.raw, ('127.0.0.1', 0))
