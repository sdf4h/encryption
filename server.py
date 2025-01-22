from flask import Flask, jsonify, render_template
from datetime import datetime, timedelta
import threading
import time
import random
import string

app = Flask(__name__)

current_password = ''
next_update = None
update_interval = 3600  # Интервал обновления в секундах (например, каждый час)

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def update_password():
    global current_password, next_update
    while True:
        current_password = generate_password()
        next_update = datetime.now() + timedelta(seconds=update_interval)
        print(f"Новый пароль: {current_password} (будет обновлен в {next_update.strftime('%H:%M:%S')})")
        time.sleep(update_interval)

# Фоновая задача для обновления пароля
thread = threading.Thread(target=update_password)
thread.daemon = True
thread.start()

@app.route('/password')
def get_password():
    remaining_time = int((next_update - datetime.now()).total_seconds())
    return jsonify({
        'password': current_password,
        'remaining_time': remaining_time
    })

@app.route('/')
def index():
    remaining_time = int((next_update - datetime.now()).total_seconds())
    return render_template('index.html', password=current_password, remaining_time=remaining_time)

if __name__ == '__main__':
    app.run(debug=False)
