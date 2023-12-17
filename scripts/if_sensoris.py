#!/usr/bin/env python

import os
import sys
import time
import json
import struct
import threading

#from socket import *
import socket
import rospy
import roslibpy
from std_msgs.msg import String

# file_path = "/home/katech/sejong/src/obu_interface/scripts/json/pvd.json"
file_path = "/mnt/hgfs/vm_shared/sejong/src/if_sensoris/scripts/json/sensorRawRequestSTART.json"

with open(file_path, 'rw') as file:
    global data
    data = json.load(file)
    # print(data)

global pvd_string
pvd_string = json.dumps(data).encode('UTF-8')

HOST = '192.168.137.200'
# HOST = socket.gethostname()
PORT = 9200

# TEST UDP Local host
# HOST = '192.168.1.55'
# PORT = 9100


Header = []
packet_seq = {0, 0, 0, 0}
timestamp = {0, 0, 0, 0, 0, 0, 0, 0}
packet_type = 0
body_length = {0, 0, 0, 0}

Body = []
data_length = {0, 0, 0, 0}

PVD_packet = []

class PVD_encoding_Thread(threading.Thread):
    def __init__(self, client_socket):
        super(PVD_encoding_Thread, self).__init__()
        rospy.init_node('if_sensoris_node', anonymous=True)

        self.client = client_socket
        self.pvd_packet_seq = 0
        self.timestamepq = 0
        self.body_length = 0

    def Encoding_Header(self, Header):
        self.Header = Header

        self.packet_seq = struct.pack('>i', self.pvd_packet_seq)
        self.pvd_packet_seq += 1

        self.timestamp = struct.pack('>q', self.timestamepq)
        self.timestamepq += 1

        self.packet_type = struct.pack('B',31)  # PVD

        self.body_length = struct.pack('>i',len(pvd_string)+4) #self.Cal_Body_Length(self.pvd_string)

        # self.Header.append(self.packet_seq)
        # self.Header.append(self.timestamp)
        # self.Header.append(self.packet_type)
        # self.Header.append(self.body_length)
        self.Header = self.packet_seq + self.timestamp + self.packet_type + self.body_length

        data_length = struct.pack('>i', len(pvd_string))

        self.Body = data_length + pvd_string

        # print(self.Header)
        # print(self.Body)

        self.PVD_packet = self.Header + self.Body
        # print(self.PVD_packet)

    def run(self):
        #      self.open_pvd_json()
        # while not rospy.is_shutdown():
         
          self.Encoding_Header(Header)

        # print(self.PVD_packet)
        # self.pvd_string = json.dumps(data).encode('UTF-8')#, indent=2)
        # body = bytes(pvd_string)
        # print(pvd_string)
          self.client.sendall(self.PVD_packet)
        # self.client.sendto(self.PVD_packet, (HOST, PORT))
          while not rospy.is_shutdown():
            time.sleep(1)


def main():
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # client_socket.bind((HOST, PORT))

    thread_pvd = PVD_encoding_Thread(client_socket)

    thread_pvd.start()

    thread_pvd.join()

    client_socket.close()



if __name__ == '__main__':
    try:  
      main()

    except rospy.ROSInterruptException:
      pass

#  pvd_string = json.dumps(data).encode('UTF-8')#, indent=2)
#  body = bytes(pvd_string)


#  thread_pvd = PVD_encoding_Thread(RelaySW_Client)


#  except Exception as e:
#    print(e)
