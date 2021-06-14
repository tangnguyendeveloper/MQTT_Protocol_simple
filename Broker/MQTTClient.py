from os import error
import socket
import asyncio
import pickle
from sqlite3.dbapi2 import connect
from EncryptDecrypt import EncryptDecrypt


SEND_KEY = bytes(f"{chr(1)}", "utf-8")
CONNECT = bytes(f"{chr(2)}", "utf-8")
RECONNECT = bytes(f"{chr(3)}", "utf-8")
PUBLISH = bytes(f"{chr(4)}", "utf-8")
SECURITY_PUBLISH = bytes(f"{chr(5)}", "utf-8")
SUBSCRIBE = bytes(f"{chr(6)}", "utf-8")


def GetIntFromBytes(value):
    fist_length = value[0]*100+value[1]
    second_length = value[2]*100+value[3]
    return fist_length, second_length


def GetBytesFromInt(value1, value2):
    b1 = value1//100
    b2 = value1%100
    b3 = value2//100
    b4 = value2%100
    return bytes(f"{chr(b1)}", "utf-8")+bytes(f"{chr(b2)}", "utf-8")+bytes(f"{chr(b3)}", "utf-8")+bytes(f"{chr(b4)}", "utf-8")


class MQTTClient:
    # Client_name is ASCII string
    def __init__(self, client_name):
        
        self._sock_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._encrypt_decrypt = EncryptDecrypt()
        self._client_name = bytes(client_name, "unicode_escape")
        self._server = None
        self._port = None
        self._server_publickey = None
        self._list_topic = []
        self._is_connect = False
        

    async def Connect(self):
        loop = asyncio.get_event_loop()
        self._encrypt_decrypt.GenerateKey()

        message_connect = CONNECT+GetBytesFromInt(len(self._client_name), len(self._encrypt_decrypt.PublicKey))
        message_connect += (self._client_name+self._encrypt_decrypt.PublicKey)

        await loop.sock_connect(self._sock_receive, (self._server, self._port))
        await loop.sock_sendall(self._sock_receive, message_connect)
        reponse = (await loop.sock_recv(self._sock_receive, 1))
        
        if (reponse == SEND_KEY):
            self._server_publickey = (await loop.sock_recv(self._sock_receive, len(self._encrypt_decrypt.PublicKey)))
            return False
        else:
            return True
        

    async def Reconnect(self):
        loop = asyncio.get_event_loop()
        self._sock_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        message_connect = RECONNECT+GetBytesFromInt(len(self._client_name), 0)
        message_connect += self._client_name

        await loop.sock_connect(self._sock_receive, (self._server, self._port))
        await loop.sock_sendall(self._sock_receive, message_connect)
        reponse = (await loop.sock_recv(self._sock_receive, 1))
        
        if (reponse == b'1'):
            return False
        else:
            return True

    
    # topic_name is ASCII string
    # data is string
    async def Publish(self, topic_name, data):
        loop = asyncio.get_event_loop()
        topic_name = bytes(topic_name, "unicode_escape")
        data = bytes(data, "utf-8")
        message_publish = PUBLISH+GetBytesFromInt(len(topic_name), len(data))
        message_publish += (topic_name+data)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await loop.sock_connect(sock, (self._server, self._port))
        await loop.sock_sendall(sock, message_publish)


    # topic_name is ASCII string
    # data is string
    async def PublishSecurity(self, topic_name, data):
        loop = asyncio.get_event_loop()
        topic_name = self._encrypt_decrypt.Encrypt(self._server_publickey, topic_name)
        data = self._encrypt_decrypt.Encrypt(self._server_publickey, data)
        message_publish = SECURITY_PUBLISH+GetBytesFromInt(len(topic_name), len(data))
        message_publish += (topic_name+data)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await loop.sock_connect(sock, (self._server, self._port))
        await loop.sock_sendall(sock, message_publish)


    # list_topic is list of ASCII string
    async def Subscribe(self):
        loop = asyncio.get_event_loop()
        list_topic = pickle.dumps(self._list_topic, pickle.HIGHEST_PROTOCOL)
        message_subscribe = SUBSCRIBE+GetBytesFromInt(len(self._client_name), len(list_topic))
        message_subscribe += (self._client_name+list_topic)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await loop.sock_connect(sock, (self._server, self._port))
        await loop.sock_sendall(sock, message_subscribe)

        reponse = (await loop.sock_recv(sock, 1))
        if reponse == b'1':
            return False
        else:
            return True


    def SetTopicSubscribe(self):
        return


    async def OnConnect(self):
        return 


    def OnMessage(self, topic, data):
        return


    async def ReceiveForever(self):
        loop = asyncio.get_event_loop()
        while self._is_connect:
            try:
                package_type = (await loop.sock_recv(self._sock_receive, 1))
                package_length = (await loop.sock_recv(self._sock_receive, 4))
                topic_length , data_length = GetIntFromBytes(package_length)
                
                if package_type == PUBLISH:
                    topc = (await loop.sock_recv(self._sock_receive, topic_length))
                    topc = topc.decode('unicode_escape')
                    data = (await loop.sock_recv(self._sock_receive, data_length))
                    data = data.decode("utf-8")
                    self.OnMessage(topc, data)
                elif package_type == SECURITY_PUBLISH:
                    topic = (await loop.sock_recv(self._sock_receive, topic_length))
                    topic = self._encrypt_decrypt.Decrypt(topic)
                    data = (await loop.sock_recv(self._sock_receive, data_length))
                    data = self._encrypt_decrypt.Decrypt(data)
                    self.OnMessage(topic, data)

            except:
                print("Check server and port.")
                return


    async def ConnectForever(self):
        try:
            self.SetTopicSubscribe()
            error = (await self.Connect())
            if error:
                print("Can not connect to Broker.")
                return
            error = (await self.Subscribe())
            if error:
                print("Can not subscribe with Broker.")
                return

            self._is_connect = True

            while True:
                await self.OnConnect()
                await asyncio.sleep(1)
                
        except:
            print("Check server and port.")
            self._is_connect = False
            self._sock_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        

    async def Run(self):
        loop = asyncio.get_event_loop()

        connect_task = loop.create_task(self.ConnectForever())
        while not self._is_connect:
            await asyncio.sleep(1)
        receive_task = loop.create_task(self.ReceiveForever())

        await receive_task
        await connect_task
    

    # server is IP address or domain name
    # port is a unsigned integer number
    def Start(self, server, port):
        self._server = server
        self._port = port
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.Run())