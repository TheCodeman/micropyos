'''
Small Simple OS for MicroPython

The MIT License (MIT)
Copyright (c) 2018 Ken Segler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

import uos
import machine
from pye import pye
import utime
import ssh
import sys
import network
import urequests
import settings
networkUp=False
currentDir = '/flash'
version = '0.2.0'
redLED = machine.Pin(5, machine.Pin.OUT)
timer = machine.Timer(0)
ledState=0;
def getch():
    return sys.stdin.read(1)

def intCallback(timer):
    global ledState
    if ledState==0:
        redLED.value(1)
        ledState=1
    else:
        redLED.value(0)
        ledState=0


def reload(mod):
    import sys
    mod_name = mod.__name__
    del sys.modules[mod_name]
    return __import__(mod_name)


if settings.autostartWiFi:
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.connect(settings.wifiSSID, settings.wifiPass)
    print('WiFI Connecting To {0}'.format(settings.wifiSSID) )
    while nic.isconnected()==False:
        print('*', end='')
        utime.sleep_ms(100)
        settings.wifiTimeout -= 1
        if settings.wifiTimeout == 0:
            break
    if settings.wifiTimeout !=0 and nic.isconnected():
        print('\n\rConnected ',nic.ifconfig())
        if settings.autoStartmDNS:
            mdns=network.mDNS()
            mdns.start(settings.networkName, 'MicroPython') 
            mdns.addService('_telnet', '_tcp', 23, "MicroPython", {"board": "ESP32", "service": "mPy Telnet REPL"})
        redLED.value(1)
        networkUp=True
    else:
        print('\n\rCould not Connect to wifi')
if settings.autoMountSD:
    settings.initSDCard()

if settings.autoStartTelnet:
    network.telnet.start(user=settings.telnetUname, password=settings.telnetPass, timeout=300)

rtc=machine.RTC()
if not rtc.synced():
    rtc.ntp_sync(server="pool.ntp.org", tz=settings.timeZone)
    utime.sleep_ms(1000)
    print("Time set to: {}".format(utime.strftime("%c", utime.localtime())))


def main():
    print(' __   __  ___   _______  ______    _______  _______  __   __  _______  _______ ')
    print('|  |_|  ||   | |       ||    _ |  |       ||       ||  | |  ||       ||       |')
    print('|       ||   | |       ||   | ||  |   _   ||    _  ||  |_|  ||   _   ||  _____|')
    print('|       ||   | |       ||   |_||_ |  | |  ||   |_| ||       ||  | |  || |_____ ')
    print('|       ||   | |      _||    __  ||  |_|  ||    ___||_     _||  |_|  ||_____  |')
    print('| ||_|| ||   | |     |_ |   |  | ||       ||   |      |   |  |       | _____| |')
    print('|_|   |_||___| |_______||___|  |_||_______||___|      |___|  |_______||_______|')
    print('small OS for micropython ver '+version+' by theCodeman')
    print('https://github.com/TheCodeman/myos')
    print('MicroPython Version : {} Platform : {}'.format(sys.version, sys.platform))

    timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=intCallback)

    while True:
        str = input(uos.getcwd() + '>')
        cmd = str.split()
#        print(cmd)
        if len(str)!=0:
            if cmd[0] == 'cd':
                try:
                    uos.chdir(cmd[1])
                except:
                    print('bad dir')
                
            elif cmd[0] == 'ls':
                print('Current Directory ', uos.getcwd())
                total =0
                      #F       1366    lora.py
                print('Type    Size    Filename')
                print('----------------------------------')
                if len(cmd) == 2:
                    path=cmd[1]
                else:
                    path=uos.getcwd()
                try:
                    for l in uos.ilistdir(path):
                        if l[1] & 0x4000:
                            print('D{0:>31}'.format(l[0]))
                        else:
                            # F       3360    myos.py
                            total += int(uos.stat(l[0])[6])
                            print('F       {0:<8}{1:>16}'.format(uos.stat(l[0])[6], l[0]))
                    print('----------------------------------')
                    print('File Size Total: {0}'.format(total))
                except Exception as e:
                    print(e)

            elif cmd[0] == 'cp':
                if len(cmd) == 3:
                    try:
                        with open(cmd[1] , 'rb') as source:
                            print('Source {0}'.format(cmd[1]))
                            data=source.read()
                            source.close()
                    except Exception as e:
                        print(e)
                    try:
                        with open(cmd[2], 'wb') as dest:
                            print('Dest {0}'.format(cmd[2]))
                            dest.write(data)
                            dest.close()
                    except Exception as e:
                        print(e)
                else:
                    print('cp requires source filename and destination filename ')

            elif cmd[0] == 'run':
                if len(cmd)==2:
                   __import__(cmd[1])
                   del sys.modules[cmd[1]]
                else:
                    print('Need File Name')
                
            elif cmd[0] == 'lr':
                if networkUp:
                    if len(cmd) == 1:
                        res=ssh.list(settings.remoteIP+settings.remotePath, settings.uname, settings.upass)
                    else:
                        res=ssh.list(settings.remoteIP+settings.remotePath+cmd[1], settings.uname, settings.upass)
                    print(res[0])
                    if res[0]==0:
                        print(res[1])
                        print(res[2])
                else:
                    print('No Network Connection')            
            elif cmd[0] == 'put':
                if networkUp:
                    res=ssh.put(settings.remoteIP+settings.remotePath+cmd[1], settings.uname, settings.upass, file=cmd[1])
                    if res[0]==0:
                        print('File %s copied to %s' % ( cmd[1], settings.remotePath))
                else:
                    print('No Network Connection')            
            elif cmd[0] == 'get':
                if networkUp:
                    res=ssh.get(settings.remoteIP+settings.remotePath+cmd[1], settings.uname, settings.upass, file='$$$.tmp')
                    if res[0]==0:
                        try:
                            uos.remove(cmd[1])
                        except:
                            pass
                        uos.rename('$$$.tmp', cmd[1])
                        print('File %s copied from %s' % (  cmd[1], settings.remotePath))
                    else:
                        uos.remove('$$$.tmp')
                        print('File Not Found')
                else:
                    print('No Network Connection')            
            elif cmd[0] == 'edit':
                pye(cmd[1])
                
            elif cmd[0] == 'rm':
                try:
                    uos.remove(cmd[1])
                except:
                    print('no file')
                
            elif cmd[0] == 'md':
                try:
                    uos.mkdir(cmd[1])
                except:
                    print("Need Directory Name")
                
            elif cmd[0] == 'rmdir':
                try:
                    uos.rmdir(cmd[1])
                except:
                    print("Need Directory Name")
                
            elif cmd[0] == 'reset':
                machine.reset()
                
            elif cmd[0] == 'cat':
                line=0
                try:
                    f=open(cmd[1], 'r')
                    while True:
                        str=f.readline()
                        if str == "":
                            break
                        print(str, end="")
                        line+=1
                        if line > 25:
                            print('----- press space to continue or q to quit -----',end="")
                            ret=getch()
                            print('\r                                                \r', end="")
                            if ret=='q':
                                break
                            else:
                                line=0;
                    f.close()
                except:
                    print('no file')
                
            elif cmd[0] == 'time':
                print('Time set to: {}'.format(utime.strftime('%c', utime.localtime())))
                
            elif cmd[0] == 'df':
                if len(cmd)  == 1:
                    fs_stat = uos.statvfs(uos.getcwd())
                else:
                    fs_stat = uos.statvfs(cmd[1])
                fs_size = fs_stat[0] * fs_stat[2]
                fs_free = fs_stat[0] * fs_stat[3]
                print('File System Size {:,} - Free Space {:,}'.format(fs_size, fs_free))
                
            elif cmd[0] == 'wget':
                if networkUp:
                    try:
                        response = urequests.get(cmd[1])

                        if response.status_code == 200:
                            print(type(response))
                            print(response.text)
                            print(type(response.text))
                            fileName = cmd[1].split('/')
                            print(fileName)
                            print(fileName[-1])
                            f=open(fileName[-1], 'w')
                            f.write(response.text)
                            f.close()
                        else:
                           print('Error: {0} {1}'.format(response.status_code, response.reason.decode('utf-8')))
                    except Exception as e:
                        print(e)
                else:
                    print('No Network Connection')            
            elif cmd[0] == 'wifi':
                try:
                    if cmd[1] == 'active':
                        nic.active(True)
                    if cmd[1] == 'deactive':
                        nic.active(False)
                    if cmd[1] == 'config':
                        status = nic.ifconfig()
                        print('IP: {0}\n\rSubnet: {1}\r\nGateway: {2}\r\nDNS: {3}'.format(status[0], status[1], status[2], status[3]))
                    if cmd[1] == 'isconnected':
                        print(nic.isconnected())
                    if cmd[1] == 'connect':
                        try:
                            nic.connect(cmd[2], cmd[3])
                        except Exception as e:
                            print(e)
                    if cmd[1] == 'scan':
                        stations = nic.scan()
                        for s in stations:
                            if s[4] == 0:
                                authmode='Open'
                            if s[4] == 1:
                                authmode='Wep'
                            if s[4] == 2:
                                authmode='WPA-PSK'
                            if s[4] == 3:
                                authmode='WPA2-PSK'
                            if s[4] == 4:
                                authmode='WPA/WPA2-PSK'
                            print('SSID: {0:<32} Channel: {1} RSSSI: {2} Auth Type: {3}'.format(s[0].decode('utf-8'), s[2], s[3], authmode))
                except Exception as e:
                    print(e)
                    print(' no action')
                
            elif cmd[0]=='umountsd':
                try:
                    uos.umountsd()
                except Exception as e:
                    print(e)
                
            elif cmd[0]=='mountsd':
                try:
                    uos.mountsd()
                except Exception as e:
                    print(e)
                
            elif cmd[0] == 'help':
                print('Command List')
                print('----------------------------------')
                print('ls      - list files current directory')
                print('lr      - list files on remote server optional directory')
                print('cat     - display file')
                print('rm      - remove file')
                print('df      - display drive space')
                print('time    - display time and date')
                print('get     - scp from server')
                print('put     - scp to server')
                print('md      - make directory')
                print('rmdir   - remove directory')
                print('run     - run python script')
                print('edit    - edit file using pye')
                print('modules - list installed modules')
                print('reset   - reset board')
                print('wget    - get file over http and save to file')
                print('----------------------------------')
                
            elif cmd[0] == 'exit':
                timer.deinit()
                return 1
                
            elif cmd[0] == 'update':
                if networkUp:
                    res=ssh.get(settings.remoteIP+settings.remotePath+'micropyos.py', settings.uname, settings.upass, file='$$$.tmp')
                    if res[0]==0:
                        try:
                            uos.remove('micropyos.py')
                        except:
                            pass
                        uos.rename('$$$.tmp', 'micropyos.py')
                        print('File %s copied from %s' % (  'micropyos.py', settings.remotePath))
                    else:
                        uos.remove('$$$.tmp')
                        print('File Not Found')
                    timer.deinit()
                    return 2
                else:
                    print('No Network Connection')            

            elif cmd[0] == 'modules':
                for m in sys.modules:
                    print(m)
                
            elif cmd[0]=='settings':
                pye('settings.py')
                
            else:
                print('unknown command');

main()


