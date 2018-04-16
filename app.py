import time
import datetime
from flask import Flask, render_template, flash ,redirect, request, url_for, session , logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, DateField,SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from wtforms.fields.html5 import DateField
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField,FileAllowed,FileRequired
from flask_uploads import UploadSet,configure_uploads,IMAGES 
from flask_wtf import RecaptchaField
from wtforms import ValidationError
from authy.api import AuthyApiClient


app = Flask(__name__)

# config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'iiita123'
app.config['MYSQL_DB'] = 'MobileVoting'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeGolAUAAAAANEcOrlm1_SBbAqbUtHEm_-ImdAK'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeGolAUAAAAAOSbI3-pRhY_QuaRZgvUJtEJScJQ'
authy_api = AuthyApiClient('xeBa90E2swVpTZOXwljn2ksUxicPdQM3')

#init MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

photos = UploadSet('photos',IMAGES)
configure_uploads(app,photos)

class Registerform(Form):
    name = StringField('',[validators.Required(), validators.Regexp(regex=r'^[a-zA-Z\s]+$', message="Username must contain only letters numbers or underscore"),validators.Length(min=1,max=30)])
    gender = RadioField(
        'Gender?',
        [validators.DataRequired()],
        choices=[('Male', 'Male'), ('Female', 'Female'),('Other', 'Other')], default='Male'
    )
    dob = DateField('', format='%Y-%m-%d',)
    def validate_dob(self, dob):
        print dob.data
        if dob.data == None:
            flash('Date Of Birth Required!','danger')
            raise ValidationError('Date Of Birth Required!')
        # print (datetime.date.today() - dob.data).days
        if (datetime.date.today() - dob.data).days < 18*365 :
            flash("Under 18",'danger')
            raise ValidationError('Under 18')

    aadhaar_no = StringField('',[validators.Required(),validators.Length(min=12,max=12),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    pincode = StringField('',[validators.Required(),validators.Length(min=6,max=6),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    phone = StringField('',[validators.Required(),validators.Length(min=10,max=11),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    email_id = StringField('',[validators.Optional(),validators.Email()])
    password = PasswordField('',[
        validators.DataRequired(),validators.Regexp(regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])', message="Password must contain atleast one lowercase letter ,one uppercase letter and one number"),
        validators.length(min=6,max=20),validators.EqualTo('confirm', message='passwords do not match')
    ])
    confirm = PasswordField('')
    recaptcha = RecaptchaField()

@app.route('/register',methods=['GET','POST'])
def register():
    if 'logged_in' in session:
        flash('logout to register','danger')
        return redirect(url_for('dashboard'))
    form =Registerform(request.form)
    if  request.method =='POST' and form.validate():
        name = form.name.data
        gender = form.gender.data
        dob = form.dob.data.strftime('%Y-%m-%d')
        aadhaar_no = form.aadhaar_no.data
        pincode = form.pincode.data
        phone = form.phone.data
        email_id =form.email_id.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT AadhaarNumber FROM Voter WHERE AadhaarNumber=%s",[aadhaar_no])
        if result>0 :
            flash('Already a user! Try logging in','danger')
            return redirect(url_for('login'))
        result = cur.execute("SELECT PinCode FROM City WHERE PinCode=%s",[pincode])
        if result == 0:
            flash('Not a Valid Pincode','danger')
            return render_template('register.html',form=form)
        cur.execute("DELETE FROM TempVoter WHERE MobileNumber = %s",[phone])
        mysql.connection.commit()
        cur.execute("INSERT INTO TempVoter(Name, Gender, DateOfBirth, AadhaarNumber, PinCode, MobileNumber, EmailId, Password) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(name, gender, dob, aadhaar_no, pincode, phone, email_id, password))
        mysql.connection.commit()
        cur.close()
        flash('verify otp valid only for 60 seconds', 'success')
        send_otp(phone)
        return redirect(url_for('verify'))
    return render_template('register.html',form=form)

def send_otp(phone):
    requests = authy_api.phones.verification_start(phone, '91', via='sms',locale='en')
    print requests

class OTPform(Form):
    phone = StringField('',[validators.Required(),validators.Length(min=10,max=11),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    otp = StringField((''),[validators.Required()])

@app.route('/verify',methods=['GET','POST'])
def verify():
    if 'logged_in' in session:
        flash('logout to register','danger')
        return redirect(url_for('dashboard'))
    form =OTPform(request.form)
    if  request.method =='POST' and form.validate():
        phone = form.phone.data
        otp = form.otp.data
        check = authy_api.phones.verification_check(phone, '91', otp)
        if check.ok():
            cur =mysql.connection.cursor()
            result = cur.execute("select * from TempVoter WHERE MobileNumber = %s",[phone])
            if result == 0:
                flash('mobile Number not registered','danger')
                return render_template('verify.html',form=form)
            data = cur.fetchone()
            cur.execute("INSERT INTO Voter(Name, Gender, DateOfBirth, AadhaarNumber, PinCode, MobileNumber, EmailId, Password) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(data['Name'],data['Gender'], data['DateOfBirth'], data['AadhaarNumber'], data['PinCode'], data['MobileNumber'], data['Emailid'], data['Password']))
            cur.execute("DELETE FROM TempVoter WHERE MobileNumber = %s",[phone])
            mysql.connection.commit()
            flash("sucessfully registered, can login",'success')
            return redirect(url_for('login'))
        else:
            flash('wrong otp','danger')
    return render_template('verify.html',form=form)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('login'))
    return wrap

class CandidateRegisterform(Form):
    eduqua = StringField('Edu*',[validators.Length(min=1,max=50)])
    password = PasswordField('',[validators.DataRequired()])
    
@app.route('/register_candidate',methods=['GET','POST'])
@is_logged_in
def register_candidate():
    if session['type'] == 'C' :
        flash('Already Registerd as Candidate')
        return redirect(url_for('dashboard'))
    if session['type'] != 'V' :
        flash('Unauthorized, please login', 'danger')
        return redirect(url_for('logout'))
    rows = []
    cur =mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Constituency WHERE StartStopNomination= 1")
    if result == 0 :
        flash('Nominations are not Open for any state','danger')
        return redirect(url_for('dashboard'))
    data = cur.fetchall()
    for state in data :
        rows.append(state['State'])
    form = CandidateRegisterform(request.form)
    if request.method == 'POST' and 'symbol' in request.files  and 'signature' in request.files :
        username = session['username']#form.aadhaar_no.data
        state = request.form.get("states")
        eduqua = form.eduqua.data
        PhotoLink = photos.save(request.files['symbol'])
        SignatureLink = photos.save(request.files['signature'])
        password_candidate = form.password.data
        if state == None:
            flash('Select Contituency','danger')
            return render_template('register_candidate.html',form=form, rows = rows)
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * FROM Candidate WHERE AadhaarNumber=%s",[username])
        if result > 0:
            flash('Already Applied!','danger')
            return redirect(url_for('login'))
        result = cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            if sha256_crypt.verify(password_candidate, password):
                cursor =mysql.connection.cursor()
                cursor.execute("INSERT INTO Candidate(AadhaarNumber,PhotoLink,SignatureLink,EduQua,Constituency) VALUES(%s,%s,%s,%s,%s)",(username,PhotoLink,SignatureLink,eduqua,state))
                mysql.connection.commit()
                cursor.close()
                session['type']='C'
                flash('you are now succesfully applied', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Authentication failed','danger')
                return render_template('register_candidate.html',form=form, rows = rows)
            cur.close()
        else:
            flash('Should be registered as voter','danger')
            return render_template('register_candidate.html',form=form, rows = rows)
    return render_template('register_candidate.html',form=form, rows = rows)

class Loginform(Form):
    aadhaar_no = StringField('',[validators.DataRequired()])
    password = PasswordField('',[validators.DataRequired()])

@app.route('/login',methods=['GET','POST'])
def login():
    if 'logged_in' in session:
        flash('logout to login as different user!!','danger')
        return redirect(url_for('dashboard'))
    form =Loginform(request.form)
    if request.method == 'POST' and form.validate():
        username = form.aadhaar_no.data
        password_candidate = form.password.data
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT Password FROM Voter WHERE AadhaarNumber=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['type']= 'V'
                result = cur.execute("SELECT * FROM Candidate WHERE AadhaarNumber=%s",[username])
                if result>0 :
                    session['type'] = 'C'
                cur.close()
                flash('you are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                cur.close()
                flash('Invalid Credentials','danger')
                return render_template('login.html',form=form)
            cur.close()
        else:
            flash('Username not found','danger')
            return render_template('login.html', form=form)
    return render_template('login.html',form=form)

@app.route('/login_electionofficer',methods=['GET','POST'])
def login_electionofficer():
    if 'logged_in' in session:
        flash('logout to login as different user!!','danger')
        return redirect(url_for('dashboard'))
    form =Loginform(request.form)
    if request.method == 'POST' and form.validate():
        username = form.aadhaar_no.data
        password_candidate = form.password.data
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * FROM ElectionOfficer WHERE UserID=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['type'] = 'E'
                if data['Constituency'] == 'INDIA':
                    session['type'] = 'A'
                flash('you are now logged in', 'success')
                cur.close()
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid login','danger')
                cur.close()
                return redirect(url_for('login_electionofficer'))
        else:
            flash('Username not found','danger')
            cur.close()
            return redirect(url_for('login_electionofficer'))
    return render_template('login_electionofficer.html',form=form)

class ChangePasswordform(Form):
    old_password = PasswordField('',[validators.DataRequired()])
    new_password = PasswordField('',[
        validators.DataRequired(),validators.Regexp(regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])', message="Password must contain atleast one lowercase letter ,one uppercase letter and one number"),
        validators.length(min=6,max=20),validators.EqualTo('confirm', message='passwords do not match')
    ])
    confirm = PasswordField('')

@app.route('/change_password',methods=['GET','POST'])
@is_logged_in
def change_password():
    form = ChangePasswordform(request.form)
    if request.method == 'POST' and form.validate():
        old_password = form.old_password.data
        new_password = sha256_crypt.encrypt(str(form.new_password.data))
        if session['type'] == 'V' or session['type'] == 'C':
            cur =mysql.connection.cursor()
            result = cur.execute("SELECT Password FROM Voter WHERE AadhaarNumber=%s",[session['username']])
            if result>0 :
                data = cur.fetchone()
                password = data['Password']
                if sha256_crypt.verify(old_password, password):
                    cur.execute("UPDATE Voter set Password=%s WHERE AadhaarNumber=%s",[new_password,session['username']])
                    mysql.connection.commit()
                    flash('password succesfully changed', 'success')
                    cur.close()
                    return redirect(url_for('dashboard'))
                else:
                    cur.close()
                    print 2
                    flash('Invalid Credentials','danger')
                    return render_template('change_password.html',form=form)
        elif session['type'] == 'E' or session['type'] == 'A':
            cur =mysql.connection.cursor()
            result = cur.execute("SELECT Password FROM ElectionOfficer WHERE UserID=%s",[session['username']])
            if result>0 :
                data = cur.fetchone()
                password = data['Password']
                if sha256_crypt.verify(old_password, password):
                    cur.execute('UPDATE ElectionOfficer set Password=%s WHERE UserID=%s',[new_password,session['username']])
                    flash('password succesfully changed', 'success')
                    mysql.connection.commit()
                    cur.close()
                    return redirect(url_for('dashboard'))
                else:
                    cur.close()
                    flash('Invalid Credentials','danger')
                    return render_template('change_password.html',form=form)
    return render_template('change_password.html',form=form)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are now logged out','success')
    return redirect(url_for('login'))

@app.route('/withdraw')
@is_logged_in
def withdraw():
    if session['type'] != 'C' :
        flash('Invalid User')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    username = session['username']
    cur.execute('SELECT StartStopNomination from Constituency,Candidate WHERE Constituency.State=Candidate.Constituency AND AadhaarNumber=%s',[username])
    data = cur.fetchone()
    startstopnomination = data['StartStopNomination']
    if startstopnomination == 0:
        cur.close()
        return redirect(url_for('dashboard'))    
    cur.execute("DELETE FROM Candidate WHERE AadhaarNumber = %s",[username])
    mysql.connection.commit()
    cur.close()
    session['type'] = 'V'
    flash('you have succesfully withdrawn','success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    session_type = session['type']
    if session_type =='E' :
        return redirect(url_for('dashboard_electionofficer'))
    if session_type =='C' :
        return redirect(url_for('dashboard_candidate'))
    if session_type =='V' :
        return redirect(url_for('dashboard_voter'))
    if session_type =='A' :
        return redirect(url_for('admin'))
    return redirect(url_for('logout'))
    
@app.route('/dashboard_voter')
@is_logged_in
def dashboard_voter():
    if session['type'] != 'V':
        return redirect(url_for('dashboard'))
    username = session['username']
    cur = mysql.connection.cursor()   
    result= cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
    if result == 0 :
        flash('not valid user')
        return redirect(url_for('logout'))
    user_details = cur.fetchone()
    pincode =  user_details['PinCode']
    cur.execute("SELECT * FROM City WHERE PinCode=%s",[pincode])
    city_details = cur.fetchone()
    print city_details
    cur.close()
    return render_template('dashboard.html', user_details=user_details,city_details=city_details )

@app.route('/dashboard_candidate')
@is_logged_in
def dashboard_candidate():
    if session['type'] != 'C':
        return redirect(url_for('dashboard'))
    username = session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
    user_details = cur.fetchone()
    pincode =  user_details['PinCode']
    cur.execute("SELECT * FROM City WHERE PinCode=%s",[pincode])
    city_details = cur.fetchone()
    cur.close()
    return render_template('dashboard_candidate.html', user_details=user_details,city_details=city_details )

@app.route('/dashboard_electionofficer')
@is_logged_in
def dashboard_electionofficer():
    if session['type'] != 'E':
        return redirect(url_for('dashboard'))
    username = session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT Constituency FROM ElectionOfficer WHERE UserID=%s",[username])
    constituency = cur.fetchone()
    cur.execute("SELECT * FROM Constituency WHERE State=%s",[constituency['Constituency']])
    constituency_details = cur.fetchone()
    cur.execute('SELECT COUNT(AadhaarNumber),SUM(VotingStatus) from Voter NATURAL JOIN (SELECT PinCode from City Where State =%s) AS T',[constituency['Constituency']])
    voter_stats=cur.fetchone()
    cur.execute('SELECT COUNT(AadhaarNumber),SUM(Validate) from Candidate Where Constituency =%s',[constituency['Constituency']])
    candidate_stats=cur.fetchone()
    cur.close()
    return render_template('dashboard_electionofficer.html', constituency_details=constituency_details,voter_stats=voter_stats,candidate_stats=candidate_stats)

@app.route('/admin')
@is_logged_in
def admin():
    if session['type']!='A':
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM ElectionOfficer WHERE Constituency != %s',['INDIA'])
    if result == 0:
        msg = 'No officer'
        cur.close()
        return render_template('admin.html',msg=msg)
    officers = cur.fetchall()
    cur.close()
    return render_template('admin.html',officers=officers)

@app.route('/vote_cast', methods=['GET', 'POST'])
@is_logged_in
def vote_cast():
    if session['type'] != 'V' and session['type'] != 'C' :
        return redirect(url_for('dashboard'))
    username = session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT VotingStatus,PinCode FROM Voter WHERE AadhaarNumber=%s", [username])
    user_details = cur.fetchone()
    if user_details['VotingStatus'] == 1 :
        flash('Already Casted Vote', 'danger')
        return redirect(url_for('dashboard'))
    pincode =  user_details['PinCode']
    cur.execute("SELECT State FROM City WHERE PinCode=%s",[pincode])
    city_details = cur.fetchone()
    constituency = city_details['State']
    cur.execute('SELECT * from Candidate NATURAL JOIN Voter where Constituency=%s AND Validate = 1',[constituency])
    candidates = cur.fetchall()
    return render_template('vote_cast.html',candidates=candidates )

class Passwordform(Form):
    password = PasswordField('Password',[validators.DataRequired()])

@app.route('/vote_candidate/<string:AadhaarNumber>', methods=['GET','POST'])
@is_logged_in
def vote_candidate(AadhaarNumber):
    if session['type'] != 'V' and session['type'] != 'C' :
        return redirect(url_for('dashboard'))
    username = session['username']
    cur = mysql.connection.cursor()
    result=cur.execute("SELECT VotingStatus FROM Voter WHERE AadhaarNumber=%s", [username])
    if result == 0:
        flash('candidate does not exist','danger')
        return redirect(url_for('dashboard'))
    user_details = cur.fetchone()
    if user_details['VotingStatus'] == 1 :
        flash('Already Casted Vote', 'danger')
        return redirect(url_for('dashboard'))
    cur.execute("SELECT * from Candidate WHERE AadhaarNumber= %s",[AadhaarNumber])
    candidate = cur.fetchone()
    form = Passwordform(request.form)
    username = session['username']
    if request.method == 'POST' and form.validate():
        password_voter = form.password.data
        result = cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            if sha256_crypt.verify(password_voter, password):
                candidate_votes = candidate['NumberOfVotes'] + 1
                candidate_aadhaar = candidate['AadhaarNumber']
                cur.execute("UPDATE Candidate SET NumberOfVotes = %s WHERE AadhaarNumber = %s",(candidate_votes,candidate_aadhaar))
                mysql.connection.commit()
                cur.execute("UPDATE Voter SET VotingStatus = %s WHERE AadhaarNumber = %s",(1,username))
                mysql.connection.commit()
                flash('Voting Succeful', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Credentials')
                return render_template('vote_candidate.html',form=form,candidate=candidate)
            cur.close()
    return render_template('vote_candidate.html',form=form,candidate=candidate)

class ElectionOfficerRegisterform(Form):
    userid = StringField('',[validators.Length(min=1,max=50)])
    password =  PasswordField('',[validators.Length(min=1,max=50)])

@app.route('/add_electionofficer',methods=['GET','POST'])
@is_logged_in
def add_electionofficer():
    if session['type'] != 'A' :
        flash('Only ADMIN can ADD','danger')
        return redirect(url_for('dashboard'))
    rows = []
    cur =mysql.connection.cursor()
    result = cur.execute("SELECT State FROM Constituency")
    data = cur.fetchall()
    for state in data :
        rows.append(state['State'])
    form = ElectionOfficerRegisterform(request.form)
    if  request.method =='POST' and form.validate():
        userid = form.userid.data
        password = sha256_crypt.encrypt(str(form.password.data))
        constituency = request.form.get("states")
        cur =mysql.connection.cursor()
        if constituency == None:
            flash('Select Contituency','danger')
            return render_template('add_electionofficer.html',form=form, rows = rows)
        result = cur.execute("SELECT UserID FROM ElectionOfficer WHERE UserID=%s",[userid])
        if result>0 :
            flash('Already a user exists!','danger')
            return render_template('add_electionofficer.html',form=form, rows = rows)
        cur.execute("INSERT INTO ElectionOfficer(UserID, Constituency, Password) VALUES(%s, %s, %s)",(userid, constituency, password))
        mysql.connection.commit()
        cur.close()
        flash('Succesfully Added!!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_electionofficer.html',form=form, rows = rows)

@app.route('/remove_electionofficer/<string:UserID>',methods=['POST'])
@is_logged_in
def remove_electionofficer(UserID):
    if session['type'] != 'A':
        flash('ONLY ADMIN CAN REMOVE','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ElectionOfficer WHERE UserID=%s',[UserID])
    mysql.connection.commit()
    cur.close()
    flash('Succesfully Removed!!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/StartStop_elections', methods=['POST'])
@is_logged_in
def StartStop_elections():
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ElectionOfficer WHERE UserID = %s ",[session['username']])
    data = cur.fetchone()
    constituency = data['Constituency']
    cur.execute("SELECT StartStopElection FROM Constituency WHERE State = %s ",[constituency])
    data =cur.fetchone()
    print data
    status = 1 - data['StartStopElection']
    cur.execute("UPDATE Constituency SET  StartStopElection = %s WHERE State = %s ",[status,constituency])
    mysql.connection.commit()
    cur.close()
    flash('Sucess', 'success')
    return redirect(url_for('dashboard'))

@app.route('/StartStop_nominations', methods=['POST'])
@is_logged_in
def StartStop_nominations():
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Constituency FROM ElectionOfficer WHERE UserID = %s ",[session['username']])
    data = cur.fetchone()
    constituency = data['Constituency']
    cur.execute("SELECT StartStopNomination FROM Constituency WHERE State = %s ",[constituency])
    data =cur.fetchone()
    status = 1 - data['StartStopNomination']
    cur.execute("UPDATE Constituency SET  StartStopNomination = %s WHERE State = %s ",[status,constituency])
    mysql.connection.commit()
    cur.close()
    flash('Sucess', 'success')
    return redirect(url_for('dashboard'))

@app.route('/ShowHide_results', methods=['POST'])
@is_logged_in
def ShowHide_results():
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Constituency FROM ElectionOfficer WHERE UserID = %s ",[session['username']])
    data = cur.fetchone()
    constituency = data['Constituency']
    cur.execute("SELECT ShowHideResults FROM Constituency WHERE State = %s ",[constituency])
    data =cur.fetchone()
    status = 1 - data['ShowHideResults']
    cur.execute("UPDATE Constituency SET ShowHideResults = %s WHERE State = %s ",[status,constituency])
    mysql.connection.commit()
    cur.close()
    flash('Sucess', 'success')
    return redirect(url_for('dashboard'))

@app.route('/validate_candidates', methods=['GET','POST'])
@is_logged_in
def validate_candidates():
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Constituency FROM ElectionOfficer WHERE UserID = %s ",[session['username']])
    data = cur.fetchone()
    constituency = data['Constituency']
    cur.execute("SELECT AadhaarNumber, Validate FROM Candidate WHERE Constituency = %s ",[constituency])
    candidates =cur.fetchall()
    cur.close()
    return render_template('validate_candidates.html',candidates = candidates)

@app.route('/clear_candidates', methods=['GET','POST'])
@is_logged_in
def clear_candidates():
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    form = Passwordform(request.form)
    username = session['username']
    if request.method == 'POST' and form.validate():
        password_typed = form.password.data
        result = cur.execute("SELECT Password,Constituency FROM ElectionOfficer WHERE UserID=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            constituency = data['Constituency']
            if sha256_crypt.verify(password_typed, password):
                cur.execute("DELETE FROM Candidate WHERE Constituency = %s ",[constituency])
                mysql.connection.commit()
                cur.close()
                flash('sucessful','sucess')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Credentials')
                cur.close()
                return render_template('clear_candidates.html',form=form)
    cur.close()
    return render_template('clear_candidates.html',form=form)

@app.route('/reset_votes', methods=['GET','POST'])
@is_logged_in
def reset_votes():
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    form = Passwordform(request.form)
    username = session['username']
    if request.method == 'POST' and form.validate():
        password_typed = form.password.data
        result = cur.execute("SELECT Password,Constituency FROM ElectionOfficer WHERE UserID=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            constituency = data['Constituency']
            if sha256_crypt.verify(password_typed, password):
                cur.execute("UPDATE Candidate set NumberOfVotes = 0 WHERE Constituency = %s ",[constituency])
                cur.execute("UPDATE Voter natural join City set VotingStatus  = 0 WHERE State = %s ",[constituency])
                mysql.connection.commit()
                cur.close()
                flash('sucessful','sucess')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Credentials')
                cur.close()
                return render_template('ResetVotes.html',form=form)
    cur.close()
    return render_template('ResetVotes.html',form=form)

@app.route('/validate_candidate/<string:AadhaarNumber>', methods=['GET','POST'])
@is_logged_in
def validate_candidate(AadhaarNumber):
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Constituency FROM ElectionOfficer WHERE UserID = %s ",[session['username']])
    data = cur.fetchone()
    constituency = data['Constituency']
    result = cur.execute("SELECT * from Candidate WHERE AadhaarNumber= %s",[AadhaarNumber])
    if result == 0:
        flash('Does not exsist','danger')
        cur.close()
        return redirect(url_for('dashboard'))
    candidate_details = cur.fetchone()
    if constituency != candidate_details['Constituency'] :
        flash('Not of your Constituency','danger')
        cur.close()
        return redirect(url_for('dashboard'))
    cur.execute("SELECT * from Voter WHERE AadhaarNumber= %s",[AadhaarNumber])
    voter_details = cur.fetchone()
    cur.close()
    return render_template('/validate_candidate.html', voter_details=voter_details,candidate_details=candidate_details)

@app.route('/validate/<string:AadhaarNumber>', methods=['GET','POST'])
@is_logged_in
def validate(AadhaarNumber):
    if session['type'] != 'E':
        flash('ONLY ELECTIONOFFICER ALLOWED','danger')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT Constituency FROM ElectionOfficer WHERE UserID = %s ",[session['username']])
    data = cur.fetchone()
    constituency = data['Constituency']
    result = cur.execute("SELECT Constituency from Candidate WHERE AadhaarNumber= %s",[AadhaarNumber])
    if result == 0:
        flash('Does not exsist','danger')
        cur.close()
        return redirect(url_for('dashboard'))
    candidate_details = cur.fetchone()
    if constituency != candidate_details['Constituency'] :
        flash('Not of your Constituency','danger')
        cur.close()
        return redirect(url_for('dashboard'))
    cur.execute("SELECT Validate FROM Candidate WHERE AadhaarNumber = %s ",[AadhaarNumber])
    data = cur.fetchone()
    status = 1 - data['Validate']
    cur.execute("UPDATE Candidate set Validate = %s WHERE AadhaarNumber = %s ",[status,AadhaarNumber])
    mysql.connection.commit()
    cur.close()
    flash('Validated', 'success')
    return redirect(url_for('validate_candidates'))

@app.route('/results')
def results():
    cur = mysql.connection.cursor()
    cur.execute('SELECT State FROM Constituency WHERE ShowHideResults = 1')
    constituencies = cur.fetchall()
    print constituencies
    return render_template('results.html',constituencies=constituencies)

@app.route('/result/<string:Constituency>', methods=['GET','POST'])
def result(Constituency):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT ShowHideResults FROM Constituency WHERE State = %s ",[Constituency])
    if result == 0:
        flash('constituency does not exist','danger')
        return redirect(url_for('/'))
    data = cur.fetchone()
    showhide = data['ShowHideResults']
    if showhide == 0:
        cur.close()
        flash('results are not open for this constituency')
        return redirect(url_for('results'))
    result = cur.execute('SELECT * from Candidate NATURAL JOIN Voter where Constituency=%s AND Validate = 1 ORDER BY NumberOfVotes DESC',[Constituency])
    if result == 0:
        flash('No one participated','danger')
        cur.close()
        return redirect(url_for('results'))
    candidates = cur.fetchall()
    cur.close()
    return render_template('result.html',candidates=candidates)

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
    # app.run(host='0.0.0.0')

