# wifi-me-niet
Wifi-me-niet scanner &amp; submitter



Usage:

Set your network-adapter in monitor mode.

sudo ip link set wlan1 down

sudo iw wlan1 set monitor none

sudo ip link set wlan1 up



./wifi-me-niet.py --interface wlan1

