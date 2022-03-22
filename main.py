# from Worky import create_app
from flask import Flask
from flaskext.mysql import MySQL
import yaml
from flask import Blueprint,render_template,request

app=Flask(__name__)

db=yaml.load(open('db.yaml'))
  

app.config["MYSQL_DATABASE_HOST"] = db['mysql_host']
app.config["MYSQL_DATABASE_USER"] = db['mysql_user']
app.config["MYSQL_DATABASE_PASSWORD"] = db['mysql_password']
app.config["MYSQL_DATABASE_DB"] = db['mysql_db']
mysql=MySQL(app)

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

@app.route('/signup',methods=['GET','POST'])
def signup():
  if request.method == 'POST':
    userdetails=request.form
    email=userdetails.get('typeEmailX')
    name=userdetails.get('name')

    # cur=mysql.connection.cursor()
    cur = mysql.get_db().cursor()
    cur.execute("INSERT INTO users(name,email) VALUES(%s,%s)",(name ,email))
    mysql.get_db().commit()
    cur.close()
    return('SUCCESS')    
  return render_template("signup.html")  

if __name__ == '__main__' :
  app.run(debug=True)