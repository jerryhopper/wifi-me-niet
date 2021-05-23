import os
import sys


def listToString(s):
    # initialize an empty string
    str1 = " "
    # return string
    return (str1.join(s))


def list_wireless():
	output = os.popen("iwconfig 2>&1 | grep ESSID | sed 's/\"//g' | cut -f1  -d' '").read()
	result =  output.split('\n')[:-1]
	result.sort()
	return result

def list_monitor_wireless():
	output = os.popen("iwconfig 2>&1 | grep Monitor | sed 's/\"//g' | cut -f1  -d' '").read()
	result =  output.split('\n')[:-1]
	result.sort()
	return result

def is_kali():
	output = os.popen("lsb_release -d|awk -F ' ' '{print $2}'").read().strip().upper()
	# print(output)
	if output == "KALI" :
		return True
	else:
		return False

def setup_monitor(iface,SETTINGS_VERBOSE):
	# Check if we are on a KALI distribution.
	wireless_adapters=list_wireless()
	monitor_adapters=list_monitor_wireless()
	if iface=="":
		if SETTINGS_VERBOSE == True:
			print("Info: no --interface  specified. ")
	else:
		if SETTINGS_VERBOSE == True:
			print("Info: --interface '"+iface+"'")
	if len(wireless_adapters)==0:
		if SETTINGS_VERBOSE == True:
			print("Error: no wireless adapters found. ")
		exit()
	if iface != "" and iface not in  wireless_adapters:
		if SETTINGS_VERBOSE == True:
			print("Error:  "+iface+" is not available.")
		exit()
	if SETTINGS_VERBOSE == True:
		print("Info: Found "+str(len(wireless_adapters))+" wireless adapters. "+listToString(wireless_adapters))
	if is_kali() == True :
		if SETTINGS_VERBOSE == True:
			print("Info: Kali distribution detected.")
		if len(monitor_adapters)!=0:
			if SETTINGS_VERBOSE == True:
				print("Info: "+str(len(monitor_adapters))+" adapters found in monitoring state!")
			if iface=="":
				if wireless_adapters[0]+"mon" not in  monitor_adapters:
					if SETTINGS_VERBOSE == True:
						print("Info: Enabling monitor mode for default adapter. "+wireless_adapters[0])
					os.system('sudo airmon-ng check kill')
					os.system('sudo airmon-ng start '+wireless_adapters[0])
					iface=wireless_adapters[0]
					return iface+'mon'
				else:
					# the adapter is already in monitor mode
					if SETTINGS_VERBOSE == True:
						print("Info: Using default adapter. "+wireless_adapters[0])
					iface=monitor_adapters[0]
					return iface
			else:
				if iface+"mon" in monitor_adapters:
					if SETTINGS_VERBOSE == True:
						print("Info: interface '"+iface+"' is already in monitor mode.");
					return iface+"mon"
				else:
					if SETTINGS_VERBOSE == True:
						print("Using adapter. "+iface)
					os.system('sudo systemctl stop wpa_supplicant.service')
					os.system('sudo systemctl stop NetworkManager.service')
					os.system('sudo airmon-ng check kill')
					os.system('sudo airmon-ng start '+iface)
					return iface+"mon"
		else:
			# No adapters found in monitor mode
			if SETTINGS_VERBOSE == True:
				print("Info: Found "+str(len(monitor_adapters))+" wireless adapters in monitoring mode. "+listToString(monitor_adapters))
			if iface=="":
				iface=wireless_adapters[0]
			if SETTINGS_VERBOSE == True:
				print("Info: Enabling monitor mode for "+iface)
			os.system('sudo airmon-ng check kill')
			os.system('sudo airmon-ng start '+iface)
			return iface+'mon'
		return iface

	# Generic device
	print("Bringing down "+ iface +"")
	try:
		os.system('sudo ip link set ' + iface +' down')
	except:
		if SETTINGS_VERBOSE == True:
			print("Failed to work with "+ iface +"!")
		sys.exit(1)
	try:
		if SETTINGS_VERBOSE == True:
			print("Setting up monitor-mode on "+ iface +"")
		os.system('iw '+ iface +' set monitor none')
	except:
		if SETTINGS_VERBOSE == True:
			print("Failed Setting up monitor-mode on "+ iface +"!")
		sys.exit(1)
	if SETTINGS_VERBOSE == True:
		print("Bringing up "+ iface +"")
	os.system('ip link set ' + iface +' up')
	return iface
