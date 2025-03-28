from flask import Flask, render_template, redirect, url_for, request, session
from flask_oauthlib.client import OAuth
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'
oauth = OAuth(app)

#Google OAuth
google = oauth.remote_app(
    'google',
    consumer_key='YOUR_GOOGLE_CLIENT_ID',
    consumer_secret='YOUR_GOOGLE_CLIENT_SECRET',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

#Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, email):
        self.email = email

@login_manager.user_loader
def load_user(email):
    return User(email)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('google_token')
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or 'access_token' not in response:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    user = User(user_info.data['email'])
    
    login_user(user)
    
    return redirect(url_for('create_poll'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/create_poll', methods=['POST'])
@login_required
def create_poll():
    if request.method == 'POST':
        if request.method == 'POST':
            question = request.form['question']
            options = request.form['options'].split(',')
            options = [option.strip() for option in options]
            polls.append({'question': question, 'options': options})
            return redirect(url_for('index'))
        pass
    return render_template('create_poll.html')

@app.route('/polls')
@login_required
def show_polls():
    return render_template('polls.html', polls=polls)

if __name__ == '__main__':
    app.run(debug=True)
