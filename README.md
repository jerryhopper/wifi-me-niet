# wifi-me-niet
Wifi-me-niet scanner &amp; submitter



Usage:

Set your network-adapter in monitor mode.

<pre>
sudo ip link set wlan1 down
sudo iw wlan1 set monitor none
sudo ip link set wlan1 up
</pre>

start the scanner

./wifi-me-niet.py --interface wlan1

