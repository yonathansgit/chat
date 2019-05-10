import sqlite3

class DB_convs_management(object):

    def __init__(self, path):
        self.path = path
        self.connction = sqlite3.connect(self.path)

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE conversations(ID INTEGER PRIMARY KEY, account TEXT,
                               message TEXT unique, chat_room_ID TEXT, msg_date TEXT, msg_hour TEXT)
        ''')

        self.connection.commit()

    def import_msg(self, CR_ID):
        ID = "\'" + str(CR_ID) + "\'"
        cursor = self.connction.cursor()
        return cursor.execute('''
            SELECT account_ID, message, msg_date, msg_hour, uuid FROM conversations WHERE chat_room_ID = ''' + ID)

    def insert_msg(self, account_IDVal, messageVal, room_ID, dateVal, hourVal, uuid_val):
        cursor = self.connction.cursor()
        cursor.execute('''INSERT INTO conversations(account_ID, message, chat_room_ID, msg_date, msg_hour, uuid)
                                 VALUES(?,?,?,?,?,?)''', (account_IDVal, messageVal, room_ID, dateVal, hourVal, uuid_val))
        self.connction.commit()

    def get_msgs_ID(self):
        cursor = self.connction.cursor()
        return cursor.execute('''SELECT ID FROM conversations''')

    def get_latest_msgs(self, last_sent, acc_ID, cr_ID):
        cursor = self.connction.cursor()
        sent = "\'" + str(last_sent) + "\'"
        account_ID = "\'" + str(acc_ID) + "\'"
        crID = "\'" + str(cr_ID) + "\'"
        return cursor.execute('''SELECT account_ID, message, chat_room_ID, msg_date, msg_hour, uuid FROM conversations WHERE ID > ''' + sent + ''' AND account_ID != ''' + account_ID  + ''' AND chat_room_ID = ''' + crID)

    def get_last_refreshed(self, uuid):
        cursor = self.connction.cursor()
        return cursor.execute('''SELECT ID FROM conversations WHERE uuid = ''' + "\'" + uuid + '\'')



