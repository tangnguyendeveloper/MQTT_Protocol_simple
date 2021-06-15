from kivy.app import App
from kivy.uix.widget import Widget
from MQTTClient import *
from random import randint
import threading
import time


def RandomName():
    value = "client"
    for i in range(0, 10):
        value += str(randint(1, 255))
    return value


class MyClient(MQTTClient):
    def __init__(self, client_name):
        super().__init__(client_name)
        self.data_from_recv = ""
        self.subscribe = ""

    def SetTopicSubscribe(self):
        self._list_topic = self.subscribe.split("\n")

    def OnMessage(self, topic, data):
        self.data_from_recv = f"{topic}: {data}"

    async def OnConnect(self):
        await asyncio.sleep(900)
        try:
            self.Publish("1", "1")
        except:
            self.Reconnect()


class RootWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.client = MyClient(RandomName())
        self.publisher = MQTTClient(RandomName())
        self.publisher._encrypt_decrypt.GenerateKey()

    async def UpdateRecv(self):
        while True:
            if self.client.data_from_recv != "":
                self.ids.output.text += (self.client.data_from_recv+"\n")
                self.client.data_from_recv = ""
                await asyncio.sleep(1)

    def UpdateRecvCall(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.UpdateRecv())

    def Connect_click(self):
        try:
            self.ids.connect_button.text = "Connecting"
            t = threading.Thread(target=self.client.Start, args=(
                self.ids.sever.text,
                int(self.ids.port.text)
            ))
            t1 = threading.Thread(target=self.UpdateRecvCall)
            t1.daemon = True
            t.daemon = True
            t.start()
            t1.start()
            self.ids.connect_button.text = "Connected"
        except:
            print("Input error!")

    def RunPublish(self, topic, data, public):
        if public == False:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.publisher.PublishSecurity(topic, data))
            return

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.publisher.Publish(topic, data))

    def Publish_click(self):
        self.publisher._server_publickey = self.client._server_publickey
        self.publisher._server = self.client._server
        self.publisher._port = self.client._port
        
        if self.ids.security_publish.active:
            t = threading.Thread(target=self.RunPublish, args=(self.ids.publish.text, self.ids.data.text, False))
            t.daemon = True
            t.start()
        else:
            t = threading.Thread(target=self.RunPublish, args=(self.ids.publish.text, self.ids.data.text, True))
            t.daemon = True
            t.start()


class ClientApp(App):

    def build(self):
        self.title = 'MQTT Client'
        return RootWidget()


if __name__ == "__main__":
    ClientApp().run()