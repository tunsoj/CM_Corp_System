# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_login import LoginManager, UserMixin, login_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cm-corp-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cm_corp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(100))

class User(UserMixin):
    def __init__(self, id): self.id = id

@login_manager.user_loader
def load_user(id): return User(id)

class RegForm(FlaskForm):
    name = StringField('Identitet', validators=[DataRequired()])
    email = StringField('Kommunikation', validators=[DataRequired(), Email()])
    role = StringField('Befattning', validators=[DataRequired()])
    submit = SubmitField('INITIALISERA')

@app.route('/', methods=['GET','POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.email.data).first():
            flash(u'VARNING: Identitet existerar redan.', 'warning')
        else:
            db.session.add(Subscriber(name=form.name.data, email=form.email.data, role=form.role.data))
            db.session.commit()
            flash(u'BEKRÄFTAT: Data lagrad i Core.', 'success')
            return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST' and request.form.get('pw')=='admin123':
        login_user(User(1))
        return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin(): return render_template('admin.html', subs=Subscriber.query.all())

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    db.session.delete(Subscriber.query.get(id))
    db.session.commit()
    return redirect(url_for('admin'))

if __name__=='__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
