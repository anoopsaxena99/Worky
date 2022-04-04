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
        return redirect('/login')
    user = session['user']
    return render_template('home.html', user=user)


@app.route('/guide')
def guide():
    return render_template('guide.html')


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userdetails = request.form
        Num = userdetails.get('typeNoX')
        password = userdetails.get('typePasswordX')

        cur = mysql.get_db().cursor()
        cur.execute("SELECT * from PERSON where MobileNo='%s'" % Num)
        user = cur.fetchone()  # fetchall can also be used
        # print(user[MobileNo])
        cur.close()

        if user:
            if password == user[1]:
                session['loggedin'] = True
                session['MobileNo'] = user[0]
                session['Name'] = user[3]
                session['user'] = user
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
        cur.execute("SELECT * FROM Offers WHERE MobileNo='%s'" % user[0])
        data = cur.fetchall()

        cur.execute("INSERT INTO Offers(MobileNo,Days,Description,DailyWage,Address) VALUES(%s,%s,%s,%s,%s)",
                    (user[0], Days, Description, Wage, location))
        mysql.get_db().commit()
        cur.close()
        return render_template('customers.html', user=user)
        return redirect('/customer')

    cur.execute("SELECT * FROM Offers WHERE MobileNo='%s'" % user[0])
    data = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('customers.html', user=user, data=data)


@app.route('/worker')
def worker():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    # cur.execute("SELECT Offer_id FROM Request_Table WHERE MobileNo='%s'"%user[0])
    cur.execute(
        "SELECT * FROM Accepted_Request WITH A1 as (SELECT * FROM Request_Table WHERE offer_id ='%s')")
    cur.execute(
        "SELECT * FROM Offers WHERE offer_id NOT IN (SELECT Offer_id FROM Request_Table WHERE UserMobileNo='%s' )" % user[0])
    data = cur.fetchall()
    cur.execute(
        "SELECT * FROM Offers WHERE offer_id IN (SELECT Offer_id FROM Request_Table WHERE UserMobileNo='%s' )" % user[0])
    requested = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('worker.html', data=data, requested=requested)


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
@app.route('/reject/<int:sno>')
def reject(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "DELETE FROM Request_Table WHERE Offer_id =%s AND UserMobileNo=%s ", (sno, user[0]))
    mysql.get_db().commit()
    cur.close()
    return redirect("/whoreq")



#worker request from given work list 
@app.route('/req/<int:sno>')
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


@app.route('/accept/<int:sno>/<string:workerNo>')
def accept(sno=None, workerNo=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute("INSERT INTO Accepted_Request(WorkerMobile,CustomerMobile,Offer_id) VALUES(%s,%s,%s)",
                (workerNo, user[0], sno))
    mysql.get_db().commit()
    cur.close()
    return("Success")


@app.route('/whoreq/<int:sno>', methods=['GET', 'POST'])
def whoreq(sno):
    cur = mysql.get_db().cursor()
    cur.execute("WITH A1 as (SELECT UserMobileNo FROM Request_Table WHERE offer_id ='%s') SELECT A1.UserMobileNo , PERSON.Name FROM A1 INNER JOIN PERSON ON A1.UserMobileNo=PERSON.MobileNo" % sno)
    data = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('whoreq.html', data=data, sno=sno)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        userdetails = request.form

        # data from sign up page

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

        # Min prize
        MinPrize = 500
        # Cursor of the database

        cur = mysql.get_db().cursor()

        cur.execute("INSERT INTO PERSON(MobileNo,Password,AdharNumber,Name,DOB) VALUES(%s,%s,%s,%s,%s)",
                    (Num, password1, Adhar_Id, name, dob))
        if NA:
            cur.execute(
                "INSERT INTO CUSTOMER(MobileNo,Rating,NOE) VALUES(%s,%s,%s)", (Num, 0, 0))
        #   #cur.execute("SELECT * FROM CUSTOMER WHERE NOE=1")
        #   #rowi=cur.fetchall()
        #   #print(rowi)
        else:
            if others == 'on':
                cur.execute("INSERT INTO WORKER(MobileNo,Labour,Mechanic,Electrician,Carpentary,Rating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                            (Num, 1, 1, 1, 1, 0, 0, MinPrize))
            else:
                cur.execute("INSERT INTO WORKER(MobileNo,Labour,Mechanic,Electrician,Carpentary,Rating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                            (Num, Labour == 'on', Mechanic == 'on', Electrician == 'on', Carpentary == 'on', 0, 0, MinPrize))
        mysql.get_db().commit()
        cur.close()
    if 'user' in session:
        user = session['user']
        return redirect('/')
    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)
