#########################################################################
#     wifi-me-niet.py - A simple python script which logs wifi probe requests.
#     Author - jerryhopper
#########################################################################

# apt-get install build-essential libssl-dev libffi-dev python3-dev
# pip3 install --upgrade pip
# pip3 install setuptools scapy OuiLookup redis cryptography PyCrypto


from datetime import datetime
from scapy.all import sniff, Dot11
import logging
import os
import signal
import time
import json
import sys
import redis
from datetime import timedelta
from OuiLookup import OuiLookup


from src.monitor import setup_monitor
from src.notify import donotify


#OuiLookup().update()


# Expire in minutes
SETTINGS_REDISEXPIRE=24*60
# in minutes
SETTINGS_RECENTSEEN=5
# amount of macs before being submitted.
SETTINGS_SENDCUE=10
# verbosity
SETTINGS_VERBOSE=True

# notify-url.
SETTINGS_NOTIFYURL="https://wifi-me-niet.jerryhopper.com/api/donotfollowtest"




r = redis.Redis(charset="utf-8", decode_responses=True)


def clear_redis(what):
	if what =="all":
		r.flushall()
		if SETTINGS_VERBOSE == True:
			print("Redis data deleted!")
		#exit()



def seenrecently(identifier):
	# returns true if exists.
	return r.exists( "R"+identifier )

def ignore(identifier):
	# returns true if exists.
	return r.exists( identifier )


def set_received(identifier,pkt):
	macinfo = {}
	macinfo["ssid"] = str(pkt.info,'utf-8')
	macinfo["signal"]= str(pkt.dBm_AntSignal)
	macinfo["rate"] = str(pkt.Rate)
	# + pkt.addr2.upper()
	if SETTINGS_VERBOSE == True:
		print( get_temp()+' '+str(datetime.now()) +' ' +  pkt.addr2  + ' ' + str(OuiLookup().query(pkt.addr2.upper())[0][pkt.addr2.upper().replace(":", "")])  +' ** dbm: '+ str(pkt.dBm_AntSignal) +'  rate: ' + str(pkt.Rate)  + ' SSID:"' + str(pkt.info,'utf-8')+'"' )
		#print( get_temp()+' '+str(datetime.now()) +' ' + pkt.addr1  +' ' + pkt.addr2  + ' '+ pkt.addr3 +' ' +' ** dbm: '+ str(pkt.dBm_AntSignal) +'  rate: ' + str(pkt.Rate)  + ' SSID:"' + str(pkt.info,'utf-8')+'"' )
	#print( get_temp()+' '+str(datetime.now()) +' 00:00:00:??:??:??'  + ' '+ str(OuiLookup().query(pkt.addr2.upper())[0][pkt.addr2.upper().replace(":", "")]) + ' '+' ** dbm: '+ macinfo['signal'] +'  rate: ' + macinfo['rate']  + ' SSID:"' + macinfo['ssid'] + '"' )
	# set the ignore flag in redis.
	macJson = json.dumps(macinfo)
	r.setex( identifier , timedelta(minutes=SETTINGS_REDISEXPIRE) , macJson )
	# set the recentseen flag in redis
	r.setex( "R"+identifier , timedelta(minutes=SETTINGS_RECENTSEEN) , macJson )

	r.hset("cue", identifier , macJson )
	if r.hlen("cue") > SETTINGS_SENDCUE:
		donotify( r.hgetall("cue"),SETTINGS_NOTIFYURL )
		r.delete("cue")


def get_identifier(identifier):
	json.loads(r.get( identifier ))







def is_root():
	if not os.geteuid() ==0:
		if SETTINGS_VERBOSE == True:
			print("Error! you must be root!")
		exit(1)



def get_temp():
	return str(float(open('/sys/class/thermal/thermal_zone0/temp', 'r').read().replace('\n', ''))/1000)
	#return str( os.system('echo $(cat /sys/class/thermal/thermal_zone0/temp)'))


def handle_packet(pkt):
	# check if the packet is a probe-request
	if not pkt.haslayer(Dot11):
		return
	# check if the packet is a probe-request
	if pkt.type == 0 and pkt.subtype == 4:
		# make sure mac is uppercase
		curmac = pkt.addr2.upper()
		# remove the colon's
		shortmac = curmac.replace(":","")
		# check if the shortmac has been seen in the last X minutes.
		if seenrecently(shortmac) == 1:
			return
		# check if the shortmac should be ingored.
		if ignore(shortmac) == 0:
			set_received(shortmac,pkt)
			#print( get_temp()+' '+str(datetime.now()) +' ' + pkt.addr1  +' ' + pkt.addr2  + ' '+ pkt.addr3 +' ' +' ** dbm: '+ str(pkt.dBm_AntSignal) +'  rate: ' + str(pkt.Rate)  + ' SSID:"' + str(pkt.info,'utf-8')+'"' )
		#else:
		#	print( '>>SKIP>>> '+ get_temp()+' '+str(datetime.now()) +' ' + pkt.addr1  +' ' + pkt.addr2  + ' '+ pkt.addr3 +' ' +' ** dbm: '+ str(pkt.dBm_AntSignal) +'  rate: ' + str(pkt.Rate)  + ' SSID:"' + str(pkt.info,'utf-8')+'"' )

def main():
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--interface', '-i', default="", help='Specify the interface.  Example: --interface wlan0')
	parser.add_argument('--clear', '-c', default="", help='Clear redis data' )
	parser.add_argument('--verbose', '-v', default="true", help='Verbosity: output to screen true/false' )
	parser.add_argument('--url', '-u', default="https://wifi-me-niet.jerryhopper.com/api/donotfollowtest", help='Notify url' )

	args = parser.parse_args()
	global SETTINGS_VERBOSE, SETTINGS_NOTIFYURL
	if args.url !="":
		SETTINGS_NOTIFYURL = args.url
	#
	if args.verbose == "false":
		SETTINGS_VERBOSE = False
	else:
		SETTINGS_VERBOSE = True
	#
	if SETTINGS_VERBOSE == True:
		logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename='wifiscanner.log',level=logging.DEBUG) #setup logging to file
	#
	if SETTINGS_VERBOSE == True:
		logging.info('\n'+'Wifi-me-niet Scanner Initialized'+ '\n') #announce that it has started to log file with yellow color
	#
	if SETTINGS_VERBOSE == True:
		print('\n' + '\033[93m' + 'Wifi-me-niet Scanner Initialized' + '\033[0m' + '\n') #announce that it has started to command line with yellow color		(/n is newline)
	#
	clear_redis(args.clear)
	iface = setup_monitor(args.interface,SETTINGS_VERBOSE)
	if SETTINGS_VERBOSE == True:
		print('\n' + '\033[93m' + 'Wifi-me-niet Scanner ('+ iface+') Started' + '\033[0m' + '\n')
	sniff(iface=iface, prn=handle_packet, store=0, count=0)
	try:
		sniff(iface=iface, prn=handle_packet, store=0, count=0)
	except:
		print("Exception!")
	sys.exit(1)

def signal_exit(signal,frame):
	if SETTINGS_VERBOSE == True:
		print("Signal exit")
	sys.exit(1)

def signal_handler(signal,frame):
	if SETTINGS_VERBOSE == True:
		print("Aborted by user.")
	os.system('kill -9 '+ str(os.getpid()))
	sys.exit(1)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	is_root()
	main()
