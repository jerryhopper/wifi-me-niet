#########################################################################
#     wifi-me-niet.py - A simple python script which logs wifi probe requests.
#     Author - jerryhopper
#########################################################################

from datetime import datetime
from scapy.all import sniff, Dot11
import logging
import time
from notify import *

IGNORE_LIST = set(['00:00:00:00:00:00'])

wificard = 'wlan1'


def handle_packet(pkt):
        global IGNORE_LIST
	if not pkt.haslayer(Dot11):
		return
        # pkt.type: subtype used to be 8 (APs) but is now 4 (Probe Requests)
	if pkt.type == 0 and pkt.subtype == 4:
		curmac = pkt.addr2
		curmac = curmac.upper()
		if curmac not in IGNORE_LIST: #If not registered as ignored
			IGNORE_LIST.add(curmac)
			notify(curmac, "", "")
		if len(IGNORE_LIST) > 5000:
			IGNORE_LIST = set(['00:00:00:00:00:00', curmac])


def main():
	logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename='wifiscanner.log',level=logging.DEBUG) #setup logging to file
	logging.info('\n'+'Wifi-me-niet Scanner Initialized'+ '\n') #announce that it has started to log file with yellow color
	print('\n' + '\033[93m' + 'Wifi-me-niet Scanner Initialized' + '\033[0m' + '\n') #announce that it has started to command line with yellow color		(/n is newline)
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--interface', '-i', default=wificard, help='monitor mode enabled interface')
	args = parser.parse_args()
	sniff(iface=args.interface, prn=handle_packet, store=0, count=0)

if __name__ == '__main__':
	main()
