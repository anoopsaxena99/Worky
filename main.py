# from Worky import create_app
from email.policy import default
from flask import Flask
from flaskext.mysql import MySQL
from pymysql import NULL
import yaml
from flask import Blueprint,render_template,request
from datetime import datetime

app=Flask(__name__)


#Database Configuration
db=yaml.load(open('db.yaml'))

app.config["MYSQL_DATABASE_HOST"] = db['mysql_host']
app.config["MYSQL_DATABASE_USER"] = db['mysql_user']
app.config["MYSQL_DATABASE_PASSWORD"] = db['mysql_password']
app.config["MYSQL_DATABASE_DB"] = db['mysql_db']
mysql=MySQL(app)

<<<<<<< HEAD
#routes on the website
=======
class customer_work(db.model1):
  sno = db.Column(db.Integer, primery_key = True)
  work_title = db.Column(db.String(300), nullable = True)
  desc = db.Column(db.String(500), nullable = True)
  wotype = db.Column(db.String(50), nullable = True)
  Location = db.Column(db.String(50), nullable = True)
  date_created = db.Column(db.Datetime, default = datetime.utcnow)


>>>>>>> 5ecbaebca4bdf71a0574892ca8e3f240e09bfaf1
@app.route('/')
def home():
  return render_template('home.html')

@app.route('/guide')
def guide():
  return render_template('guide.html')  

@app.route('/support')
def support():
  return render_template('support.html') 

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/customer')
def customer():
  return render_template('customer.html')

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
    
        #wage related
    NA1=request.form.get('wage_na')    
    min_salary=request.form.get('min_salary')

    #Cursor of the database

    cur = mysql.get_db().cursor()
    cur.execute("SELECT * from users where email='%s'"%email1)
    rows = cur.fetchall()
    if(rows!=NULL) : 
      x=0
      for row in rows:
        print(row[0])
        x=x+1
      print("{0} no of entries already there".format(x))   
      return("{0} no of entries already there".format(x))  
    cur.execute("INSERT INTO users(name,email) VALUES(%s,%s)",(name ,email))
    mysql.get_db().commit()
    cur.close()
    return('SUCCESS')    
  return render_template("signup.html")  

if __name__ == '__main__' :
  app.run(debug=True)