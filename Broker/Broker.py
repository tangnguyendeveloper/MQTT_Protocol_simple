# -*- coding: utf-8 -*-
import socket
import asyncio
import time
import pickle
from Database import Database
from EncryptDecrypt import EncryptDecrypt


SEND_KEY = bytes(f"{chr(1)}", "utf-8")
CONNECT = bytes(f"{chr(2)}", "utf-8")
RECONNECT = bytes(f"{chr(3)}", "utf-8")
PUBLISH = bytes(f"{chr(4)}", "utf-8")
SECURITY_PUBLISH = bytes(f"{chr(5)}", "utf-8")
SUBSCRIBE = bytes(f"{chr(6)}", "utf-8")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection = {}
fist_time = time.time()
database = Database("Broker.db")
encrypt_decrypt = EncryptDecrypt()


def Binding():
    global sock
    try:
        sock.bind(("0.0.0.0", 5883))
        print("listen: ", ("0.0.0.0", 5883))
    except:
        print("Can not binding port 5883")
        while True:
            try:
                port = int(input("New port: "))
                sock.bind(("0.0.0.0", port))
                print("listen: ", ("0.0.0.0", port))
                break
            except:
                print("Can not binding")


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


def CheckConnectionExist(name):
    global connection
    for i in connection:
        if i == name:
            return True
    return False


async def ForwardPackage(list_client, topic, data, security=False):
    global connection, encrypt_decrypt
    loop = asyncio.get_event_loop()

    if security:
        for client in list_client:
            try:
                topic = encrypt_decrypt.Encrypt(client[1], topic)
                data = encrypt_decrypt.Encrypt(client[1], data)
                
                package = SECURITY_PUBLISH+GetBytesFromInt(len(topic), len(data))+topic+data
                await loop.sock_sendall(connection[client[0]][0], package)
            except:
                print("Error forward package  ")

        return

    topic = bytes(topic, "unicode_escape")

    for client in list_client:
        try:
            package = PUBLISH+GetBytesFromInt(len(topic), len(data))+topic+data
            await loop.sock_sendall(connection[client][0], package)
        except:
            print("Error forward package to ", client)


async def ClientConnect(client, reconnect=False):
    global database, encrypt_decrypt, connection

    loop = asyncio.get_event_loop()
    
    if reconnect:
        try:
            package_length = (await loop.sock_recv(client, 4))
            name_length, _ = GetIntFromBytes(package_length)
            name = (await loop.sock_recv(client, name_length))
            name = name.decode("unicode_escape")
            if CheckConnectionExist(name):
                connection[name] = (client, time.time())
                await loop.sock_sendall(client, b'1')
            else:
                await loop.sock_sendall(client, b'0')
        except:
            print("A reconnection error.")
            client.close()
        finally:
            return

    try:
        package_length = (await loop.sock_recv(client, 4))
        name_length, public_key_length = GetIntFromBytes(package_length)
        name = (await loop.sock_recv(client, name_length))
        public_key = (await loop.sock_recv(client, public_key_length))
        name = name.decode("unicode_escape")

        if not database.ClientExist(name):
            database.AddClient(name, public_key)
            data = SEND_KEY+encrypt_decrypt.PublicKey
            await loop.sock_sendall(client, data)
            connection[name] = (client, time.time())
        else:
            await loop.sock_sendall(client, b'0')
    except:
        print("A connection error.")
        client.close()


async def ClentPublish(client, security=False):
    global database, encrypt_decrypt
    loop = asyncio.get_event_loop()

    if security:
        try:
            package_length = (await loop.sock_recv(client, 4))
            topic_length, data_length = GetIntFromBytes(package_length)
            topic = (await loop.sock_recv(client, topic_length))
            data = (await loop.sock_recv(client, data_length))
            topic = encrypt_decrypt.Decrypt(topic)
            data = encrypt_decrypt.Decrypt(data)

            client_subcribe_and_key = database.GetListClientAndKeySubscribeTopic(topic)
            await ForwardPackage(client_subcribe_and_key, topic, data, True)

        except:
            print("Publish package error.")
        finally:
            return

    try:
        package_length = (await loop.sock_recv(client, 4))
        topic_length, data_length = GetIntFromBytes(package_length)
        topic = (await loop.sock_recv(client, topic_length))
        data = (await loop.sock_recv(client, data_length))
        topic = topic.decode("unicode_escape")

        client_subcribe = database.GetListClientSubscribeTopic(topic)
        await ForwardPackage(client_subcribe, topic, data)

    except:
        print("Publish package error.")


async def ClentSubcribe(client):
    global database
    loop = asyncio.get_event_loop()

    try:
        package_length = (await loop.sock_recv(client, 4))
        name_length, list_topic_length = GetIntFromBytes(package_length)
        name = (await loop.sock_recv(client, name_length))
        list_topic = (await loop.sock_recv(client, list_topic_length))
        name = name.decode("unicode_escape")
        list_topic = pickle.loads(list_topic)
        
        error = database.UpdateSubscribeInformation(name, list_topic)
        if error != 0:
            await loop.sock_sendall(client, b'0')
        else:
            await loop.sock_sendall(client, b'1')

    except:
        print("A Clent subcribe error.")


async def ReceiveFromClient(client, address):
    loop = asyncio.get_event_loop()

    package_type = (await loop.sock_recv(client, 1))
    
    if package_type == CONNECT:
        await loop.create_task(ClientConnect(client))
        print(f"Client {address}  CONNECT.\n")

    elif package_type == RECONNECT:
        await loop.create_task(ClientConnect(client, True))
        print(f"Client {address}  RECONNECT.\n")

    elif package_type == SUBSCRIBE:
        await loop.create_task(ClentSubcribe(client))
        print(f"Client {address}  SUBSCRIBE.\n")
        client.close()

    elif package_type == PUBLISH:
        print(f"\nClient {address[0]}  PUBLISH.")
        await loop.create_task(ClentPublish(client))
        client.close()

    elif package_type == SECURITY_PUBLISH:
        print(f"\nClient {address[0]}  SECURITY_PUBLISH.")
        await loop.create_task(ClentPublish(client, True))
        client.close()
    
    else:
        client.close()


async def AcceptClient():
    global sock

    loop = asyncio.get_event_loop()

    while True:
        client, address = await loop.sock_accept(sock)
        loop.create_task(ReceiveFromClient(client, address))


async def UpdateConnection():
    global connection, fist_time, database
    
    current_time = time.time()
    
    while True:
        if current_time-fist_time > 3600:
            print("UpdateConnection()")

            for i in connection:
                if connection[i][1] - current_time > 1800:
                    connection[i][0].close()
                    del connection[i]
                    database.DeleteSubscribe(i)
                    database.DeleteClient(i)
        
        fist_time = time.time()
        await asyncio.sleep(60)


async def main():
    global sock, database, encrypt_decrypt
    
    Binding()
    sock.listen()
    database.CreateNewORTryConnect()
    encrypt_decrypt.GenerateKey()

    accept_client_task = asyncio.create_task(AcceptClient())
    update_connection_task = asyncio.create_task(UpdateConnection())

    await accept_client_task
    await update_connection_task


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())