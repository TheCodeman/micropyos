import uos
remoteIP='192.168.0.3'
remotePath='/Users/thecodeman/Projects/MicroPython_ESP32_psRAM_LoBo/MicroPython_BUILD/components/internalfs_image/image/'
uname='username'
upass='password'
wifiSSID = 'ssid'
wifiPass = 'wifipassword'

sdCardCLK = 4
sdCardMOSI = 12
sdCardMiso = 2
sdCardCS =15

timeZone= 'PST8PDT'


autostartWiFi = True
autoMountSD = True

def initSDCard():
#	uos.sdconfig(uos.SDMODE_4LINE, sdCardCLK , sdCardMOSI, sdCardMiso, sdCardCS)
	uos.sdconfig(uos.SDMODE_4LINE)
	try:
	    uos.mountsd()
	except Exception as e:
	    print(e)

