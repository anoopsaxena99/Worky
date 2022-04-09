# from Worky import create_app
from email.policy import default
from flask import Flask
from flaskext.mysql import MySQL
from pymysql import NULL
#from tables import Description
import yaml
from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.secret_key = 'your secret key'
# Database Configuration
db = yaml.load(open('db.yaml'))

app.config["MYSQL_DATABASE_HOST"] = db['mysql_host']
app.config["MYSQL_DATABASE_USER"] = db['mysql_user']
app.config["MYSQL_DATABASE_PASSWORD"] = db['mysql_password']
app.config["MYSQL_DATABASE_DB"] = db['mysql_db']
mysql = MySQL(app)


# class customer_work(db.model1):
#   sno = db.Column(db.Integer, primery_key = True)
#   work_title = db.Column(db.String(300), nullable = True)
#   desc = db.Column(db.String(500), nullable = True)
#   wotype = db.Column(db.String(50), nullable = True)
#   Location = db.Column(db.String(50), nullable = True)
#   date_created = db.Column(db.Datetime, default = datetime.utcnow)

# routes on the website
# routes on the website


@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/home1')
    user = session['user']
    return render_template('home.html', user=user)


@app.route('/home1')
def home1():
    return render_template('home1.html')


@app.route('/guide')
def guide():
    return render_template('guide.html')


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        user = session['user']
        return redirect('/')
    if request.method == 'POST':
        # data from sign up page
        userdetails = request.form

        # personal stuff
        Num = userdetails.get('typeNumX')
        Adhar_Id = userdetails.get('adhar')

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        name = userdetails.get('name')
        dob = request.form.get('dob')
        Adress = request.form.get('adress')

        # skills details
        NA = request.form.get('one')
        Labour = request.form.get('two')
        Mechanic = request.form.get('three')
        Electrician = request.form.get('four')
        Carpentary = request.form.get('five')
        others = request.form.get('six')
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        # Min prize
        MinPrize = request.form.get('MinWage')
        # Cursor of the database

        cur = mysql.get_db().cursor()

        cur.execute("INSERT INTO PERSON(MobileNo,Password,AdharNumber,Name,DOB,DateTime) VALUES(%s,%s,%s,%s,%s,%s)",
                    (Num, password1, Adhar_Id, name, dob, now))
        cur.execute(
            "INSERT INTO CUSTOMER(CMobileNo,CRating,NOE) VALUES(%s,%s,%s)", (Num, 0, 0))

        if others == 'on':
            cur.execute("INSERT INTO WORKER(WMobileNo,Labour,Mechanic,Electrician,Carpentary,WRating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                        (Num, 1, 1, 1, 1, 0, 0, MinPrize))
        else:
            cur.execute("INSERT INTO WORKER(WMobileNo,Labour,Mechanic,Electrician,Carpentary,WRating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                        (Num, Labour == 'on', Mechanic == 'on', Electrician == 'on', Carpentary == 'on', 0, 0, MinPrize))
        mysql.get_db().commit()
        cur.close()
    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userdetails = request.form
        Num = userdetails.get('typeNoX')
        password = userdetails.get('typePasswordX')

        cur = mysql.get_db().cursor()
        cur.execute("SELECT * FROM PERSON where MobileNo='%s'" % Num)
        user = cur.fetchone()  # fetchall can also be used
        # print(user[MobileNo])
        cur.execute("SELECT * FROM Worker where WMobileNo='%s'" % Num)
        userWorker = cur.fetchone()
        cur.close()

        if user:
            if password == user[1]:
                session['loggedin'] = True
                session['MobileNo'] = user[0]
                session['Name'] = user[3]
                session['user'] = user
                session['userWorker'] = userWorker
                return render_template('home.html', user=user)
            else:
                return "password not correct"
        else:
            return "Mobile number Not Exists!!!"

    if 'user' in session:
        user = session['user']
        return redirect('/')  # check
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('MobileNo', None)
    session.pop('Name', None)
    session.pop('user', None)
    return redirect('/login')


@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()

    if request.method == 'POST':

        # extracting details from customer page
        workDetails = request.form
        Wt = workDetails.get('title')
        Days = workDetails.get('days')
        Description = workDetails.get('description')
        location = workDetails.get('location')  # address
        Wage = workDetails.get('Price')
        labour = workDetails.get('labour')
        mechanic = workDetails.get('mechanic')
        electrician = workDetails.get('electrician')
        carpentry = workDetails.get('carpentry')
        others = workDetails.get('others')
        if others:
            labour = 1
            mechanic = 1
            electrician = 1
            carpentry = 1
        now = datetime.now()
        Td = now.strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("INSERT INTO Offers(CMobileNo,Days,Description,DailyWage,Address,DateTime,Labour,Mechanic,Electrician,Carpentary) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (user[0], Days, Description, Wage, location, now, labour, mechanic, electrician, carpentry))

        mysql.get_db().commit()
        cur.execute("SELECT * FROM Offers WHERE DateTime='{}'".format(now))
        Of = cur.fetchone()
        cur.execute("INSERT INTO ActiveOffers(offer_id) VALUES(%s)" % Of[1])
        mysql.get_db().commit()
        cur.close()
        return redirect('/customer')

    cur.execute(
        "SELECT * FROM ActiveOffers as a1 INNER JOIN Offers as a2 ON  a1.offer_id=a2.offer_id WHERE a2.CMobileNo='%s'" % user[0])
    data = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('customers.html', user=user, data=data)


@app.route('/worker')
def worker():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    skill = session['userWorker']
    cur = mysql.get_db().cursor()
    cur.execute(
        "SELECT * FROM ActiveOffers AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE Offers.CMobileNo != '{}' AND a1.offer_id NOT IN (SELECT offer_id FROM Request_Table WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM RejectedRequest WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM AcceptedRequest WHERE WMobileNo='{}')".format(user[0], user[0], user[0], user[0]))
    data = cur.fetchall()  # need to specify request according to their interest
    cur.execute(
        "SELECT * FROM Request_Table AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE a1.WMobileNo ='{}'".format(user[0]))
    requested = cur.fetchall()
    cur.execute(
        "SELECT * FROM AcceptedRequest AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE a1.WMobileNo ='{}'".format(user[0]))
    accept_offer = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('worker.html', data=data, requested=requested, accept_offer=accept_offer, skill=skill)


@app.route('/offer')
def offer():
    return render_template('offer.html')


@app.route('/delete/<int:sno>')
def delete(sno):
    cur = mysql.get_db().cursor()
    cur.execute("DELETE FROM Offers WHERE offer_id ='%s'" % sno)
    mysql.get_db().commit()
    cur.close()
    return redirect("/customer")


@app.route('/delete1/<int:sno>')  # for deleting requests by Workers
def delete1(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "DELETE FROM Request_Table WHERE offer_id =%s AND UserMobileNo=%s ", (sno, user[0]))
    mysql.get_db().commit()
    cur.close()
    return redirect("/worker")


# link for reject option in whoreq page where customer
# reject worker request.
@app.route('/reject/<int:sno>/<string:workerNo>')
def reject(sno=None, workerNo=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "DELETE FROM Request_Table WHERE Offer_id =%s AND UserMobileNo=%s", (sno, workerNo))
    mysql.get_db().commit()
    cur.close()
    s = "/whoreq/%s" % sno
    return redirect(s)


# worker request from given work list
@app.route('/req/<int:sno>')  # for requesting work by worker on sno worker id
def req(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "INSERT INTO Request_Table(UserMobileNo,Offer_id) VALUES(%s,%s)", (user[0], sno))
    mysql.get_db().commit()
    cur.close()
    return redirect("/worker")


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    cur = mysql.get_db().cursor()
    if request.method == 'POST':
        days = request.form['days']
        description = request.form['description']
        location = request.form['location']
        price = request.form['Price']
        cur.execute("UPDATE Offers SET Days=%s,Description=%s,DailyWage=%s,Address=%s WHERE offer_id =%s",
                    (days, description, price, location, sno))
        mysql.get_db().commit()
        cur.close()
        return redirect("/customer")
    cur.execute("SELECT * FROM Offers WHERE offer_id ='%s'" % sno)
    data = cur.fetchone()
    mysql.get_db().commit()
    cur.close()
    return render_template('update.html', data=data)


@app.route('/cusCompleted/<int:sno>', methods=['GET', 'POST'])
def cusCompleted(sno=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    if request.method == 'POST':
        crating = request.form['crating']
        cur.execute("SELECT * FROM WorkRecord where offer_id='%s'" % sno)
        data = cur.fetchone()
        if data:
            cur.execute(
                "UPDATE WorkRecord SET CRating=%s where offer_id=%s", (crating, sno))
        else:
            cur.execute(
                "SELECT * FROM Accepted_Request where offer_id=%s AND CustomerMobile=%s", (sno, user[0]))
            wor = cur.fetchone()
            cur.execute(
                "INSERT INTO WorkRecord(offer_id,WorkerMob,CRating) VALUES(%s,%s,%s)", (sno, wor[0], crating))
            mysql.get_db().commit()
            cur.close()
            return("success")
        mysql.get_db().commit()
        cur.close()
        return redirect("/customer")
    cur.execute("SELECT * FROM Offers where offer_id='%s'" % sno)
    data = cur.fetchone()
    mysql.get_db().commit()
    cur.close()
    return render_template("cusCompleted.html", data=data)


@app.route('/worCompleted/<int:sno>', methods=['GET', 'POST'])
def worCompleted(sno=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    if request.method == 'POST':
        wrating = request.form['wrating']
        cur.execute("SELECT * FROM WorkRecord where offer_id='%s'" % sno)
        data = cur.fetchone()
        if data:
            cur.execute(
                "UPDATE WorkRecord SET WRating=%s where offer_id=%s", (wrating, sno))
        else:
            cur.execute(
                "INSERT INTO WorkRecord(offer_id,WorkerMob,WRating) VALUES(%s,%s,%s)", (sno, user[0], wrating))
            mysql.get_db().commit()
            cur.close()
            return("success")
        mysql.get_db().commit()
        cur.close()
        return redirect("/customer")
    cur.execute("SELECT * FROM Offers where offer_id='%s'" % sno)
    data = cur.fetchone()
    mysql.get_db().commit()
    cur.close()
    return render_template("worCompleted.html", data=data)


@app.route('/accept/<int:sno>/<string:workerNo>')
def accept(sno=None, workerNo=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute("INSERT INTO Accepted_Request(WorkerMobile,CustomerMobile,Offer_id) VALUES(%s,%s,%s)",
                (workerNo, user[0], sno))
    # cur.execute("DELETE FROM Requested_")
    mysql.get_db().commit()
    cur.close()
    return("Success")


@app.route('/whoreq/<int:sno>', methods=['GET', 'POST'])
def whoreq(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "WITH A1 as (SELECT UserMobileNo FROM Request_Table WHERE offer_id ='%s') SELECT A1.UserMobileNo , PERSON.Name FROM A1 INNER JOIN PERSON ON A1.UserMobileNo=PERSON.MobileNo" % sno)
    data = cur.fetchall()
    cur.execute(
        "WITH A1 as (SELECT * FROM Accepted_Request where CustomerMobile=%s) SELECT PERSON.name,A1.WorkerMobile FROM A1 INNER JOIN PERSON ON A1.WorkerMobile=PERSON.MobileNo where offer_id=%s ;", (user[0], sno))
    accept_data = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('whoreq.html', data=data, sno=sno, accept_data=accept_data)


if __name__ == '__main__':
    app.run(debug=True)
