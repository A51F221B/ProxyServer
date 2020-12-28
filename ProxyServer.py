import socket #main socket programming module
import sys    # for file reading and other functions 
import datetime # for writing logs with date and time
import time    # for the time stamp in logs.txt
import argparse #for parsing arguments 
import threading #for concurrency and parrallelism i.e running code in parallel

#sudo lsof -t -i tcp:8080 | xargs kill -9 to free the port for testing

class Server:
    def __init__(self,blockedIP=False,blockedWebsite=False):
        self.maximum_connections=0
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
    
    def HTTP(self,webserver, port, conn, request, addr, buffer, requested_file):
        pass
    
    def HTTPS(self,webserver, port, conn, request, addr, buffer, requested_file):
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

            # If no port in header i.e, if http connection then use port 80 else the port in header
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
                print(self.GETtime + " [!] IP is Blacklisted")
                self.logs(self.GETtime + "  [!] IP Blacklisted")
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
                print(self.GETtime() + "  Connect HTTP request")
                self.logs(self.GETtime() + "   Connect HTTPS request")
                self.HTTP(webserver, port, conn, request, addr, buffer, requested_file)

        except Exception as e:
            # print(self.GETtime() + "  Error: Cannot read connection request..." + str(e))
            # self.logs(self.GETtime() + "  Error: Cannot read connection request..." + str(e))
            return
    
    def start(self,conn=5,buffer=5,port=8080):
        try:
            self.logs(self.GETtime()+" \n[+] Starting the Server\n")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind("",port)
            s.listen(conn)
            print(self.GETtime()+" [+] Listening " )
            self.logs(self.GETtime()+" [+] Trying to Initialize a socket")
        
        except:
            print(self.GETtime()+"[!] Error , Connot start listening")
            exit(1)
        while True:
            try:
                conn,addr=s.accept() #start accepting connections
                print(self.GETtime()+" [+] Started accepting connections ")
                self.logs(self.GETtime()+" [+] Connected to "+addr[0]+" on port "+str(addr[1]))
                threading.Thread(target=self.handlingClient, args=(conn, addr,buffer)).start()
            except Exception as e:
                print(self.GETtime()+" [!] Error : Cannot connect"+ str(e))
                self.logs(self.GETtime()+" [!] Error : Connot established connection "+str(e))
                sys.exit(1)
        s.close()
    
class Arguments:
    pass