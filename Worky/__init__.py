# from flask import Flask
# from flaskext.mysql import MySQL
# import yaml

# def create_app():
#   app=Flask(__name__)
#   db=yaml.load(open('db.yaml'))
  

#   app.config["MYSQL_DATABASE_HOST"] = db['mysql_host']
#   app.config["MYSQL_DATABASE_USER"] = db['mysql_user']
#   app.config["MYSQL_DATABASE_PASSWORD"] = db['mysql_password']
#   app.config["MYSQL_DATABASE_DB"] = db['mysql_db']

#   from .views import views
#   from .auth import auth

#   app.register_blueprint(views, url_prefix='/')
#   app.register_blueprint(auth,url_prefix='/')

#   return app