from flask import Flask, render_template, url_for, request, redirect
from flask_mail import Mail, Message
from utils.user import User
import pandas as pd
from datetime import date
import datetime

app = Flask(__name__)
app.config.update({
    "DEBUG": True,
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 465,
    'MAIL_USE_SSL': True,
    'MAIL_USE_TLS': False,
    'MAIL_USERNAME': 'ipsit.iitb@gmail.com',
    'MAIL_PASSWORD': 'ipsitmantri2000'
})
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        users = pd.read_csv('users.csv', index_col=None, parse_dates=True)
        if str(request.form['ldap']) in users['Roll No'].values:
            idx = list(users['Roll No'].values).index(str(request.form['ldap']))
            if request.form['password'] == users['Password'].values[idx]:
                if (date.today() - datetime.datetime.strptime(users['Time Stamp'].values[idx],
                                                              '%Y-%m-%d').date()).days == 0:
                    error = 'You cannot log in today, come back tomorrow'
                else:
                    users['Time Stamp'].values[idx] = date.today()
                    users.to_csv('users.csv', index=False)
                    return redirect(url_for('health'))
            else:
                error = "Check your password!!"
        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route('/health', methods=['GET', 'POST'])
def health():
    if request.method == 'POST':
        user = User(request.form)
        user.save()
        return redirect(url_for('sendMail'))

    return render_template('health.html', error=None)


@app.route('/sent')
def sendMail():
    symptoms = {'s1': 'Slight fever',
                's2': 'Difficulty in breathing'}
    df = pd.read_csv('userData.csv', index_col=None)
    name = df['name'].values[-1]
    rollNo = df['rollNum'].values[-1]
    s = []
    for x in symptoms.keys():
        if df[x].values[-1] == True:
            s.append(x)
    msg = Message(
        sender='ipsit.iitb@gmail.com',
        recipients=['mmkipsit@gmail.com']
    )
    msg.subject = "{} Health Update".format(rollNo)
    msg.body = "{} has the following symptoms: \n".format(name)
    for ss in s:
        msg.body += symptoms[ss] + '\n'
    mail.send(msg)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
