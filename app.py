from flask import Flask
from flask import request
from flask import render_template
from flask import make_response
from flask import redirect, url_for
import json
from templates.account_management import *
from templates.chat_room_management import *
from templates.convs_management import *
from templates.hash_processor import *
import logging, os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import uuid




db_path = 'C:\\Users\\yonat\\OneDrive\\Documents\\Chatter_lineDB.db'





app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/static/profile_picture'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=["GET", "POST"])
def login():
    account = accounting_operations()
    if 'user' in request.cookies:
        return render_template("home_page.html", error="")

    elif request.method == "GET":
        return render_template("Login.html", error="")

    else:
        login_username = request.values.get("email")
        login_password = request.values.get("pass")


        if account.check_data(login_username, login_password):
            return account.create_cookie(login_username, login_password)

        else:
            return render_template("Login.html", error="incorrect email or password")


@app.route('/register', methods=["GET", "POST"])
def register():
    account = accounting_operations()
    if request.method == 'POST':
        try:
            account.save_data()
            email = request.values.get("your_email")
            password = request.values.get("password")
        except Exception as e:
            return render_template("register.html", error="your email or username might already be used")
        return account.create_register_cookie(email, password)
    else:
        return render_template("register.html", error="")


@app.route('/avatar_creation', methods=["GET", "POST"])
def get_avatar():
    if request.method == 'POST':
        try:
            accounts = accounting_operations()
            app.logger.info(app.config['UPLOAD_FOLDER'])
            img = request.files['pic']
            img_name = secure_filename(img.filename)
            account_ID = accounts.get_account_ID() + 1
            name_split = img_name.split('.')
            name = str(account_ID) + "." + name_split[1]
            create_new_folder(app.config['UPLOAD_FOLDER'])
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], name)
            app.logger.info("saving {}".format(saved_path))
            img.save(saved_path)
            send_from_directory(app.config['UPLOAD_FOLDER'], name, as_attachment=True)
            accounts.re_save_data(name)
            return redirect(url_for("login"))
        except:
            name = "images.png"
            accounts.re_save_data(name)
            return redirect(url_for("login"))
    else:
        return render_template("avatar_creation.html")


@app.route('/home_page', methods=["GET", "POST"])
def save_msg():
    if 'user' in request.cookies:
        cookie_value = request.cookies.get('user')
        split_cookie = cookie_value.split(" ")
        email = split_cookie[0]
        db = DB_account_handler(db_path)
        username = db.findID_with_email(email)
        return "OK"


@app.route('/enter_chat_room', methods=["GET", "POST"])
def load_chat_room():
    CR_name = request.values.get("name")

    cr_db = DB_CR_handler(db_path)
    conv_db = DB_convs_management(db_path)

    account_class = accounting_operations()
    message_class = messaging_operations()

    account_ID = account_class.get_account_ID()
    cr_ID = cr_db.find_chat_room(CR_name, account_ID).fetchone()[0]
    conv = conv_db.import_msg(cr_ID).fetchall()
    final_conv = message_class.avatar_to_account(conv)
    final_conv.insert(0, account_ID)
    return json.dumps(final_conv)


@app.route('/message_sending', methods=["GET", "POST"])
def save_messages():
    print(1)
    msg = request.values.get("msg")
    room_name = request.values.get("cr_name")
    date_time = request.values.get("time")

    db_room = DB_CR_handler(db_path)
    db_conv = DB_convs_management(db_path)
    db_accounts = DB_account_handler(db_path)

    class_accounts = accounting_operations()
    class_messages = messaging_operations()

    date = class_messages.set_date(date_time)
    hour = class_messages.set_hour(date_time)
    account_ID = class_accounts.get_account_ID()
    uuid_var = str(uuid.uuid4())

    room_ID = db_room.find_chat_room(room_name, account_ID).fetchone()[0]
    db_conv.insert_msg(account_ID, msg, room_ID, date, hour, uuid_var)

    db_room.connection.close()
    db_conv.connction.close()
    db_accounts.connection.close()

    final_var = date + " " + hour + "," + str(uuid_var)
    return final_var


@app.route('/search_room', methods=["GET", "POST"])
def search_rooms():
    expression = request.values.get("exp")
    db_cr = DB_CR_handler(db_path)
    class_accounting = accounting_operations()
    account_ID = class_accounting.get_account_ID()
    ID_names = db_cr.search_for_cr(account_ID, expression).fetchall()
    if ID_names == []:
        return json.dumps("")

    else:
        return json.dumps(ID_names)


@app.route('/search_rooms_else', methods=["GET", "POST"])
def refill_rooms():
    db_cr = DB_CR_handler(db_path)
    class_accounting = accounting_operations()
    account_ID = class_accounting.get_account_ID()
    ID_names = db_cr.find_all_cr_for_account(account_ID).fetchall()
    return json.dumps(ID_names)


@app.route('/search_messages', methods=["GET", "POST"])
def search_msgs():
    try:
        last_uuid = request.values.get("id")
        cr_name = request.values.get("name")

        db_convs = DB_convs_management(db_path)
        db_cr = DB_CR_handler(db_path)
        try:
            account_ID = accounting_operations().get_account_ID()
            cr_id = db_cr.find_chat_room(cr_name, account_ID).fetchone()[0]
            last_id = db_convs.get_last_refreshed(last_uuid).fetchone()[0]
            last_convs = db_convs.get_latest_msgs(last_id, account_ID, cr_id).fetchall()
            final_conv = messaging_operations().avatar_to_account(last_convs)

            db_convs.connction.close()
            db_cr.connection.close()

            return json.dumps(final_conv)

        except:
            db_convs.connction.close()
            db_cr.connection.close()
            return "no messages"
    except:
        return "no messages"






@app.route('/suggest_account', methods=["GET", "POST"])
def suggest_email():
    db_accounts = DB_account_handler(db_path)
    suggestions = db_accounts.get_all_with_exp().fetchall()
    email_list = []
    for email in suggestions:
        email_list.append(email[0])
    db_accounts.connection.close()
    return email_list



@app.route('/new_chat_room', methods=["GET", "POST"])
def create_new_cr():
    if request.method == 'POST':
        print(1)
        cr_name = request.values.get("new_cr_name")
        cr_members = request.values.get("ncr_users_list")
        description = request.values.get("new_description")

        if description == '':
            description = "Description"


        db_cr = DB_CR_handler(db_path)
        db_acc = DB_account_handler(db_path)

        try:
            account_ID = accounting_operations().get_account_ID()
            members = cr_members.split(',')
            members_list = []
            check_list = []
            members_list.append("," + str(account_ID) + ",")
            check_list.append(str(account_ID))
            check_list.append(str(db_acc.findID_with_email(members[0]).fetchone()[0]))
            members_list.append("," + str(db_acc.findID_with_email(members[0]).fetchone()[0]) + ",")
            for index in range(len(members)):
                if index + 1 != len(members):
                    middle_members = members[index + 1].split(' ')[1]
                    if middle_members != '':
                        account_ID_2 = db_acc.findID_with_email(middle_members).fetchone()[0]
                        if account_ID_2 != account_ID:
                            check_list.append(str(account_ID_2))
                            string = "," + str(account_ID_2) + ","
                            members_list.append(string)


                else:
                    break

            for ID in check_list:
                check = db_cr.check_existence(ID, cr_name).fetchall()
                if check != []:
                    db_cr.connection.close()
                    db_acc.connection.close()
                    return render_template("home_page.html", error="some user(s) might already have a chat room called %s : please change the name. Please press home to return to the main page" %(cr_name))



            try:
                app.logger.info(app.config['UPLOAD_FOLDER'])
                img = request.files['ncr_avatar_pic']
                img_name = secure_filename(img.filename)
                create_new_folder(app.config['UPLOAD_FOLDER'])
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
                app.logger.info("saving {}".format(saved_path))
                img.save(saved_path)
                send_from_directory(app.config['UPLOAD_FOLDER'], img_name, as_attachment=True)
                path = "/static/profile_picture/" + img_name

                final_members = "".join(members_list)
                db_cr.new_chat_room(cr_name, final_members, path, description)
                db_cr.connection.close()
                return redirect(url_for("login"))

            except:
                path = "/static/profile_picture/users-icon.png"
                final_members = "".join(members_list)
                db_cr.new_chat_room(cr_name, final_members, path, description)
                db_cr.connection.close()
                return redirect(url_for("login"))

        except:
            db_cr.connection.close()
            return redirect(url_for("login"))
    else:
        return  "Problem with the server, please come back later"
















@app.route('/return_home', methods=["GET", "POST"])
def return_home():
    resp = make_response(render_template("Login.html"))
    resp.set_cookie('user', expires=0)
    print("cookies deleted")
    return resp








def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath












class accounting_operations(object):
    def __init__(self):
        self.self = self

    def create_cookie(self, username, password):
        resp = make_response(render_template("home_page.html", error=""))
        string = str(username) + " " + str(hash_expression(password))
        resp.set_cookie('user', value=string)
        return resp

    def create_register_cookie(self, email, password):
        resp = make_response(redirect(url_for("get_avatar")))
        string = str(email) + " " + str(hash_expression(password))
        resp.set_cookie('user', value=string)
        return resp

    def get_cookie(self):
        if 'user' in request.cookies:
            cookie = request.cookies.get("user")
            return cookie
        else:
            return None

    def get_email_with_cookie(self):
        cookie = self.get_cookie()
        if cookie != None:
            split_cookie = cookie.split(" ")
            email = split_cookie[0]
            return email
        else:
            return render_template("Login.html", error="this website is using cookies, please login to create them. Once login, please do not remove the cookies.")

    def save_data(self):
        username = request.values.get("full_name")
        email = request.values.get("your_email")
        password = hash_expression(request.values.get("password"))
        db = DB_account_handler(db_path)
        db.create_user(username, email, password)

    def check_data(self, email, password):
        password_final = hash_expression(password)
        db = DB_account_handler(db_path)
        length = db.find_user(email, password_final)
        found = length.fetchone()
        if found == None:
            return False
        else:
            return True

    def get_account_ID(self):
        email = self.get_email_with_cookie()
        db_accounts = DB_account_handler(db_path)
        ID = db_accounts.findID_with_email(email).fetchone()[0]
        return ID



    def re_save_data(self, path):
        db_accounts = DB_account_handler(db_path)
        last_acc = db_accounts.get_last_account().fetchone()
        username = last_acc[1]
        password = last_acc[2]
        email = last_acc[3]
        avatar = "/static/profile_picture/" + path
        db_accounts.replace_account(username, password, email, avatar)




class messaging_operations(object):
    def __init__(self):
        self.self = self

    def get_messages(self, CR_ID):
        room_ID = CR_ID[0]
        db = DB_convs_management(db_path)
        messages = db.import_msg(room_ID)
        return messages.fetchall()

    def messages_by_account(self, messages):
        if messages == None:
            return None

        elif isinstance(messages, tuple):
            print("in tuple")
            final_list = []
            final_list.append(messages[0])
            final_list.append(messages[1])
            return final_list

        elif isinstance(messages, list):
            accounts_list = []
            final_list = []
            for index in range(len(messages)):
                for tuple_index in range(len(messages[index])):
                    if messages[index][0] not in accounts_list:
                        accounts_list.append(messages[index][0])

            for index in range(len(messages)):
                in_first_if = False
                test_count = 0
                if len(final_list) == 0:
                    accounts_message = list(messages[0])
                    final_list.append(accounts_message)
                    in_first_if = True

                for final_index in range(len(final_list)):
                    if messages[index][0] == final_list[final_index][0] and messages[index][1] != \
                            final_list[final_index][1]:
                        middle_list = list(messages[index])
                        middle_list.pop(0)
                        final_list[final_index].append("".join(middle_list))

                    else:
                        test_count += 1

                if test_count == len(final_list) and in_first_if == False:
                    accounts_message = list(messages[index])
                    final_list.append(accounts_message)
        new_list = []
        for index in range(len(final_list)):
            new_list.append(tuple(final_list[index]))

        final_conv = tuple(new_list)
        print(final_conv)
        return final_conv


    def set_date(self, expression):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        exp_split = expression.split(" ")
        for value in exp_split:
            for month in months:
                if value == month:
                    month_num = months.index(month) + 1
                    break

        day = exp_split[2]
        year = exp_split[3]
        date = day + "/" + str(month_num) + "/" + year
        return date


    def set_hour(self, expression):
        exp_split = expression.split(" ")
        hour_sec = exp_split[4]
        hour_split = hour_sec.split(":")
        hour = hour_split[0] + ":" + hour_split[1]
        return hour


    def search_account_msgs(self, messages):
        class_accounts = accounting_operations()
        db_rooms = DB_CR_handler(db_path)
        account_ID = class_accounts.get_account_ID()
        cr_IDs = db_rooms.find_all_cr_for_account(account_ID)
        account_msg_list = []
        for data in messages:
            for CR in cr_IDs:
                if data[3] == CR and data[1] != account_ID:
                    account_msg_list.append(data)

        return account_msg_list


    def avatar_to_account(self, conversation):
        class_accounts = accounting_operations()
        db_accounts = DB_account_handler(db_path)
        account_ID = class_accounts.get_account_ID()
        conv = []
        for message in conversation:
            if message[0] != account_ID:
                path = db_accounts.get_pp_path_ID(message[0]).fetchone()
                conv.append(message + path)
            else:
                conv.append(message)

        return conv


    def get_counter(self):
        f = open("/Users/yonathan/PycharmProjects/ChatterLine/templates/conv_ID_sent", "r")
        lines = f.readlines()
        f.close()
        return lines

    def modify_counter(self, new_val):
        f = open("/Users/yonathan/PycharmProjects/ChatterLine/templates/conv_ID_sent", "w")
        f.writelines(str(new_val))
        f.close()









class rooms_operations(object):
    def __init__(self):
        self.self = self

    def retain_room_ID(self, num, ID = None):
        if num == 0:
            var = 0
        elif num == 1:
            var = 1
        else:
            var = 2

        while var != 1:
            ID = ID





if __name__ == '__main__':
    app.run()



