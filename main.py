import json
import configparser
import os
import hashlib
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
app.secret_key = os.environ.get("KEY")

uri = os.environ.get("MONGO")

client = MongoClient(uri, server_api=ServerApi('1'))

class db():
    def __init__(self, id):
        self.id = id

    def ping_db():
        try:
            client.admin.command('ping')
            return True
        except:
            return False
    
    def save_user(self, password):
        db = client['todo']
        users = db['users']
        password = crypto().encrypt_sha256(password)
        if users.find_one({'id': self.id}):
            raise Exception('User already exists')
        else:
            users.insert_one({'id': self.id, 'password': password})
    
    def check_user(self, password):
        db = client['todo']
        users = db['users']
        user = users.find_one({'id': self.id})
        password = crypto().encrypt_sha256(password)
        if user and user['password'] == password:
            return True
        return False
    
    def get_list(self):
        db = client['todo']
        lists = db['lists']
        list = lists.find_one({'id': self.id})
        if list:
            return list['items']
        return []
    
    def add_to_list(self, items):
        if self.get_list() == []:
            db = client['todo']
            lists = db['lists']
            lists.insert_one({'id': self.id, 'items': items})
        else:
            db = client['todo']
            lists = db['lists']
            lists.update_one({'id': self.id}, {'$push': {'items': {'$each': items}}})

class crypto():
    def __init__(self):
        pass
    
    def encrypt_sha256(self, data):
        return hashlib.sha256(data.encode()).hexdigest()
    
# print(crypto().encrypt_sha256('password'))
# os.abort()



login_manager = LoginManager()
login_manager.init_app(app)


config = configparser.ConfigParser()

class storage():
    def __init__(self, id):
        self.id = id
    
    def add_to_list(self, items):
        list_item = {'id': self.id, 'item': items}
        if os.path.exists('./data/lists.json'):
            try:
                with open('./data/lists.json', 'r') as file:
                    existing_data = json.load(file)
                if not isinstance(existing_data, list):
                    existing_data = []
            except json.JSONDecodeError:
                existing_data = []
            for i in existing_data:
                if i['id'] == self.id:
                    i['item'].extend(items)
                    break
            else:
                existing_data.append(list_item)
        else:
            existing_data = [list_item]
        with open('./data/lists.json', 'w') as file:
            json.dump(existing_data, file)
    
    def get_list(self):
        if os.path.exists('./data/lists.json'):
            with open('./data/lists.json', 'r') as file:
                existing_data = json.load(file)
            if not isinstance(existing_data, list):
                existing_data = []
            for i in existing_data:
                if i['id'] == self.id:
                    return i['item']
        return []
    
    def save_user(self, password):
        if os.path.exists('./data/users.ini'):
            config.read('./data/users.ini')
            if not config.has_section('users'):
                config.add_section('users')
            config.set('users', self.id, password)
            with open('./data/users.ini', 'w') as file:
                config.write(file)
        else:
            config.add_section('users')
            config.set('users', self.id, password)
            with open('./data/users.ini', 'w') as file:
                config.write(file)
    
    def check_user(self, password):
        if os.path.exists('./data/users.ini'):
            config.read('./data/users.ini')
            if config.has_section('users'):
                if self.id in config['users'] and config['users'][self.id] == password:
                    return True
        return False

# db('admin').add_to_list(['Task 1', 'Task 2', 'Task 3'])

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/', methods=['GET', 'POST'])
# @app.route('/')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # if username == 'admin' and password == 'password':
        #     user = User(id=username)
        #     login_user(user)
        #     return redirect(url_for('index'))
        if db(username).check_user(password):
            user = User(id=username)
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/add', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db(username)
        try:
            user.save_user(password)
        except Exception as e:
            print(e)
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
@login_required
def index():
    return render_template('index.html', tasks=db(current_user.id).get_list())

@app.route('/add_item', methods=['POST'])
@login_required
def add_task():
    task = request.form['task']
    db(current_user.id).add_to_list([task])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)