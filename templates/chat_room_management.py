import sqlite3


class DB_CR_handler(object):


    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.connect(self.path)

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE chat_rooms(id INTEGER PRIMARY KEY, accounts TEXT,
                               cr_name TEXT)
        ''')

        self.connection.commit()


    def find_chat_room(self, name, acc_ID):
        cursor = self.connection.cursor()
        account = "\'" + "%," + str(acc_ID) + ",%" + "\'"
        return cursor.execute('''SELECT ID FROM chat_rooms WHERE cr_name = ''' + '\'' + name + '\'' ''' AND accounts_ID LIKE ''' + account)


    def search_for_cr(self, acc_ID, exp):
        cursor = self.connection.cursor()
        account = "\'" + "%," + str(acc_ID) + ",%" + "\'"
        expression = "\'" + "%" + exp + "%" + "\'"
        return cursor.execute('''SELECT ID, cr_name, cr_avatar, description FROM chat_rooms WHERE cr_name LIKE ''' + expression + ''' AND accounts_ID LIKE ''' + account)


    def find_all_cr_for_account(self, acc_ID):
        cursor = self.connection.cursor()
        account = "\'" + "%," + str(acc_ID) + ",%" + "\'"
        return cursor.execute('''SELECT ID, cr_name, cr_avatar, description FROM chat_rooms WHERE accounts_ID LIKE ''' + account)


    def new_chat_room(self, name, accounts, avatar_path, desc):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO chat_rooms(accounts_ID, cr_name, cr_avatar, description)
                                 VALUES(?,?,?,?)''', (accounts, name, avatar_path, desc))
        self.connection.commit()


    def check_existence(self, acc_ID, name):
        cursor = self.connection.cursor()
        final_ID = "\'" + "%," + acc_ID + ",%" + "\'"
        final_name = "\'" + name + "\'"
        return cursor.execute('''SELECT cr_name FROM chat_rooms WHERE cr_name = ''' + final_name + ''' AND accounts_ID LIKE ''' + final_ID)
