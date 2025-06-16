from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set this to something secure

# In-memory storage (resets on app restart)
users = {}

# Candidate info
candidates = {
    "56": {"name": "Mr. Steve Jobs", "party": "United National Party", "image": "candidate1.png", "votes": 0},
    "73": {"name": "Mr. Albert Einstein", "party": "Freedom Liberation Front", "image": "candidate2.jpg", "votes": 0},
    "88": {"name": "Mr. Barack Obama", "party": "Democratic Alliance", "image": "candidate3.jpg", "votes": 0},
    "95": {"name": "Mr. Rowan Atkinson", "party": "People's Voice", "image": "candidate4.jpg", "votes": 0},
    "42": {"name": "Mrs. Marilyn Monroe", "party": "Progressive Movement", "image": "candidate5.jpg", "votes": 0},
    "62": {"name": "Mr. Mahinda Rajapaksha", "party": "People's Party", "image": "candidate6.jpg", "votes": 0},
    "76": {"name": "Mr. Che Guevara", "party": "Communist Freedom Society", "image": "candidate7.jpg", "votes": 0},
    "99": {"name": "Mr. Will Smith", "party": "Sunflower Unity", "image": "candidate8.jpg", "votes": 0}
}

# Protect routes with login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        id_number = request.form['id_number'].strip()
        password = request.form['password'].strip()

        if not username or not id_number or not password:
            flash('Please fill in all fields.')
            return redirect(url_for('register'))

        if username in users:
            flash('Username already taken.')
            return redirect(url_for('register'))

        for user in users.values():
            if user['id_number'] == id_number:
                flash('ID number already registered.')
                return redirect(url_for('register'))

        password_hash = generate_password_hash(password)

        users[username] = {
            'id_number': id_number,
            'password_hash': password_hash,
            'has_voted': False
        }

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        id_number = request.form['id_number']
        password = request.form['password']

        user = users.get(username)
        if user and user['id_number'] == id_number and check_password_hash(user['password_hash'], password):
            if user['has_voted']:
                flash("You have already voted.")
                return redirect(url_for('results'))
            session['username'] = username
            return redirect(url_for('vote'))
        else:
            flash("Invalid login credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if request.method == 'POST':
        candidate_number = request.form.get('candidate')
        if candidate_number and candidate_number in candidates:
            candidates[candidate_number]['votes'] += 1
            users[session['username']]['has_voted'] = True
            session.pop('username', None)
            return render_template('success.html', candidate=candidates[candidate_number])
        else:
            flash("Invalid selection.")
            return redirect(url_for('vote'))

    return render_template('vote.html', candidates=candidates)

@app.route('/results')
def results():
    return render_template('results.html', candidates=candidates)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
