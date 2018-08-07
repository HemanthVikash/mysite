from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import widgets
from wtforms import RadioField, TextAreaField, TextField, FormField, FieldList, HiddenField,SelectField
from wtforms.validators import Optional
#from wtforms.compat import with_metaclass, iteritems, itervalues
from wtforms.meta import DefaultMeta
import logging
from collections import OrderedDict

from flask_wtf.csrf import CSRFProtect
import os

logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
logging.debug('This message should go to the log file')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://runaway57:propaganda@runaway57.mysql.pythonanywhere-services.com/runaway57$frames"
app.secret_key = "runaway57$frames"
db = SQLAlchemy(app)
crsf = CSRFProtect(app)

CATEGORIES = ["PROBLEMATIZATION"]

SUBCATEGORIES = {
    "PROBLEMATIZATION":["Ethnicity or Race","Nationality or Immigrant status","Sexual Orientation","Religious Conviction/Belief","Political Views","Sex/Gender/Gender Identity"]
}

index_range = []
header = []
start_idx = 0
for idx in range(len(CATEGORIES)):
    index_range.append(start_idx)
    start_idx += len(SUBCATEGORIES[CATEGORIES[idx]])
    header.append("Code for text in category: "+CATEGORIES[idx]);
index_range.append(start_idx)



class Tweets(db.Model):
    __tablename__ = 'TWEETS'
    tweetid = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(16), primary_key=True)
    completed = db.Column(db.Boolean)

    def serialize(self):
        return {"tweetid": self.tweetid, "completed": self.completed}


class Codes(db.Model):
    __tablename__ = 'CODES'
    tweetid = db.Column(db.String(50), primary_key=True)
    subcategory = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(16), primary_key=True)
    exist = db.Column(db.Boolean)
    text = db.Column(db.String(5000))
    __table_args__ = (db.ForeignKeyConstraint([tweetid], [Tweets.tweetid]), {})


class dynamicForm(FlaskForm):
    logging.info("Inside the dynamicForm class")
    nameofuser = TextField("Enter your name here")





@app.route("/<username>/", methods=["POST", "GET"])
@app.route("/<username>/<int:page>/", methods=["POST", "GET"])
#@app.route("/<username>/<int:page>/<tweetid>", methods=["POST", "GET"])
def showSurvey(page=1, tweetid="",username=""):
    #Change 2
    catlist = ['Ethnicity_or_Race', 'Nationality_or_Immigrant_status', 'Sexual_Orientation', 'Religious_Conviction_Belief', 'Political_Views',  'Sex_Gender_Gender_Indentity']

    #Change 3 - got rid of completed=false
    tweets = Tweets.query.filter_by(username=username).order_by(Tweets.tweetid)
    if len(tweetid) > 0:
        tweets = Tweets.query.filter_by(tweetid=tweetid,username=username)
    if tweets.count() < page:
        return redirect(url_for('submitted'))


    posts = tweets.paginate(page, 1, False)

    #Change 4
    tweetid = posts.items[0].tweetid
    logging.info(tweetid)

    #Change 5 Look at the completed tweets
    if posts.items[0].completed == True:
        logging.info("Inside completed tweets")
        response = OrderedDict()
        for code in catlist:
            ans = Codes.query.filter_by(tweetid=tweetid, subcategory = code, username=username)
            if ans[0].exist==True or ans[0].exist== '1' or ans[0].exist==1 or ans[0].exist == 'yes':
                r = '1'
            else:
                r = '0'
            #r = ans[0].exist
            t = ans[0].text
            r_l = code+ '_r'
            t_l = code+ '_t'
            response[r_l] = r
            response[t_l] = t
            logging.info("%s, %s, %s, %s", r_l, r, t_l, t)

        for k, v in response.iteritems():
            if k.endswith("_r"):
                setattr(dynamicForm, k, RadioField(k.strip("_r"), choices=[('0', 'no'), ('1', 'yes')], default = v))
            else:
                setattr(dynamicForm, k, TextField(k.strip("_t"), default = v))
        form = dynamicForm()
        #form = dynamicForm()

    else:
        logging.info("Inside the incomplete else")

        response = OrderedDict()
        for code in catlist:
            r_l = code+ '_r'
            t_l = code+ '_t'
            response[r_l] = '0'
            response[t_l] = ''
            logging.info("%s, 0, %s, none", r_l , t_l)

        for k, v in response.iteritems():
            if k.endswith("_r"):
                setattr(dynamicForm, k, RadioField(k.strip("_r"), choices=[('0', 'no'), ('1', 'yes')], default = '0'))
            else:
                setattr(dynamicForm, k, TextField(k.strip("_t")))


        form = dynamicForm()

    if form and form.validate_on_submit():
        session = db.session

        logging.info('this is inside the form validation condition')
        ctweets = []
        tweetid = posts.items[0].tweetid
        ###################Making changes here
        if posts.items[0].completed == True:

            for question in form.data:
                if len(form.data[question]) > 0 and question[len(question)-1] == "r":
                    session.query(Codes).filter_by(username=username, tweetid = tweetid,subcategory=question[:-2]).update({"exist":int(form.data[question]), "text":form.data[question[:-1]+"t"]})


            for tweet in tweets:
                if tweetid==tweet.tweetid:
                    setattr(tweet, 'completed', True)

            try:
                session.commit()
                logging.info("updated rows in the database")

            except Exception as e:
                logging.info("rollback from inside dataset updation")
                session.rollback()


        else:
        ###################
            for question in form.data:
                if len(form.data[question]) > 0 and question[len(question)-1] == "r":
                    x = Codes(username=username, tweetid=tweetid, subcategory=question[:-2], exist=int(form.data[question]), text=form.data[question[:-1]+"t"])
                    ctweets.append(x)


            for tweet in tweets:
                if tweetid==tweet.tweetid:
                    setattr(tweet, 'completed', True)


            try:
                #session.execute(update(completed[0]))
                session.add_all(ctweets)
                session.commit()
                logging.info("added unique response to the database")
            except Exception as e:
                print(e)
                logging.info(e)
                logging.info("inside session rollback: whatever that means")
                session.rollback()
            #session.rollback()


        if tweets.count() > 0:
            return redirect(url_for('showSurvey', page=page,username=username))
        else:
            return redirect(url_for('submitted'))

    logging.info("printing form here")
    logging.info(form)

    return render_template("main_page.html", posts=posts, username=username, response = response, form=form, page=page, tweet_id=tweetid,pagesLeft = tweets.count()-1, header=header, index_range=index_range)


############################################################

############################################################
@app.route("/submitted", methods=["GET"])
def submitted():
    return "Thanks for using this coding framework"


