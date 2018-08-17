#!/usr/bin/env python
import os,sys,time,threading

sys.path.append('..')
from common import logviewer, tcpserver
from common.settings import Settings, SSLSettings
SETTINGS = Settings('settings.py')
SSLSETTINGS = SSLSettings(SETTINGS.CERTFILE, SETTINGS.KEYFILE)

class HttpHandler(tcpserver.ConnectionHandler):
    def handle(self):
        request = self.sock.read()
        while request:
            print(request)
            self.f.write(request)
            self.f.flush()
            request = self.sock.read()
        self.sock.write("HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n")

def main():
    if not os.path.exists(SETTINGS.LOG_DIR):
        os.makedirs(SETTINGS.LOG_DIR)
    if SETTINGS.MOTD_FILE and os.path.isfile(SETTINGS.MOTD_FILE): # motd
        import shutil
        shutil.copyfile(SETTINGS.MOTD_FILE, os.path.join(SETTINGS.LOG_DIR, SETTINGS.MOTD_FILE))

    logviewer.ViewerServer(('', SETTINGS.LOG_VIEWER_PORT), SETTINGS.AUTHKEY, SETTINGS.LOG_DIR, SSLSETTINGS if SETTINGS.LOG_VIEWER_HTTPS else None).start()
    tcpserver.DumpingServer(80, False, HttpHandler, SETTINGS.LOG_DIR, None, SETTINGS.ANON).start()
    tcpserver.DumpingServer(443, True, HttpHandler, SETTINGS.LOG_DIR, SSLSETTINGS, SETTINGS.ANON).start()
    tcpserver.DumpingServer(6969, False, HttpHandler, SETTINGS.LOG_DIR, None, True).start()
    tcpserver.DumpingServer(6970, True, HttpHandler, SETTINGS.LOG_DIR, SSLSETTINGS, True).start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()
