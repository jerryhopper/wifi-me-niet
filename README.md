# wifi-me-niet
Wifi-me-niet scanner &amp; submitter



Usage:

Set your network-adapter in monitor mode. (make sure your wireless adapter supports monitoring mode)

<pre>
sudo ip link set wlan1 down
sudo iw wlan1 set monitor none
sudo ip link set wlan1 up
</pre>

start the scanner

<pre>
./wifi-me-niet.py --interface wlan1
</pre>

Or, edit 'wifi-me-niet' file and set the correct wireless adapter.

Make the file executable using :  chmod +x wifi-me-niet

And then run the ./wifi-me-niet script.



Compatible USB adapter

https://www.wirelesshack.org/best-kali-linux-compatible-usb-adapter-dongles.html
