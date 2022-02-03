"""

How to run :
1) Download all dependent thing
2)run in  cmd  "python file_name"
3)
localhost:5000/
http://127.0.0.1:5000/
"""

"""
Import Library
pip install flask
pip install flask_sqlalchemy
pip install werkzeug.security
pip install pandas

"""
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

"""
Create DataBase environment
"""
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="postgresql://postgres:janvi@localhost/oneassure"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
db=SQLAlchemy(app)

"""
Create a User Database for Login and Register by creating user table and using three arguments
ID, EMAIL, PASSWORD
"""
class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(40))
    password=db.Column(db.String(200))
    

    def __init__(self,email,password,):
        self.email=email
        self.password=password


"""
Create a Data Database for Saving the csv file by creating data table and using three arguments
ID, Fname, Lname
"""

class Data(db.Model):
    __tablename__='data'
    id=db.Column(db.Integer,primary_key=True)
    Fname=db.Column(db.String(40), nullable=True)
    Lname=db.Column(db.String(40), nullable=True)

    def __init__(self,Fname,Lname):
        self.Fname=Fname
        self.Lname=Lname

@app.route('/')
def index():
    return { "mess": "Welcome"}

"""
For user registration

link: http://127.0.0.1:5000/register

Syntax: API TESTING
        {
    "name":"xxxxxxxxxxxx@gmail.com",
    "password":"xxxxxxx"
    }
"""

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        _json = request.json
        _name=_json['name']
        _password=_json['password']
        passhash = generate_password_hash(_password)
        user= User(_name,passhash)
        db.session.add(user)
        db.session.commit()
        return f" Register Successfully"
    else:
        return "ERROR"


"""
For Login

Link: http://127.0.0.1:5000/login

Syntax: API TESTING
        {
    "name":"xxxxxxxxxxxx@gmail.com",
    "password":"xxxxxxx"
    }
"""

@app.route('/login', methods=['POST'])
def login():
    if request.method=='POST':
        _json = request.json
        _name = _json['name']
        _password = _json['password']
        # validate the received values
        if _name and _password:
            #check user exists          
            user=User.query.filter_by(email=_name).first()
            if user:
                if check_password_hash(user.password, _password):
                    session['user'] = _name
                    return 'LOGIN Sucessfully'
                else:
                    return 'pass not same'
            else:
                return "user not found"
        else:
            return "NO name and Password"

"""
For Logout

Link: http://127.0.0.1:5000/logout

"""
@app.route('/logout')
def logout():
    session.pop('user')
    return "SUccessfully logout"

"""
For Upload file

Link: http://127.0.0.1:5000/uploadfile

Syntax: API TESTING
        {
            "file": file location
    }
"""
@app.route('/uploadfile',methods=['POST'])
def upload():
    try:
        if session['user']:
            if request.method=="POST":
                file=request.files['file']
                df=pd.read_csv(file)
                list_=df.values.tolist()
                set_data=db.session()
                try:
                    for row in list_:
                        record=Data(**{
                            'Fname': row[0],
                            'Lname':row[1]
                        })
                        set_data.add(record)
                    set_data.commit()
                    return "Upload sucessfully"
                except:
                    set_data.rollback()
                    return "NOT Uploaded"
                finally:
                    set_data.close()
    except:
        return "Session expired"

"""
A search API  to look through all the CSV data uploaded and return results.

Link: http://127.0.0.1:5000/search

Syntax: API TESTING
  {
    "Fname":"XYZ"
}
"""
@app.route('/search',methods=['POST'])
def search():
    try:
        if session['user']:
            if request.method=="POST":
                _json = request.json
                try:
                    _Fname = _json['Fname']
                except:
                    _Lname = _json['Lname']
                
                if _Fname:
                    user=Data.query.filter_by(Fname=_Fname).first()
                    data={
                        "Fname":user.Fname,
                        "Lname": user.Lname
                    }
                    return {"data":data}
                elif _Lname:
                    user=Data.query.filter_by(Lname=_Lname).first()
                    data={
                        "Fname":user.Fname,
                        "Lname": user.Lname
                    }
                    return {"data":data}
                else:
                    return "No Input found"

            else:
                return "Search Not working"

    except:
        return "Session expired"
    
"""
Show a list of data uploaded categorized by fields

Link: http://127.0.0.1:5000/list_of_data

Syntax: API TESTING
  {
}

"""
@app.route('/list_of_data', methods=['GET'])
def list_of_data():
    try:
        if session['user']:
            if request.method=="GET":
                user=Data.query.all()
                result=[]
                for i in user:
                    data={
                        "Fname":i.Fname,
                        "Lname":i.Lname
                    }
                    result.append(data)
                return {"DATA":result}
    except:
        return "Session expired"

"""
Delete files/data that match specific filter values.

Link: http://127.0.0.1:5000/delete

Syntax: API TESTING
      {
    "Fname":"n"
}


"""
@app.route('/delete', methods=['POST'])
def delete():
    try:
        if session['user']:
            if request.method=="POST":
                _json = request.json
                try:
                    _Fname = _json['Fname']
                except:
                    _Lname = _json['Lname']
                if _Fname:
                    stmt = Data.query.filter_by(Fname = _Fname).delete()
                    db.session.add(stmt)
                    db.commit()
                    return "Deleted successfully"
                elif _Lname:
                    stmt = Data.query.filter_by(Fname = _Fname).delete()
                    db.session.add(stmt)
                    db.commit()
                else:
                    return "unexpected input"
    
    except:
        return "Session expired"


if __name__ == "__main__":
    app.run(debug=True)