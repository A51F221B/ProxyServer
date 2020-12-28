import socket #main socket programming module
import sys    # for file reading and other functions 
import datetime # for writing logs with date and time
import time    # for the time stamp in logs.txt
import argparse #for parsing arguments 
import threading #for concurrency and parrallelism i.e running code in parallel
from _thread import start_new_thread
import subprocess
#sudo lsof -t -i tcp:8080 | xargs kill -9       to free the port for testing
        
            
class Server:
    def __init__(self,blockedIP="",blockedWebsite=""):
        self.max_conn=0
        self.buffer=0
        self.socket=0
        self.port=0
        self.blacklistIP=blockedIP
        self.blacklistWebsite=blockedWebsite
        
    def logs(self,log):
        with open("logs.txt","w+") as f:
            f.write(log)   #open a file and write logs
            f.write("\n")
    
    def GETtime(self):
         return "[" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "]"
     
    def StatusCode(self,code,length):
        h = ''
        if code == 200:
            # Status code
            h = 'HTTP/1.1 200 OK\n'
            h += 'Server: Proxy\n'

        elif code == 404:
            # Status code
            h = 'HTTP/1.1 404 Not Found\n'
            h += 'Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + '\n'
            h += 'Server: Proxy\n'

        h += 'Content-Length: ' + str(length) + '\n'
        h += 'Connection: close\n\n'

        return h
    
    def HTTP(self,webserver, port, conn, request, addr, buffer, requested_file):
        # Stripping file name
        requested_file = requested_file.replace(b".", b"_").replace(b"http://", b"_").replace(b"/", b"")

        # Trying to find in cache
        try:
            print(self.GETtime() + "  Searching for: ", requested_file)
            print(self.GETtime() + "  Cache Hit")
            file_handler = open(b"cache/" + requested_file, 'rb')
            self.logs(self.GETtime() + "  Cache Hit")
            response_content = file_handler.read()
            file_handler.close()
            response_headers = self.StatusCode(200, len(response_content))
            conn.send(response_headers.encode("utf-8"))
            time.sleep(1)
            conn.send(response_content)
            conn.close()

        # request from web if not in cache
    
        except Exception as e:
            print(e)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((webserver, port))
                s.send(request)

                print(self.GETtime() + " [+] Sending GET request from ", addr, " to ", webserver)
                self.logs( self.GETtime() + " [+] Sending GET request from  " + addr[0] + " to host " + str(webserver))
                # Makefile for socket
                file_object = s.makefile('wb', 0)
                file_object.write(b"GET " + b"http://" + requested_file + b" HTTP/1.0\n\n")
                # Read the response into buffer
                file_object = s.makefile('rb', 0)
                buff = file_object.readlines()
                temp_file = open(b"cache/" + requested_file, "wb+")
                for i in range(0, len(buff)):
                    temp_file.write(buff[i])
                    conn.send(buff[i])

                print(self.GETtime() + " [+] Client Request " + str(addr) + " completed")
                self.logs(self.GETtime() + "[+] Client Request " + str(addr[0]) + " completed")
                s.close()
                conn.close()

            except Exception as e:
                print(self.GETtime() + "  [!] Error while forwarding the request " + str(e))
                self.logs(self.GETtime() + " [!] Error while forwarding the request " + str(e))
                return
    
    def HTTPS(self,webserver, port, conn, request, addr, buffer, requested_file):
        # Stripping for filename
        requested_file = requested_file.replace(b".", b"_").replace(b"http://", b"_").replace(b"/", b"")

        # Trying to find in cache
        try:
            print(self.GETtime() + " [+] Finding : ", requested_file)
            file_handler = open(b"cache/" + requested_file, 'rb')
            print("\n")
            print(self.GETtime() + " [+] Found in Cache\n")
            self.logs(self.GETtime() + " [+] Found in Cache\n")
            response_content = file_handler.read()
            file_handler.close()
            response_headers = self.StatusCode(200, len(response_content))
            conn.send(response_headers.encode("utf-8"))
            time.sleep(1)
            conn.send(response_content)
            conn.close()

        # Trying to find in cache
        except:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # Send 200 in response if successful
                s.connect((webserver, port))
                reply = "HTTP/1.0 200 Connection established\r\n"
                reply += "Proxy-agent: Proxy\r\n"
                reply += "\r\n"
                conn.sendall(reply.encode())
            except socket.error :
                pass
                # print(self.GETtime() + "  Error: No Cache Hit in HTTPS because " + str(err))
                # self.logs(self.GETtime() + "  Error: No Cache Hit in HTTPS beacuse" + str(err))

            conn.setblocking(0)
            s.setblocking(False)
            print(self.GETtime() + " [+] HTTPS Connection Established")
            self.logs(self.GETtime() + " [+] HTTPS Connection Established")
            while True:
                try:
                    request = conn.recv(buffer)
                    s.sendall(request)
                except socket.error :
                    pass

                try:
                    reply = s.recv(buffer)
                    conn.sendall(reply)
                except socket.error :
                    pass

    
    def handlingClient(self,conn,addr,buffer):
        # Try to split necessary info from the header
        try:
            request = conn.recv(buffer)
            header = request.split(b'\n')[0]
            requested_file = request
            requested_file = requested_file.split(b' ')
            url = header.split(b' ')[1]

            # Stripping Port and Domain
            hostIndex = url.find(b"://")
            if hostIndex == -1:
                temp = url
            else:
                temp = url[(hostIndex + 3):]

            portIndex = temp.find(b":")

            serverIndex = temp.find(b"/")
            if serverIndex == -1:
                serverIndex = len(temp)

            # If port 80 use http else use https
            webserver = ""
            port = -1
            if (portIndex == -1 or serverIndex < portIndex):
                port = 80
                webserver = temp[:serverIndex]
            else:
                port = int((temp[portIndex + 1:])[:serverIndex - portIndex - 1])
                webserver = temp[:portIndex]

            # Stripping requested file to see if it exists in cache
            requested_file = requested_file[1]
            print("Requested File ", requested_file)

            # Stripping method to find if HTTPS (CONNECT) or HTTP (GET)
            method = request.split(b" ")[0]

            # blocked IP
            if addr[0] in self.blacklistIP:
                print(self.GETtime() + " [!] IP is Blacklisted")
                self.logs(self.GETtime() + "  [!] IP Blacklisted")
                conn.close()

            # Checking for blacklisted IPs and Websites
            target = webserver
            target = target.replace(b"http://", b"").split(b".")[1].decode("utf-8")
            try:
                if target in self.blacklistWebsite:
                    print(self.GETtime() + "  [!] Website Blacklisted")
                    self.logs(self.GETtime() + " [!] Website Blacklisted")
                    conn.close()
            except:
                pass

            # for HTTPS
            if method == b"CONNECT":
                print(self.GETtime() + "  [+] Connect HTTPS request")
                self.logs(self.GETtime() + " [+] Connect HTTPS request")
                self.HTTPS(webserver, port, conn, request, addr, buffer, requested_file)

            #For HTTP
            else:
                print(self.GETtime() + " [+]  Connect HTTP request")
                self.logs(self.GETtime() + " [+]   Connect HTTP request")
                self.HTTP(webserver, port, conn, request, addr, buffer, requested_file)

        except Exception as e:
             print(self.GETtime() + "  [!] Error: Cannot read connection request..." + str(e))
             self.logs(self.GETtime() + " [!] Error: Cannot read connection request..." + str(e))
            #return
    
    def start(self,conn=5,buffer=4096,port=8080):
        #try:
            self.logs(self.GETtime()+" \n[+] Starting the Server\n")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       #     SERVER = socket.gethostbyname(socket.gethostname())
            ADDR = ('127.0.1.1', port)
            s.bind(ADDR)
            s.listen(conn)
            print(self.GETtime()+" [+] Listening " )
            self.logs(self.GETtime()+" [+] Trying to Initialize a socket")
        
        #except:
         #   print(self.GETtime()+" [!] Error , Cannot start listening")
          #  exit(1)
            while True:
                try:
                    conn,addr=s.accept() #start accepting connections
                    print(self.GETtime()+" [+] Started accepting connections ")
                    self.logs(self.GETtime()+" [+] Connected to "+addr[0]+" on port "+str(addr[1]))
                    start_new_thread(self.handlingClient, (conn, ADDR, buffer))
                   # threading.Thread(target=self.handlingClient, args=(conn, ADDR,buffer)).start()
                   # self.handlingClient(conn,ADDR,buffer)
                except Exception as e:
                    print(self.GETtime()+" [!] Error : Cannot connect"+ str(e))
                    self.logs(self.GETtime()+" [!] Error : Cannot establish connection "+str(e))
                    sys.exit(1)
            s.close()
        

if __name__=='__main__':
    subprocess.call('clear',shell=True)
    print("..............")
    print("Loading:")

#animation = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
    animation = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■] "]

    for i in range(len(animation)):
        time.sleep(0.2)
        sys.stdout.write("\r" + animation[i % len(animation)])
        sys.stdout.flush()
    print("  ")
    print("  ")
    server=Server(blockedIP="",blockedWebsite="facebook")
    server.start()