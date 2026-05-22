from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, register_user, login_user, get_user_by_id, update_user_profile
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'qwerty123'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs('static/avatars', exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


init_db()


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('index.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        success, message = register_user(username, password, email, full_name)
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, result = login_user(username, password)
        if success:
            session['user_id'] = result['id']
            session['username'] = result['username']
            flash(f'Добро пожаловать, {result["username"]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash(result, 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])
    if request.method == 'POST':
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        avatar_filename = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                if user['avatar'] and user['avatar'] != 'default_avatar.png':
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], user['avatar'])
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = f"user_{session['user_id']}_{secure_filename(file.filename)}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                avatar_filename = filename
        update_user_profile(session['user_id'], email, full_name, avatar_filename)
        flash('Профиль успешно обновлён!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
