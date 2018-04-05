from flask import Flask, render_template, flash ,redirect, request, url_for, session , logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, DateField,SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from wtforms.fields.html5 import DateField
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField,FileAllowed,FileRequired
from flask_uploads import UploadSet,configure_uploads,IMAGES 
from flask_recaptcha import ReCaptcha
from flask_wtf import RecaptchaField
from wtforms import ValidationError

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


#init MYSQL
mysql = MySQL(app)

rows = []


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
    # def validate_dob(form, field):
    #     cur = datetime.year()
    #     age = cur - field.data
    #     age =age/365
    #     if age < 18:
    #         raise ValidationError('Invalid Age.')
        
    aadhaar_no = StringField('',[validators.Required(),validators.Length(min=12,max=12),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    # city = StringField('',[validators.Length(min=1,max=30)])
    pincode = StringField('',[validators.Required(),validators.Length(min=6,max=6),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    # state = SelectField(label='state', 
        # choices=[(state, state) for state in rows])
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
    form =Registerform(request.form)
    if  request.method =='POST' and form.validate():
        name = form.name.data
        gender = form.gender.data
        # dob = form.dob.data
        dob = form.dob.data.strftime('%Y-%m-%d')
        aadhaar_no = form.aadhaar_no.data
        # father_name = form.father_name.data
        # address = form.address.data
        # city = form.city.data
        pincode = form.pincode.data
        # state = form.state.data
        phone = form.phone.data
        email_id =form.email_id.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur =mysql.connection.cursor()

        result = cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[aadhaar_no])
        if result>0 :
            flash('Already a user! Try logging in','danger')
            return redirect(url_for('login'))
        result = cur.execute("SELECT * FROM City WHERE PinCode=%s",[pincode])
        if result == 0:
            flash('Not a Valid Pincode','danger')
            return render_template('register.html',form=form)
        cur.execute("INSERT INTO Voter(Name, Gender, DateOfBirth, AadhaarNumber, PinCode, MobileNumber, EmailId, Password) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(name, gender, dob, aadhaar_no, pincode, phone, email_id, password))
        mysql.connection.commit()
        cur.close()
        flash('you are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)


# check if user logged in
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
    aadhaar_no = StringField('',[validators.Required(),validators.Length(min=12,max=12),validators.Regexp(regex=r'^[0-9]*$', message="Only Numbers are allowed")])
    state = state = SelectField(label='state', 
        choices=[(state, state) for state in rows])
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
    del rows[:]
    print rows
    cur =mysql.connection.cursor()
    result = cur.execute("SELECT * FROM Constituency WHERE StartStopNomination= 0")
    if result == 0 :
        flash('Nominations are not Open for any state','danger')
        return redirect(url_for('dashboard'))
    
    data = cur.fetchall()

    for state in data :
        print state['State']
        rows.append(state['State'])
    # print rows
    form = CandidateRegisterform(request.form)
    if request.method == 'POST' and 'symbol' in request.files  and 'signature' in request.files :
        username = form.aadhaar_no.data
        state = form.state.data
        eduqua = form.eduqua.data
        PhotoLink = photos.save(request.files['symbol'])
        SignatureLink = photos.save(request.files['signature'])
        
        password_candidate = form.password.data
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * FROM Candidate WHERE AadhaarNumber=%s",[username])
        if result > 0:
            flash('Already a user! Try logging in','danger')
            return redirect(url_for('login'))
        result = cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
        #result = cur.execute("SELECT * FROM Voter")
        if result>0 :
            #get hash
            data = cur.fetchone()
            password = data['Password']
            #campare passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                # session['logged_in'] = True
                # session['username'] = username
                cursor =mysql.connection.cursor()
                cursor.execute("SELECT * FROM Constituency WHERE State=%s",[state])
                data = cursor.fetchone()
                result = data['Id']
                cursor.execute("INSERT INTO Candidate(AadhaarNumber,PhotoLink,SignatureLink,EduQua,ConstituencyId) VALUES(%s,%s,%s,%s,%s)",(username,PhotoLink,SignatureLink,eduqua,result))
	            #Commit to DB
                mysql.connection.commit()
    
                cursor.close()
                flash('you are now succesfully applied as candidate and can login', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid Credentials','danger')
                return render_template('register_candidate.html',form=form)
            # cur close
            cur.close()
        else:
            flash('Should be registered as voter','danger')
            return render_template('register_candidate.html',form=form)

    return render_template('register_candidate.html',form=form)


@app.route('/edit_voter',methods=['GET','POST'])
def edit_voter() :
    session_type =session['type']
    print session_type
    if session_type != 'C' and session_type != 'V' :
        flash('Not a valid User,Try to login in')
        return redirect(url_for('logout'))
    form = Registerform(request.form)
    username = session['username']
    cur = mysql.connection.cursor()
    result = cur.execute('SELECT * FROM Voter WHERE AadhaarNumber = %s',[username])
    if result <= 0:
        print result
        flash('Not a valid User,Try to login in')
        return redirect(url_for('logout'))
    data = cur.fetchone()
    form.name.data = data['Name']
    form.gender.data = data['Gender']
    form.dob.data = data['DateOfBirth']
    form.aadhaar_no.data = data['AadhaarNumber']
    form.pincode.data = data['PinCode']
    form.phone.data = data['MobileNumber']
    form.email_id.data = data['EmailId']
    return render_template('edit_voter.html',form=form)


class Loginform(Form):
    aadhaar_no = StringField('',[validators.Length(min=12,max=16)])
    password = PasswordField('',[validators.DataRequired()])

#user login
@app.route('/login',methods=['GET','POST'])
def login():
    form =Loginform(request.form)
    if request.method == 'POST' and form.validate():
        username = form.aadhaar_no.data
        password_candidate = form.password.data

        #craete cursor

        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * FROM Candidate WHERE AadhaarNumber=%s",[username])
        if result>0 :
            cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
            data = cur.fetchone()
            password = data['Password']

            #campare passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session['logged_in'] = True
                session['username'] = username
                session['type']= 'C'
                flash('you are now logged in', 'success')
                return redirect(url_for('dashboard_candidate'))
        #get user by username
        result = cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
        if result>0 :
            #get hash
            data = cur.fetchone()
            password = data['Password']

            #campare passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session['logged_in'] = True
                session['username'] = username
                session['type']= 'V'
                flash('you are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid login','danger')
                return render_template('login.html')
            # cur close
            cur.close()
        else:
            flash('Username not found','danger')
            return render_template('login.html', form=form)

    return render_template('login.html',form=form)

@app.route('/login_electionofficer',methods=['GET','POST'])
def login_electionofficer():
    form =Loginform(request.form)
    if request.method == 'POST' and form.validate():
        username = form.aadhaar_no.data
        password_candidate = form.password.data
        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * FROM ElectionOfficer WHERE AadhaarNumber=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['type'] = 'E'
                flash('you are now logged in', 'success')
                return redirect(url_for('dashboard_electionofficer'))
            else:
                flash('Invalid login','danger')
                return redirect(url_for('/login_electionofficer'))
            # cur close
            cur.close()
        else:
            flash('Username not found','danger')
            return redirect(url_for('/login_electionofficer'))

    return render_template('login_electionofficer.html',form=form)


#logout
@app.route('/logout')
@is_logged_in
def logout():
    # print rows
    session.clear()
    flash('you are now logged out','success')
    return redirect(url_for('login'))

@app.route('/withdraw')
@is_logged_in
def withdraw():
    if session['type'] != 'C' :
        flash('Invalid User')
        return redirect(url_for('logout'))
    cur = mysql.connection.cursor()
    username = session['username']
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
    return redirect(url_for('dashboard_voter'))
    
@app.route('/dashboard_voter')
@is_logged_in
def dashboard_voter():
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
    cur.close()
    return render_template('dashboard.html', user_details=user_details,city_details=city_details )


@app.route('/dashboard_candidate')
@is_logged_in
def dashboard_candidate():
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
    session_type = session['type']
    if session_type != 'E' :
         flash('Not a valid User')
         return redirect(url_for('logout'))
    username = session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Voter WHERE ElectionOfficer=%s",[username])
    user_details = cur.fetchone()
    pincode =  user_details['PinCode']
    cur.execute("SELECT * FROM City WHERE PinCode=%s",[pincode])
    city_details = cur.fetchone()
    cur.close()
    return render_template('dashboard_candidate.html', user_details=user_details,city_details=city_details )


@app.route('/vote_cast',methods=['GET','POST'])
@is_logged_in
def vote_cast():
    username = session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
    user_details = cur.fetchone()
    if user_details['VotingStatus'] == 1 :
        flash('Already Casted Vote','danger')
        return redirect(url_for('dashboard'))
    pincode =  user_details['PinCode']
    cur.execute("SELECT * FROM City WHERE PinCode=%s",[pincode])
    city_details = cur.fetchone()
    constituency = city_details['State']
    cur.execute('SELECT * from Candidate where State=%s',[constituency])
    candidates = cur.fetchall()
    print candidates
    return render_template('vote_cast.html',candidates=candidates )


class Votingform(Form):
    password = PasswordField('Password',[validators.DataRequired()])


@app.route('/vote_candidate/<string:AadhaarNumber>', methods=['GET','POST'])
@is_logged_in
def vote_candidate(AadhaarNumber):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from Candidate WHERE AadhaarNumber= %s",[AadhaarNumber])
    candidate = cur.fetchone()
    print candidate
    print AadhaarNumber
    form = Votingform(request.form)
    username = session['username']
    if request.method == 'POST' and form.validate():
        password_voter = form.password.data
        result = cur.execute("SELECT * FROM Voter WHERE AadhaarNumber=%s",[username])
        if result>0 :
            data = cur.fetchone()
            password = data['Password']
            if sha256_crypt.verify(password_voter, password):
                #session['logged_in'] = True
                #session['username'] = username
                candidate_votes = candidate['NumberOfVotes'] + 1
                candidate_aadhaar = candidate['AadhaarNumber']
                print 3
                cur.execute("UPDATE Candidate SET NumberOfVotes = %s WHERE AadhaarNumber = %s",(candidate_votes,candidate_aadhaar))
                mysql.connection.commit()
                cur.execute("UPDATE Voter SET VotingStatus = %s WHERE AadhaarNumber = %s",(1,username))
                mysql.connection.commit()
                flash('Voting Succeful', 'success')
                return redirect(url_for('dashboard'))
            else:
                print 4
                flash('Invalid login')
                return redirect(url_for('logout'))
            cur.close()
        else:
            print 5
            flash('Username not found')
            return redirect(url_for('logout'))

    return render_template('vote_candidate.html',form=form)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)

