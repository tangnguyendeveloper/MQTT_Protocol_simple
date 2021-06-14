import sqlite3

class Database:
    def __init__(self, database_part):
        self.__database_part = database_part


    def CreateNewORTryConnect(self):
        conn = sqlite3.connect(self.__database_part)
        try:
            cr = conn.cursor()
            cr.execute(
                """
                CREATE TABLE Client (
                    client_name VARCHAR(255),
                    public_key BLOB,
                    PRIMARY KEY (client_name)
                )
                """
            )
            cr.execute(
                """
                CREATE TABLE Topic (
                    topic_name VARCHAR(255),
                    PRIMARY KEY (topic_name)
                )
                """
            )
            cr.execute(
                """
                CREATE TABLE Subscribe (
                    client VARCHAR(255),
                    topic VARCHAR(255),
                    FOREIGN KEY(client) REFERENCES Client(client_name),
                    FOREIGN KEY(topic) REFERENCES Topic(topic_name)
                )
                """
            )
            conn.commit()
        except:
            print("Database was created!")
        conn.close()
    

    def ClientExist(self, client_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            SELECT client_name
            FROM Client
            WHERE client_name = '{client_name}'
            """
        )
        response = cr.fetchall()
        conn.commit()
        conn.close()
        
        if len(response) == 1:
            return True
        return False


    def TopicExist(self, topic_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            SELECT topic_name
            FROM Topic
            WHERE topic_name = '{topic_name}'
            """
        )
        response = cr.fetchall()
        conn.commit()
        conn.close()
        
        if len(response) == 1:
            return True
        return False


    def SubscribeExist(self, client_name, topic_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            SELECT client, topic
            FROM Subscribe
            WHERE topic = '{topic_name}' AND client = '{client_name}'
            """
        )
        response = cr.fetchall()
        conn.commit()
        conn.close()
        
        if len(response) == 1:
            return True
        return False


    def AddClient(self, client_name, public_key):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        data = (client_name, public_key)
        cr.execute(
            """
            INSERT INTO Client VALUES (?,?)
            """,
            data
        )
        conn.commit()
        conn.close()


    def AddTopic(self, topic_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            INSERT INTO Topic VALUES ('{topic_name}')
            """
        )
        conn.commit()
        conn.close()


    def AddSubscribe(self, client_name, topic_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        data = (client_name, topic_name)
        cr.execute(
            """
            INSERT INTO Subscribe VALUES (?,?)
            """,
            data
        )
        conn.commit()
        conn.close()


    def DeleteClient(self, client_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            DELETE FROM Client
            WHERE client_name = '{client_name}'
            """
        )
        conn.commit()
        conn.close()


    def DeleteSubscribe(self, client_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            DELETE FROM Subscribe
            WHERE client = '{client_name}'
            """
        )
        conn.commit()
        conn.close()


    def UpdateSubscribeInformation(self, client_name, list_topic):
        if not self.ClientExist(client_name):
            return 1
        else:
            self.DeleteSubscribe(client_name)
            for topic in list_topic:
                if not self.TopicExist(topic):
                    self.AddTopic(topic)
                
                self.AddSubscribe(client_name, topic)
                
        return 0


    def GetListClientSubscribeTopic(self, topic_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            SELECT client
            FROM Subscribe
            WHERE topic = '{topic_name}'
            """
        )

        list_client = cr.fetchall()
        for i in range(0, len(list_client)):
            list_client[i] = list_client[i][0]

        conn.commit()
        conn.close()

        return list_client


    def GetListClientAndKeySubscribeTopic(self, topic_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            SELECT client, public_key
            FROM Subscribe, Client
            WHERE topic = '{topic_name}' AND Client.client_name = Subscribe.client
            """
        )

        list_client_and_key = cr.fetchall()

        conn.commit()
        conn.close()

        return list_client_and_key


    def ShowTable(self, table_name):
        conn = sqlite3.connect(self.__database_part)
        cr = conn.cursor()
        cr.execute(
            f"""
            SELECT * FROM {table_name}
            """
        )

        print(f"---------------- TABLE {table_name} ----------------")
        table = cr.fetchall()
        for row in table:
            print(row)

        conn.commit()
        conn.close()
