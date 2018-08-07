from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import widgets
from wtforms import RadioField, TextAreaField, TextField, FormField, FieldList, HiddenField,SelectField
from wtforms.validators import Optional
from flask_wtf.csrf import CSRFProtect
import os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://runaway57:propaganda@runaway57.mysql.pythonanywhere-services.com/runaway57$frames"
app.secret_key = "runaway57$frames"
db = SQLAlchemy(app)
crsf = CSRFProtect(app)


class Tweets(db.Model):
    __tablename__ = 'TWEETS'
    tweetid = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(16), primary_key=True)
    completed = db.Column(db.Boolean)

    def serialize(self):
        return {"tweetid": self.tweetid, "username": self.username ,"completed": self.completed}


userlist = ["shruti", "mattia", "test"]

def main():
    with open('batch1.csv', 'rb') as csvfile:
        tweets = csv.reader(csvfile)
        cnt = 0
        all_tweets = []
        for tweetid in tweets:
            print(tweetid)
            cnt += 1
            # ignore header line
            if cnt == 1:
                continue
            for username in userlist:
                tweet = Tweets()
                setattr(tweet,'tweetid',tweetid[0])
                setattr(tweet,'completed',False)
                setattr(tweet,'username',username)
                all_tweets.append(tweet)
        session = db.session
        try:
            session.add_all(all_tweets)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            session.rollback()

if __name__ == '__main__':
    main()