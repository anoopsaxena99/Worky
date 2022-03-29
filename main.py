# from Worky import create_app
from email.policy import default
from flask import Flask
from flaskext.mysql import MySQL
from pymysql import NULL
import yaml
from flask import Blueprint,render_template,request,redirect,session
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

app=Flask(__name__)

app.secret_key = 'your secret key'
#Database Configuration
db=yaml.load(open('db.yaml'))

app.config["MYSQL_DATABASE_HOST"] = db['mysql_host']
app.config["MYSQL_DATABASE_USER"] = db['mysql_user']
app.config["MYSQL_DATABASE_PASSWORD"] = db['mysql_password']
app.config["MYSQL_DATABASE_DB"] = db['mysql_db']
mysql=MySQL(app)


# class customer_work(db.model1):
#   sno = db.Column(db.Integer, primery_key = True)
#   work_title = db.Column(db.String(300), nullable = True)
#   desc = db.Column(db.String(500), nullable = True)
#   wotype = db.Column(db.String(50), nullable = True)
#   Location = db.Column(db.String(50), nullable = True)
#   date_created = db.Column(db.Datetime, default = datetime.utcnow)

#routes on the website
#routes on the website



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

@app.route('/login',methods=['GET','POST'])
def login():
  if request.method == 'POST':
    userdetails=request.form
    Num=userdetails.get('typeNoX')
    password=userdetails.get('typePasswordX')

    cur = mysql.get_db().cursor()
    cur.execute("SELECT * from PERSON where MobileNo='%s' LIMIT 1"%Num)
    user=cur.fetchone()#fetchall can also be used
    #print(user[MobileNo])
    cur.close()

    if user :
      if password==user[1] :
        session['loggedin'] = True
        session['MobileNo'] = user[0]
        session['Name'] = user[3]
        session['user'] = user
        return render_template('home.html',user=user)  
      else:
        return "password not correct" 
    else :
      return "Email Not Exists!!!"  
    
  if 'user' in session:
    user = session['user']
    return redirect('/')      ##check
  return render_template('login.html')


@app.route('/logout')
# @login_required
def logout():
  session.pop('loggedin', None)
  session.pop('MobileNo', None)
  session.pop('Name', None)
  session.pop('user', None)
  return redirect('/login')


@app.route('/customer',methods=['GET','POST'])
def customer():
  if 'user' not in session:
    return redirect('/login')
  user = session['user'] 
  cur = mysql.get_db().cursor() 
  
  if request.method == 'POST':
    print("Hello Guys")
    #extracting details from customer page 
    workDetails=request.form
    Wt=workDetails.get('title')
    Days=workDetails.get('days')
    Description=workDetails.get('description')
    location=workDetails.get('location')#address
    Wage=workDetails.get('Price')
    cur.execute("SELECT COUNT(*) FROM Offers")
    count=cur.fetchone()

    cur.execute("SELECT * FROM Offers WHERE MobileNo='%s'"%user[0])
    data=cur.fetchall()  

    print(count)
    cur.execute("INSERT INTO Offers(MobileNo,Days,Description,DailyWage,Address) VALUES(%s,%s,%s,%s,%s)",(user[0],Days,Description,Wage,location))
    mysql.get_db().commit()
    cur.close()
    return render_template('home.html', user=user)
  
  cur.execute("SELECT * FROM Offers WHERE MobileNo='%s'"%user[0])
  data=cur.fetchall()  
  mysql.get_db().commit()
  cur.close()
  return render_template('customers.html',user=user,data=data)

@app.route('/worker')
def worker():
  return render_template('worker.html')

@app.route('/offer')
def offer():
  return render_template('offer.html')
    
@app.route('/signup',methods=['GET','POST'])
def signup():
  if request.method == 'POST':
    userdetails=request.form

    #data from sign up page

        #personal stuff
    Num=userdetails.get('typeNumX')
    Adhar_Id=userdetails.get('adhar')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    name=userdetails.get('name')
    dob = request.form.get('dob')
    Adress=request.form.get('adress')



        #skills details
    NA=request.form.get('one')
    Labour=request.form.get('two')
    Mechanic=request.form.get('three')
    Electrician=request.form.get('four')
    Carpentary=request.form.get('five')
    others=request.form.get('six')
    
    # Min prize 
    MinPrize=500
    #Cursor of the database

    cur = mysql.get_db().cursor()

    cur.execute("INSERT INTO PERSON(MobileNo,Password,AdharNumber,Name,DOB) VALUES(%s,%s,%s,%s,%s)",(Num,password1,Adhar_Id,name,dob))
    if NA :
      cur.execute("INSERT INTO CUSTOMER(MobileNo,Rating,NOE) VALUES(%s,%s,%s)",(Num,0,0))
    #   #cur.execute("SELECT * FROM CUSTOMER WHERE NOE=1")
    #   #rowi=cur.fetchall()
    #   #print(rowi)
    else :
      if others=='on' :
        cur.execute("INSERT INTO WORKER(MobileNo,Labour,Mechanic,Electrician,Carpentary,Rating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(Num,1,1,1,1,0,0,MinPrize))  
      else :
        cur.execute("INSERT INTO WORKER(MobileNo,Labour,Mechanic,Electrician,Carpentary,Rating,Experience,MinPrice) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(Num,Labour=='on',Mechanic=='on',Electrician=='on',Carpentary=='on',0,0,MinPrize))  
    mysql.get_db().commit()
    cur.close()
    # if NA :
    #   #return Customer page

    # else :
    #   #it will be worker page  


    # return render_template('customer.html')
    # cur.execute("SELECT * from users where email='%s'"%email1)
    # rows = cur.fetchall()
    # if(rows!=NULL) : 
    #   x=0
    #   for row in rows:
    #     print(row[0])
    #     x=x+1
    #   print("{0} no of entries already there".format(x))   
    #   return("{0} no of entries already there".format(x))  
    # cur.execute("INSERT INTO users(name,email) VALUES(%s,%s)",(name ,email))
    # mysql.get_db().commit()
    # cur.close()
    # return('SUCCESS')    
  if 'user' in session:
    user = session['user']
    return redirect('/')  
  return render_template("signup.html")  

if __name__ == '__main__' :
  app.run(debug=True)