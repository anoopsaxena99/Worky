# from flask import Flask
# from flask import Blueprint,render_template,request
# from flaskext.mysql import MySQL


# auth=Blueprint('auth',__name__)
# @auth.route('/login')
# def login():
#   return render_template('login.html')

# @auth.route('/signup',methods=['GET','POST'])
# def signup():
#   if request.method == 'POST':
#     userdetails=request.form
#     email=userdetails['typeEmailX']
#     name=userdetails['name']

#     # cur=mysql.connection.cursor()
#     cur = mysql.get_db().cursor()
#     cur.execute("INSERT INTO users(name,email) VALUES(%s,%s)",(name ,email))
#     mysql.get_db().commit()
#     cur.close()
#     return('SUCCESS')    
#   return render_template("signup.html")  
