# from Worky import create_app
from email.policy import default
from xmlrpc.client import DateTime
from flask import Flask, flash
from flask_login import user_accessed
from flaskext.mysql import MySQL
from pymysql import NULL
from sqlalchemy import null
from werkzeug.security import generate_password_hash, check_password_hash
# from tables import Description
import yaml
from flask import Blueprint, render_template, request, redirect, session
from datetime import date, datetime
import googleapiclient.discovery
import os
from google.oauth2 import service_account

# Working on Google Api's


app = Flask(__name__)

app.secret_key = 'your secret key'
# Database Configuration
db = yaml.load(open('db.yaml'))

app.config["MYSQL_DATABASE_HOST"] = db['mysql_host']
app.config["MYSQL_DATABASE_USER"] = db['mysql_user']
app.config["MYSQL_DATABASE_PASSWORD"] = db['mysql_password']
app.config["MYSQL_DATABASE_DB"] = db['mysql_db']
mysql = MySQL(app)


def get_credentials():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    GOOGLE_PRIVATE_KEY = os.environ["GOOGLE_PRIVATE_KEY"]
    # The environment variable has escaped newlines, so remove the extra backslash
    GOOGLE_PRIVATE_KEY = GOOGLE_PRIVATE_KEY.replace('\\n', '\n')

    account_info = {
        "private_key": GOOGLE_PRIVATE_KEY,
        "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
        "token_uri": "https://accounts.google.com/o/oauth2/token",
    }

    credentials = service_account.Credentials.from_service_account_info(
        account_info, scopes=scopes)
    return credentials


def get_service(service_name='sheets', api_version='v4'):
    credentials = get_credentials()
    service = googleapiclient.discovery.build(
        service_name, api_version, credentials=credentials)

    return service


@app.route('/updateDatabase')
def updatedatabase():
    service = get_service()
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    range_name = os.environ["GOOGLE_CELL_RANGE"]
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    res = []
    values = result.get('values', [])
    # removing duplicates
    for row in values:
        if row not in res:
            res.append(row)
    values = res
    # print(values)
    cur = mysql.get_db().cursor()

    for row in values:
        WMobileNo = row[0]
        cur.execute(
            "SELECT * FROM Worker where WMobileNo='{}'".format(WMobileNo))
        check = cur.fetchone()
        # print(WMobileNo, check)
        if check == None:
            continue
        cur.execute(
            "SELECT * FROM AcceptedRequest where WMobileNo='{}'".format(WMobileNo))
        Arequest = cur.fetchall()
        # print(Arequest)
        for eachRequest in Arequest:
            print(eachRequest)
            cur.execute("SELECT * FROM WorkRecord WHERE WMobileNo='{}' AND offer_id='{}' AND DateTime='{}'".format(
                eachRequest[0], eachRequest[1], eachRequest[2]))
            temp = cur.fetchone()
            # print(temp)
            cur.execute(
                "SELECT * FROM Offers where offer_id='{}'".format(eachRequest[1]))
            CMobileNo = cur.fetchone()
            CMobileNo = CMobileNo[0]
            # print(CMobileNo)
            cur.execute(
                "SELECT * FROM Customer WHERE CMobileNo='{}'".format(CMobileNo))
            CRating = cur.fetchone()
            CRating = CRating[1]
            # print(CRating)
            if temp == None:
                cur.execute(
                    "INSERT INTO WorkRecord(offer_id,WMobileNo,CRating,DateTime) VALUES(%s,%s,%s,%s)", (eachRequest[1], eachRequest[0], CRating, eachRequest[2]))
            else:
                cur.execute(
                    "UPDATE WorkRecord SET CRating='{}' where offer_id='{}' AND WMobileNo='{}' AND DateTime='{}'".format(CRating, eachRequest[1], eachRequest[0], eachRequest[2]))

                # cur.execute(
                # "DELETE FROM AcceptedRequest WHERE Offer_id =%s AND WMobileNo=%s", (eachRequest[0], WMobileNo))
            mysql.get_db().commit()
        cur.execute(
            "SELECT * FROM Worker WHERE WMobileNo='{}'".format(WMobileNo))
        MinWage = cur.fetchone()
        MinWage = MinWage[7]
        # for row in values:
        #     cur.execute(
        #         "SELECT a1.offer_id FROM ActiveOffers AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE Offers.CMobileNo != '{}' AND a1.offer_id NOT IN (SELECT offer_id FROM Request_Table WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM RejectedRequest WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM AcceptedRequest WHERE WMobileNo='{}') AND a1.offer_id IN  (With b1 as (SELECT b3.offer_id,DailyWage,Labour,Mechanic,Electrician,Carpentry FROM ActiveOffers AS b3 INNER JOIN Offers ON b3.offer_id=Offers.offer_id),b2 as (SELECT * FROM Worker where WMobileNo='{}') select b1.offer_id from b1,b2 where b1.DailyWage>=b2.MinPrice AND ((b1.Labour=1 and b2.Labour=1) or (b1.Electrician=1 and b2.Electrician=1) or (b1.Carpentry=1 and b2.Carpentry=1) or (b1.Mechanic=1 and b2.Mechanic=1))) AND Offers.DailyWage>='{}'".format(row[0], row[0], row[0], row[0], row[0], MinWage))
        #     Offers = cur.fetchall()
        #     for eachOfferId in Offers:
        #         cur.execute(
        #             "INSERT INTO Request_Table(WMobileNo,Offer_id) VALUES(%s,%s)", (WMobileNo, eachOfferId[0]))
        #         mysql.get_db().commit()
    mysql.get_db().commit()
    cur.close()
    return redirect('/')
    # request = service.spreadsheets().values().clear(
    # spreadsheetId=spreadsheet_id, range=range_name).execute()


@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/home1')
    user = session['user']
    userWorker = session['userWorker']
    print(user)
    print(userWorker)
    return render_template('home.html', user=user, userWorker=userWorker)


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
        Carpentry = request.form.get('five')
        others = request.form.get('six')
        now = datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')
        # Min prize
        MinPrize = request.form.get('MinWage')
        # Cursor of the database
        if len(Num) > 13:
            flash("Mobile Number's Digit Exceeding", category="error")
        elif len(Adhar_Id) > 12:
            flash("Adhar's Number Cannot Exceed 12 digits", category="error")
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif NA == 'on' and (Labour == 'on' or Mechanic == 'on' or Electrician == 'on' or Carpentry == 'on' or others == 'on'):
            flash(
                'Select NA for Customer otherwise Your class of work dont select both', category='error')
        else:
            password2 = generate_password_hash(password1, method='sha256')
            print(password2)
            password1 = generate_password_hash(password1, method='sha256')
            print(password1)
            print(type(password1))
            cur = mysql.get_db().cursor()
            cur.execute("INSERT INTO PERSON(MobileNo,Password,AdharNumber,Name,DOB,DateTime) VALUES(%s,%s,%s,%s,%s,%s)",
                        (Num, password1, Adhar_Id, name, dob, now))
            cur.execute(
                "INSERT INTO Customer(CMobileNo,CRating,NOE) VALUES(%s,%s,%s)", (Num, 0, 0))

            if NA != 'on':
                if others == 'on':
                    cur.execute("INSERT INTO Worker(WMobileNo,Labour,Mechanic,Electrician,Carpentry,WRating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                (Num, 1, 1, 1, 1, 0, 0, MinPrize))
                else:
                    cur.execute("INSERT INTO Worker(WMobileNo,Labour,Mechanic,Electrician,Carpentry,WRating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                (Num, Labour == 'on', Mechanic == 'on', Electrician == 'on', Carpentry == 'on', 0, 0, MinPrize))
            mysql.get_db().commit()
            cur.close()
            return redirect('/login')
        return redirect('/signup')
    # after signup user goes to login page
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userdetails = request.form
        Num = userdetails.get('typeNoX')
        password = userdetails.get('typePasswordX')
        password1 = generate_password_hash(password, method='sha256')
        # print(password1)

        # signup()

        cur = mysql.get_db().cursor()
        cur.execute("SELECT * FROM PERSON where MobileNo='%s'" % Num)
        user = cur.fetchone()
        cur.execute("SELECT * FROM Worker where WMobileNo='%s'" % Num)
        temp = cur.fetchone()
        if temp == None:
            temp = False
        else:
            temp = True
        cur.close()
        if user:
            if check_password_hash(user[1], password):
                flash('Logged in successfully!', category='success')

                session['loggedin'] = True
                session['MobileNo'] = user[0]
                session['Name'] = user[3]
                session['user'] = user
                session['userWorker'] = temp
                return redirect('/')
            else:
                flash('Password Not Correct!!!', category='error')
        else:
            flash('Mobile Number of Worker Not exist', category='error')
    return render_template('login.html')


@ app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('MobileNo', None)
    session.pop('Name', None)
    session.pop('user', None)
    return redirect('/home1')


@ app.route('/customer', methods=['GET', 'POST'])
def customer():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    userWorker = session['userWorker']
    cur = mysql.get_db().cursor()

    if request.method == 'POST':

        # extracting details from customer page
        workDetails = request.form
        Days = workDetails.get('days')
        Description = workDetails.get('description')
        location = workDetails.get('location')  # address
        Wage = workDetails.get('Price')
        labour = workDetails.get('labour')
        mechanic = workDetails.get('mechanic')
        electrician = workDetails.get('electrician')
        carpentry = workDetails.get('carpentry')
        others = workDetails.get('others')
        if labour == 0:
            others = 1
        if others:
            labour = 1
            mechanic = 1
            electrician = 1
            carpentry = 1
        now = datetime.now()
        Td = now.strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("INSERT INTO Offers(CMobileNo,Days,Description,DailyWage,Address,DateTime,Labour,Mechanic,Electrician,Carpentry) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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
    return render_template('customers.html', user=user, data=data, userWorker=userWorker)


@ app.route('/worker')
def worker():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    skill = session['userWorker']  # skill-->userWorker
    cur = mysql.get_db().cursor()
    cur.execute(
        "SELECT * FROM ActiveOffers AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE Offers.CMobileNo != '{}' AND a1.offer_id NOT IN (SELECT offer_id FROM Request_Table WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM RejectedRequest WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM AcceptedRequest WHERE WMobileNo='{}') AND a1.offer_id IN  (With b1 as (SELECT b3.offer_id,Labour,Mechanic,Electrician,Carpentry FROM ActiveOffers AS b3 INNER JOIN Offers ON b3.offer_id=Offers.offer_id),b2 as (SELECT * FROM Worker where WMobileNo='{}') select b1.offer_id from b1,b2 where (b1.Labour=1 and b2.Labour=1) or (b1.Electrician=1 and b2.Electrician=1) or (b1.Carpentry=1 and b2.Carpentry=1) or (b1.Mechanic=1 and b2.Mechanic=1) )".format(user[0], user[0], user[0], user[0], user[0]))
    data = cur.fetchall()
    # data have those offer details:
    # 1.not in accepted table
    # 2.not in Rejected table
    # 3.not in Request table
    # 4.according to there match of type of work
    cur.execute(
        "with b1 as (SELECT a1.offer_id,a2.WMobileNo FROM ActiveOffers as a1 INNER JOIN Request_Table as a2 on a1.offer_id=a2.offer_id )SELECT * FROM b1 INNER JOIN Offers ON b1.offer_id=Offers.offer_id WHERE b1.WMobileNo='{}';".format(user[0]))
    requested = cur.fetchall()  # for show requested offer  by worker on worker page
    cur.execute(
        "SELECT DateTime FROM WorkRecord WHERE WMobileNo ='{}' AND CRating IS NOT NULL AND WRating IS NULL ".format(user[0]))
    data1 = cur.fetchall()
    print(data1)
    cur.execute(
        "SELECT * FROM AcceptedRequest AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE a1.WMobileNo ='{}' AND a1.DateTime Not IN (SELECT DateTime FROM WorkRecord WHERE WMobileNo = '{}' AND CRating IS NOT NULL AND WRating IS NULL)".format(user[0], user[0]))
    accept_offer = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('worker.html', data=data, requested=requested, accept_offer=accept_offer, skill=skill)


@ app.route('/offer')
def offer():
    return render_template('offer.html')


# for deleting the offer by the customers in customers page
@ app.route('/delete/<int:sno>')
def delete(sno):
    user = session['user']
    cur = mysql.get_db().cursor()
    # first we have to delete from active offer than we can delete from offer table.

    # first see is there any accepted Request or not
    cur.execute("SELECT * AcceptedRequest WHERE offer_id = %s", (sno))
    AcceptedRequest = cur.fetchall()
    if AcceptedRequest:
        # if there is accepted request then we have to rate all the accepted workers.
        for each in AcceptedRequest:
            cur.execute(
                "SELECT * FROM WorkRecord WHERE  offer_id='{}' AND WMobileNo='{}' AND DateTime='{}'".format(each[1], each[0], each[2]))
            data = cur.fetchone()
            deleteit = False  # crating
            cur.execute(
                "SELECT * FROM Worker WHERE WMobileNo='{}'".format(each[0]))
            worker = cur.fetchone()
            WRating = worker[5]
            if data != None:
                deleteit = True
            if data:
                # print("update Working")
                cur.execute(
                    "UPDATE WorkRecord SET WRating='{}' where offer_id='{}' AND WMobileNo='{}'AND DateTime='{}'".format(WRating, each[1], each[0], each[2]))
            else:
                cur.execute(
                    "INSERT INTO WorkRecord(offer_id,WMobileNo,WRating,DateTime) VALUES(%s,%s,%s,%s)", (each[1], each[0], WRating, each[2]))
            if deleteit:
                cur.execute(
                    "DELETE FROM AcceptedRequest WHERE Offer_id =%s AND WMobileNo=%s", (each[1], each[0]))
            cur.execute("UPDATE Worker SET WRating='{}' , Experience ='{}' WHERE WMobileNo='{}'".format(
                WRating, worker[6]+1, each[0]))
            cur.execute()
            mysql.get_db().commit()

    cur.execute("DELETE FROM ActiveOffers WHERE offer_id = %s", (sno))
    cur.execute(
        "DELETE FROM Offers WHERE offer_id =%s", (sno))
    mysql.get_db().commit()
    cur.close()
    return redirect("/customer")


@ app.route('/delete1/<int:sno>')  # for deleting requests by Workers
def delete1(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "DELETE FROM Request_Table WHERE offer_id =%s AND WMobileNo=%s ", (sno, user[0]))
    mysql.get_db().commit()
    cur.close()
    return redirect("/worker")


# link for reject option in whoreq page where customer
# reject worker request.
@ app.route('/reject/<int:sno>/<string:workerNo>')
def reject(sno=None, workerNo=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "DELETE FROM Request_Table WHERE Offer_id =%s AND WMobileNo=%s", (sno, workerNo))
    cur.execute(
        "INSERT INTO RejectedRequest(WMobileNo,Offer_id) VALUES(%s,%s)", (workerNo, sno))
    mysql.get_db().commit()
    cur.close()
    s = "/whoreq/%s" % sno
    return redirect(s)


# worker request from given work list
@ app.route('/req/<int:sno>')  # for requesting work by worker on sno worker id
def req(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "SELECT * FROM AcceptedRequest WHERE WMobileNo='{}'".format(user[0]))
    accepted = cur.fetchone()
    if accepted == None:
        cur.execute(
            "INSERT INTO Request_Table(WMobileNo,Offer_id) VALUES(%s,%s)", (user[0], sno))
    else:
        # accepted[2] is dateTime
        cur.execute(
            "SELECT * FROM WorkRecord WHERE WMobileNo='{}' AND Offer_id='{}' AND DateTime='{}'".format(user[0], accepted[1], accepted[2]))
        wr = cur.fetchone()
        if wr == None:
            flash('first Complete your Work and then Rate it...', category='error')
        else:
            cur.execute(
                "INSERT INTO Request_Table(WMobileNo,Offer_id) VALUES(%s,%s)", (user[0], sno))

    mysql.get_db().commit()
    cur.close()
    return redirect("/worker")


@ app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    cur = mysql.get_db().cursor()
    user = session['user']
    if request.method == 'POST':
        # extracting details from customer page
        workDetails = request.form
        days = workDetails.get('days')
        description = workDetails.get('description')
        location = workDetails.get('location')  # address
        Price = workDetails.get('Price')
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

        print(user[0])
        cur.execute("UPDATE Offers SET Days=%s,Description=%s,DailyWage=%s,Address=%s, DateTime=%s, Labour=%s,  Mechanic=%s, Electrician=%s, Carpentry=%s WHERE offer_id =%s",
                    (days, description, Price, location, now, labour, mechanic, electrician, carpentry, sno))
        mysql.get_db().commit()
        cur.close()
        return redirect("/customer")
    cur.execute(
        "SELECT * FROM ActiveOffers as a1 INNER JOIN Offers as a2 ON  a1.offer_id=a2.offer_id WHERE a1.offer_id='%s'" % sno)
    data = cur.fetchone()
    mysql.get_db().commit()
    cur.close()
    return render_template('update.html', data=data)


@ app.route('/cusCompleted/<int:sno>/<string:WMobileNo>', methods=['GET', 'POST'])
def cusCompleted(sno=None, WMobileNo=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    if request.method == 'POST':
        rating = []
        for i in range(5):
            s = 'rating{}'.format(i+1)
            rating.append(request.form.get(s))
        WRating = None
        for i in range(5):
            if rating[i] != None:
                WRating = i+1
        if WRating == None:
            print("Hello")
            flash("rating cannot be empty", category="error")
            s1 = '/cusCompleted/{}/{}'.format(sno, WMobileNo)
            return redirect(s1)
        cur.execute(
            "SELECT * FROM AcceptedRequest WHERE offer_id='{}' AND WMobileNo='{}'".format(sno, WMobileNo))
        dateTime = cur.fetchone()
        dateTime = dateTime[2]
        cur.execute(
            "SELECT * FROM WorkRecord WHERE  offer_id='{}' AND WMobileNo='{}' AND DateTime='{}'".format(sno, WMobileNo, dateTime))
        data = cur.fetchone()
        # print(data)
        deleteit = False  # crating
        if data != None:
            deleteit = True
        # print(deleteit)
        if data:
            # print("update Working")
            cur.execute(
                "UPDATE WorkRecord SET WRating='{}' where offer_id='{}' AND WMobileNo='{}'".format(WRating, sno, WMobileNo))
        else:
            cur.execute(
                "INSERT INTO WorkRecord(offer_id,WMobileNo,WRating,DateTime) VALUES(%s,%s,%s,%s)", (sno, WMobileNo, WRating, dateTime))

        if deleteit:
            cur.execute(
                "DELETE FROM AcceptedRequest WHERE Offer_id =%s AND WMobileNo=%s", (sno, WMobileNo))
        cur.execute(
            "SELECT * FROM Worker WHERE WMobileNo='{}'".format(WMobileNo))
        worker = cur.fetchone()
        cur.execute("UPDATE Worker SET WRating='{}' , Experience ='{}' WHERE WMobileNo='{}'".format(
            (WRating+worker[5]*worker[6])/(worker[6]+1), worker[6]+1, WMobileNo))
        mysql.get_db().commit()
        cur.close()
        s = '/whoreq/{}'.format(sno)
        return redirect(s)
    cur.execute(
        "SELECT * FROM AcceptedRequest  where offer_id='{}' and WMobileNo='{}'".format(sno, WMobileNo))
    data = cur.fetchone()
    mysql.get_db().commit()
    cur.close()
    return render_template("cusCompleted.html", data=data)


@ app.route('/worCompleted/<int:sno>', methods=['GET', 'POST'])
def worCompleted(sno=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    # here user[0] is worker's Mobile No
    cur = mysql.get_db().cursor()
    if request.method == 'POST':
        rating = []
        for i in range(5):
            s = 'rating{}'.format(i+1)
            rating.append(request.form.get(s))
        CRating = None
        for i in range(5):
            if rating[i] != None:
                CRating = i+1
        if CRating == None:
            flash("rating cannot be empty", category="error")
            s1 = '/worCompleted/{}'.format(sno)
            return redirect(s1)
        cur.execute("SELECT * FROM Offers Where offer_id='{}'".format(sno))
        cmobile = cur.fetchone()
        cmobile = cmobile[0]
        cur.execute(
            "SELECT * FROM Customer Where CMobileNo='{}'".format(cmobile))
        temp = cur.fetchone()
        cur.execute("UPDATE Customer SET CRating='{}' , NOE ='{}' WHERE CMobileNo='{}'".format(
            (temp[1]*temp[2]+CRating)/(temp[2]+1), temp[2]+1, cmobile))
        cur.execute(
            "SELECT * FROM AcceptedRequest WHERE offer_id='{}' AND WMobileNo='{}'".format(sno, user[0]))
        dateTime = cur.fetchone()
        dateTime = dateTime[2]
        cur.execute(
            "SELECT * FROM WorkRecord WHERE offer_id='{}' AND WMobileNo='{}' AND DateTime='{}' ".format(sno, user[0], dateTime))
        data = cur.fetchone()
        deleteit = False  # crating
        if data != None:
            deleteit = True

        if data:
            cur.execute(
                "UPDATE WorkRecord SET CRating='{}' where offer_id='{}' AND WMobileNo='{}'".format(CRating, sno, user[0]))
        else:
            # print("Insert Working")
            now = datetime.now()
            Td = now.strftime('%Y-%m-%d %H:%M:%S')
            print(Td)
            cur.execute(
                "INSERT INTO WorkRecord(offer_id,WMobileNo,CRating,DateTime) VALUES(%s,%s,%s,%s)", (sno, user[0], CRating, dateTime))
        if deleteit:
            print("deleted your request")
            cur.execute(
                "DELETE FROM AcceptedRequest WHERE Offer_id =%s AND WMobileNo=%s", (sno, user[0]))
        mysql.get_db().commit()
        cur.close()
        return redirect("/worker")
    cur.execute(
        "SELECT * FROM AcceptedRequest where offer_id='{}' and WMobileNo='{}'".format(sno, user[0]))
    data = cur.fetchone()
    mysql.get_db().commit()
    cur.close()
    return render_template("worCompleted.html", data=data)


@ app.route('/accept/<int:sno>/<string:workerNo>')
def accept(sno=None, workerNo=None):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    now = datetime.now()
    Td = now.strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO AcceptedRequest(WMobileNo,Offer_id,DateTime) VALUES(%s,%s,%s)",
                (workerNo, sno, Td))
    cur.execute(
        "DELETE FROM Request_Table WHERE WMobileNo=%s", (workerNo))

    mysql.get_db().commit()
    cur.close()
    s = '/whoreq/{}'.format(sno)
    # s = '/'
    return redirect(s)


@ app.route('/whoreq/<int:sno>', methods=['GET', 'POST'])
def whoreq(sno):
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    cur = mysql.get_db().cursor()
    cur.execute(
        "with a1 as (SELECT b1.Offer_id , b1.WMobileNo , Worker.WRating FROM Request_Table as b1 INNER JOIN Worker on b1.WMobileNo=Worker.WMobileNo WHERE b1.Offer_id IN (SELECT offer_id FROM ActiveOffers) AND b1.Offer_id=%s)     SELECT a1.Offer_id , a1.WMobileNo , a1.WRating , PERSON.Name  FROM a1 INNER JOIN PERSON on a1.WMobileNo=PERSON.MobileNo" % sno)
    data = cur.fetchall()
    cur.execute("with a1 as (SELECT b1.Offer_id , b1.WMobileNo , Worker.WRating FROM AcceptedRequest as b1 INNER JOIN Worker on b1.WMobileNo=Worker.WMobileNo WHERE b1.Offer_id IN (SELECT offer_id FROM ActiveOffers) AND b1.Offer_id='{}' AND b1.DateTime NOT IN (SELECT DateTime FROM WorkRecord WHERE offer_id ='{}' AND WRating IS NOT NULL AND CRating IS NULL))         SELECT a1.Offer_id , a1.WMobileNo , a1.WRating , PERSON.Name  FROM a1 INNER JOIN PERSON on a1.WMobileNo=PERSON.MobileNo".format(sno, sno))
    accept_data = cur.fetchall()
    mysql.get_db().commit()
    cur.close()
    return render_template('whoreq.html', data=data, sno=sno, accept_data=accept_data)


if __name__ == '__main__':
    app.run(debug=True)