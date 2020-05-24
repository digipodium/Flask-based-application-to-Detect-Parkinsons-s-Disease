from flask import render_template,redirect,request,flash,session,url_for
from flask_login import logout_user,current_user, login_user, login_required
from app import app,db
from app.models import User
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app.predict_parkinsons import predict
import shutil as sh

app.secret_key = "yoyoyo"

print(os.path.exists('app/static/data'))

if os.path.exists('app/static/data'):
   sh.rmtree('app/static/data')

UPLOAD_FOLDER = 'app/static/data'

if not os.path.exists(UPLOAD_FOLDER):
   os.mkdir(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/',methods=['GET','POST'])

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Invalid username or password','danger')
                return redirect(url_for('login'))
            login_user(user, remember=True)
            return redirect(url_for('uploaddata'))
    return render_template('login.html', title='Sign In')


@app.route('/upload',methods=['GET','POST'])  #it is decorator
@login_required
def uploaddata():
   print("hello")
   print(request.method)
   if request.method == 'POST' and request.form['action']=='num':
      pnumber=int(request.form.get('pnum'))
      session['pnumber']=pnumber
      return render_template('dataUpload.html',pat=pnumber)
   elif request.method == 'POST'and request.form['action']=='data':
      print("yeah")
      print("Button press=",request.form['action'])

      if os.path.exists('static/data'):
         sh.rmtree('static/data')
      if not os.path.exists(UPLOAD_FOLDER):
         os.mkdir(UPLOAD_FOLDER)

      print(os.path.realpath(__file__))
      # pnumber=int(request.form.get('pnum'))
      pnumber=session.get('pnumber')
      print(pnumber)
      name,age,spi,wav=[],[],[],[]
      for i in range(1,(pnumber+1)):
         name.append(request.form.get(('pname'+str(i))))
         age.append(request.form.get(('page'+str(i))))
         if ('sfile'+str(i)) in request.files and request.files[('sfile'+str(i))].filename!='':
            spi.append(request.files[('sfile'+str(i))])
         else:
            spi.append('')
         if ('wfile'+str(i)) in request.files and request.files[('wfile'+str(i))].filename!='':
            wav.append(request.files[('wfile'+str(i))])
         else:
            wav.append('')
      print(name,age,spi,wav)

      for i,j,k,l,m in zip(name,age,spi,wav,list(range(1,(pnumber+1)))):
         if i=='':
            flash(f'Enter a proper name for Patient {m}')
            return render_template('dataUpload.html',pat=pnumber)
         if j=='':
            flash(f'Enter a proper age for Patient {m}')
            return render_template('dataUpload.html',pat=pnumber)
         if k=='':
            flash(f'No spiral image in Patient {m}')
            return render_template('dataUpload.html',pat=pnumber)
         if l=='':
            flash(f'No wave image in Patient {m}')
            return render_template('dataUpload.html',pat=pnumber)

      for i,j,k,l,m in zip(name,age,spi,wav,list(range(1,(pnumber+1)))):
         des=os.path.join(app.config['UPLOAD_FOLDER'],f'{m}_{i}_{j}')
         if not (os.path.exists(des)):
            os.mkdir(des)
         k.save(os.path.join(des,"Spiral."+secure_filename(k.filename).split(".")[1]))
         l.save(os.path.join(des,"Wave."+secure_filename(l.filename).split(".")[1]))
      flash("Upload Successful")
      return render_template("dataUpload.html",flag=1)
   print("hello2")
   return render_template("dataUpload.html")

@app.route('/predict', methods=['GET', 'POST'])
def datapredict():
   for root,dir,fname in os.walk(app.config['UPLOAD_FOLDER']):
      print('root=',root)
      print('dir=',dir)
      print('file=',fname)
      break

   pspath,pwpath=[],[]

   for i in dir:
      dirpath=os.path.join(app.config['UPLOAD_FOLDER'],i)
      for root,dire,fname in os.walk(dirpath):
         for j in fname:
            if "spiral" in j.lower():
               spiralpath=os.path.join(dirpath,j)
            else:
               wavepath=os.path.join(dirpath,j)
         print("spiralpath=",spiralpath)
         print("wavepath=",wavepath)
         spath,wpath=predict(spiralpath,wavepath)
         pspath.append('/'+spath.replace('\\','/'))
         pwpath.append('/'+wpath.replace('\\','/'))

   name,age,index=[],[],[]

   for dname in dir:
      data=dname.split("_")
      index.append(data[0])
      name.append(data[1])
      age.append(data[2])

   p=len(dir)

   print(index,name,age,pspath,pwpath)
   return render_template('diseasePred.html',pat=p,d=dir,n=name,a=age,ind=index,s=pspath,w=pwpath)


    
@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        email = request.form.get('email')
        username = request.form.get('username')
        cpassword = request.form.get('cpassword')
        password = request.form.get('password')
        print(cpassword, password, cpassword==password)
        if username and password and cpassword and email:
            if cpassword != password:
                flash('Password do not match','danger')
                return redirect('/register')
            else:
                if User.query.filter_by(email=email).first() is not None:
                    flash('Please use a different email address','danger')
                    return redirect('/register')
                elif User.query.filter_by(username=username).first() is not None:
                    flash('Please use a different username','danger')
                    return redirect('/register')
                else:
                    user = User(username=username, email=email)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    flash('Congratulations, you are now a registered user!','success')
                    return redirect(url_for('login'))
        else:
            flash('Fill all the fields','danger')
            return redirect('/register')

    return render_template('register.html', title='Sign Up page')


@app.route('/forgot',methods=['GET', 'POST'])
def forgot():
    if request.method=='POST':
        email = request.form.get('email')
        if email:
            pass
    return render_template('forgot.html', title='Password reset page')
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('uploaddata'))

@login_required
@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user, title=f'{user.username} profile')


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method=='POST':
        current_user.username = request.form.get('username')
        current_user.about_me = request.form.get('aboutme')
        db.session.commit()
        flash('Your changes have been saved.','success')
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', title='Edit Profile',user=user)
