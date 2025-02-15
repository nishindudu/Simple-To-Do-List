import json
import configparser
import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = os.environ.get("KEY")

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

# storage('admin').add_to_list(['Task 1', 'Task 2', 'Task 3'])

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # if username == 'admin' and password == 'password':
        #     user = User(id=username)
        #     login_user(user)
        #     return redirect(url_for('index'))
        if storage(username).check_user(password):
            user = User(id=username)
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/add', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = storage(username)
        user.save_user(password)
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', tasks=storage(current_user.id).get_list())

@app.route('/add_item', methods=['POST'])
@login_required
def add_task():
    task = request.form['task']
    storage(current_user.id).add_to_list([task])
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)