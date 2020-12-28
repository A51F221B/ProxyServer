# HTTP-Proxy-Server
![proxy.png](https://github.com/A51F221B/ProxyServer/blob/main/proxy.png)
#### - LIBRARIES USED IN THE PROJECT

![imports.png](https://github.com/A51F221B/ProxyServer/blob/main/imports.png)

#### - CODE DESCRIPTION
The proxy acts as the man-in-middle between client which is our browser and the web server to which the request **(HTTP or HTTPS)** is sent. To use the proxy, we will have to set it in the browser proxy setting with **IP 127.0.1.1** at port 8080.
![ss.png](https://github.com/A51F221B/ProxyServer/blob/main/ss.png)
Before running the proxy, we have to make sure that no other process is running on port **8080.** To do that, open terminal (linux) and type:

   #### **sudo lsof -t -i tcp:8080 | xargs kill -9**

Initially, the object of the class server is created by which we are able to access the methods of the class. The function server( ) triggers the proxy server. Now, the proxy checks if the requested website is blocked or not. For port 80 it will call HTTP() function and for port 443 it will call HTTPS() function. If the website is requested more than once, the proxy will automatically cache it. This whole process is displayed on terminal with current date and time.

.
