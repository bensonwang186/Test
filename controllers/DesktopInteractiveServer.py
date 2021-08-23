import socket
import threading

SERVICE_PORT = 53567
SERVICE_IP = "127.0.0.1"
CLIENT_READY_TIME = 3 * 1000
LOGOUT_RESPONSE_TIME = 3 * 1000
LOGOUT_PROLONG_TIME = 30 * 1000
class DesktopInteractiveServer(threading.Thread):
    pass


    def __init__(self):
        super(DesktopInteractiveServer, self).__init__()
        self.start()
        self.clients = []

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVICE_IP, SERVICE_PORT))
        self.socket.listen(5)
        while True:
            connection, address = self.socket.accept()
            self.clients.append(connection)
        print("hello")

    def terminate(self):
        if self.clients is not None and len(self.clients) > 0:
            for client in self.clients:
                s = b"terminate"
                client.send(s)

    def logout(self):
        if self.clients is not None and len(self.clients) > 0:
            for client in self.clients:
                s = b"logout"
                try:
                    client.send(s)
                except:
                    return False
        return True

if __name__ == "__main__":
    # import socket
    #
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.bind(('127.0.0.1', 53567))
    # sock.listen(5)
    # while True:
    #     connection, address = sock.accept()
    #     try:
    #         connection.settimeout(5)
    #         # buf = connection.recv(1024)
    #         # print(buf.decode("utf-8"))
    #         s = b"logout"
    #         connection.send(s)
    #     except socket.timeout:
    #         print('time out')
    #     connection.close()

    dis = DesktopInteractiveServer()
    import time
    print("something")
    dis.terminate()
    time.sleep(5.5)    # pause 5.5 seconds
    print("something")
