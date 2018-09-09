import uos
'''
Settings file for micropyos

'''

# Remote ip of the ssh server to scp to
remoteIP= '192.168.0.3'		<- Set ip address of the server to connect to
# path to scp to and from
remotePath='/Users/thecodeman/Projects/micropyos/'	<- Set path on server
# username on server for scp
uname='username'			<- User Name for server
upass='password'			<- Password for server
# wifi username and password 
wifiSSID = 'ssid'			<- WiFi SSID
wifiPass = 'wifipassword' 	<- WiFi Password
wifiTimeout = 50
# username and password for telnet server 
telnetUname = 'micropyos'	<- User Name for telnet server on MicroPython 
telnetPass = 'esp32'		<- User Password for telnet server on MicroPython 

# name for nDNS so you can connect remotely using name 
# using name below you  can telnet to myesp32.local or ping myesp32.local to get devices ip address
networkName = 'myesp32' 	<- nDNS Name
# your time zone
timeZone= 'PST8PDT'

# Autostart options
autostartWiFi = True	
autoMountSD = True
autoStartTelnet = True
autoStartmDNS = True

sdCardCLK = 4
sdCardMOSI = 12
sdCardMiso = 2
sdCardCS =15

def initSDCard():
#	uos.sdconfig(uos.SDMODE_4LINE, sdCardCLK , sdCardMOSI, sdCardMiso, sdCardCS)
	uos.sdconfig(uos.SDMODE_4LINE)
	try:
	    uos.mountsd()
	except Exception as e:
	    print(e)

