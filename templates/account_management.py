import sqlite3


class DB_account_handler(object):

    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.connect(self.path)


    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE accounts_management(id INTEGER PRIMARY KEY, username TEXT,
                               email TEXT unique, password TEXT)
        ''')

        self.connection.commit()


    def create_user(self, usernameVal, emailVal, passwordVal):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO accounts_management(username, email, password)
                          VALUES(?,?,?)''', (usernameVal, emailVal, passwordVal))
        print("user added to %s"%self.path)
        self.connection.commit()


    def find_user(self, input_email, input_password):
        cursor = self.connection.cursor()
        return cursor.execute('''SELECT username, password FROM accounts_management
         WHERE email = ? AND password = ?''',(input_email, input_password))


    def insert_avatar(self, avatar_path):
        cursor = self.connection.cursor()
        return cursor.execute('''INSERT INTO accounts_management(avatar)
                                VALUES(?)''', avatar_path)


    def findID_with_email(self, email):
        cursor = self.connection.cursor()
        return cursor.execute('''SELECT ID FROM accounts_management WHERE email = ''' + '\'' + email + '\'')


    def find_email(self, email):
        cursor = self.connection.cursor()
        return cursor.execute('''SELECT * FROM accounts_management
            WHERE email = ''' + '\'' + email + '\'')


    def find_username(self, username):
        cursor = self.connection.cursor()
        return cursor.execute('''SELECT * FROM accounts_management
            WHERE username = ''' + '\'' + username + '\'')


    def get_last_account(self):
        cursor = self.connection.cursor()
        return cursor.execute('''SELECT * FROM accounts_management WHERE ID = (SELECT MAX(ID) FROM accounts_management)''')

    def replace_account(self, usernameVal, passwordVal, emailVal, avatarPath):
        cursor = self.connection.cursor()
        cursor.execute('''REPLACE INTO accounts_management(username, password, email, avatar)
                          VALUES (?,?,?,?)''', (usernameVal, passwordVal, emailVal, avatarPath))
        self.connection.commit()


    def get_pp_path_ID(self, ID):
        cursor = self.connection.cursor()
        account = "\'" + str(ID) + "\'"
        return cursor.execute('''SELECT avatar FROM accounts_management WHERE ID = ''' + account)


    def get_all_with_exp(self):
        cursor = self.connection.cursor()
        return cursor.execute('''SELECT email FROM accounts_management''')
