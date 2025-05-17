import email
from gevent import monkey
monkey.patch_all()
from flask_socketio import SocketIO
from email import message
import os
from email.policy import default
import mimetypes
from re import sub
from unittest import result
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
#from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import User, Message, user_friend
from helpers import login_required, user_image
from image import createImage
from flask import Flask, send_file
from datetime import timedelta
import datetime
from models import db

from Functions import Decrypt, Encryptor, HashToId, makeKeyFilesAlice, Encrypt, ReadKey, WriteToFiles, get_random_bytes, shutil
import time

UPLOAD_FOLDER = 'static/images/users'
UPLOAD_FOLDER_TEMP = 'temp/'
ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg','txt','mp4','mp3'])

app = Flask("__name__")
# socketio for server to client event
app.config['SECRET_KEY'] = 'itsyoursecret!'
socketio = SocketIO(app)

# Profile Images Upload Folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_TEMP'] = UPLOAD_FOLDER_TEMP

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'

# Custom filter
app.jinja_env.filters["user_image"] = user_image

# Requires that "Less secure app access" be on

app.config["MAIL_DEFAULT_SENDER"] = "os.environ['MAIL_DEFAULT_SENDER']"
app.config["MAIL_PASSWORD"] = "os.environ['MAIL_PASSWORD']"
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "os.environ['MAIL_USERNAME']"



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db.init_app(app) # add line after all app config.

@app.before_first_request
def cleanup_temp_directory():
    temp_directory = 'temp/'
    if os.path.exists(temp_directory):
        current_time = datetime.datetime.now()
        print(current_time)
        for filename in os.listdir(temp_directory):
            file_path = os.path.join(temp_directory, filename)
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            # Kiểm tra nếu file đã tồn tại hơn 7 ngày
            if (current_time - creation_time).days > 7:
                os.remove(file_path)
                print(f"Đã xóa file {filename} trong thư mục temp.")
    # Xoá các tin nhắn đã quá 7 ngày trong DB
    seven_days_ago = datetime.datetime.now() - timedelta(days=7)
    
    # Lấy tất cả các tin nhắn có thời gian tạo lớn hơn 7 ngày
    old_messages = Message.query.filter(Message.date < seven_days_ago).all()
    
    # Xóa các tin nhắn đã lỗi thời
    for message in old_messages:
        db.session.delete(message)
    db.session.commit()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#db = SQLAlchemy(app)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id 
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        error = None
        # Ensure username was submitted
        if not request.form.get("email"):
            error = "Please provide your email!"
            flash(error)
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Please provide your password!"
            flash(error)
            return render_template("login.html")

        # Query database for username
        user = User.query.filter_by(email = request.form.get("email")).first()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user.password, request.form.get("password")):
            error = "Invalid username and/or password!"
            flash(error)
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = user.id
  
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/download')
def download_file():
    file_path = './temp/key.txt'  # Đường dẫn đến file .txt bạn muốn tải xuống
    try:
        return send_file(file_path, as_attachment=True)
    finally:
        os.remove(file_path)  # Xóa file sau khi gửi xuống người dùng


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        name = request.form.get("name").strip()
        email = request.form.get("email")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")

        if not name:
            flash("Please provide your name")
            return render_template("register.html")

        if not email:
            flash("Please provide your email")
            return render_template("register.html")

        if not password:
            flash("Please set a password")
            return render_template("register.html")

        if not cpassword:
            flash("Please confirm your password")
            return render_template("register.html")

        if password != cpassword:
            flash("Your password does not match")
            return render_template("register.html")

        #check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already exist!" )
            return render_template("register.html")

        image = createImage(name)

        # create publicKey, privateKey and add into file + database
        publicKey, privateKey = makeKeyFilesAlice('./temp/key.txt', 256)
        str_publicKeyN = str(publicKey[0])
        str_publicKeyE = str(publicKey[1])

        # create user   
        user = User(name=name, email=email, image=image, password=generate_password_hash(password), publicKeyN=str_publicKeyN, publicKeyE=str_publicKeyE)
        db.session.add(user)
        db.session.commit()

        

        # redirect to login and show message
        error = f"Awesome, you have been registered!\n"
        return render_template("login.html", error=error)
    else:
        return render_template("register.html")


@app.route('/', methods = ['GET'])
@login_required
def index():
    id = session['user_id']
    user = User.query.filter_by(id=id).first()
    session_friend = session.get('friend_id', id)
    friend = User.query.filter_by(id=session_friend).first()
    
    if user is None:
        return redirect("/login")

    messages = Message.query.filter(Message.user_id.like(user.id), Message.friend_id.like(id), Message.friend_id.like(friend.id)).all()

    subq = db.session.query(user_friend).filter(user_friend.c.friend_id == id).subquery()
    thefriends = User.query.join(subq, User.id == subq.c.user_id).all()
    ourfriends = []
    for afriend in user.friends:
        ourfriends.append(afriend.id)
    for ufriend in thefriends:
        ourfriends.append(ufriend.id)
    allfriends = User.query.filter(User.id.in_(ourfriends))
    page = request.args.get('page', 1, type=int)
    get_potential_friends = User.query.filter(~User.id.in_(ourfriends))
    records = get_potential_friends.paginate(page=page, per_page=20)
    if "hx_request" in request.headers:
        return render_template("record.html", datas = records)
    return render_template('index.html', **locals())

@app.route("/add-friend")
def addFriend():
    page = request.args.get('page', 1, type=int)
    add_users = User.query.paginate(page=page, per_page=50)
    return render_template("record.html", datas = add_users)

def sendNewFriendMessage(user_id, friend_id):
    query = Message(user_id=user_id, friend_id=friend_id, send_id=friend_id)
    db.session.add(query)
    db.session.commit()

@app.route('/new-friend', methods=['POST'])
def newFriend():
    if session.get("user_id") is None:
        return redirect("/login")

    id = session['user_id']
    friend_id = request.form.get("friend_id")

    if not friend_id:
        return "Error: User not found!"

    """myfriends = db.session.query(User).filter_by(id=id).all()
    temp = []
    for myfriend in myfriends:
        element = myfriend.friend_id
        temp.append(element)

    a = set(temp)
    n = int(friend_id)
    if n in a:
        return ("Error: You are friends already")"""

    friend = User.query.filter_by(id=friend_id).first()
    user = User.query.filter_by(id=id).first()
    sendNewFriendMessage(id, friend_id)
    loadData()
    user.friends.append(friend)
    db.session.commit()
    return "success"

@app.route('/search', methods=['POST'])
def search():
    search = request.form.get('search', None)
    if search:
        users = User.query.filter(User.name.like(f'%{search}%')).all()
        return render_template('search.html', results=users)
    id = session['user_id']
    user = User.query.filter_by(id=id).first()
    
    if user is None:
        return redirect("/login")

    subq = db.session.query(user_friend).filter(user_friend.c.friend_id == id).subquery()
    thefriends = User.query.join(subq, User.id == subq.c.user_id).all()
    ourfriends = []
    for afriend in user.friends:
        ourfriends.append(afriend.id)
    for ufriend in thefriends:
        ourfriends.append(ufriend.id)
    allfriends = User.query.filter(User.id.in_(ourfriends))
    return render_template('search.html', results=allfriends)

@app.route('/search-all', methods=['POST'])
def searchall():
    search = request.form.get('searchall', None)
    if search:
        users = User.query.filter(User.name.like(f'%{search}%')).all()
        return render_template('allsearch.html', results=users)
    id = session['user_id']
    user = User.query.filter_by(id=id).first()
    
    if user is None:
        return redirect("/login")

    subq = db.session.query(user_friend).filter(user_friend.c.friend_id == id).subquery()
    thefriends = User.query.join(subq, User.id == subq.c.user_id).all()
    ourfriends = []
    for afriend in user.friends:
        ourfriends.append(afriend.id)
    for ufriend in thefriends:
        ourfriends.append(ufriend.id)
    allfriends = User.query.filter(User.id.in_(ourfriends))
    return render_template('allsearch.html', results=allfriends)


@app.route('/retrieve-message', methods=['GET'])
def retrieveMessage():
    user_id = session['user_id']
    friend_id = session.get('friend_id', id)
    messages = Message.query.filter(db.or_(db.and_(Message.user_id.like(user_id), Message.friend_id.like(friend_id)), db.and_(Message.friend_id.like(user_id), Message.user_id.like(friend_id))))
    if messages:
        return render_template('messages.html', messages=messages)

@app.route('/retrieve-friend', methods=['GET'])
def retrieveFriend():
    friend_id = session.get('friend_id', id)
    friend = User.query.filter_by(id=friend_id).first()
    return render_template('fhead.html', friend=friend)

@app.route('/retrieve-user', methods=['GET'])
def retrieveUser():
    id = session['user_id']
    user = User.query.filter_by(id=id).first()
    return render_template('loaduser.html', user=user)

@app.route('/retrieve-user-image', methods=['GET'])
def retrieveUserImage():
    id = session['user_id']
    user = User.query.filter_by(id=id).first()
    return render_template('userimage.html', user=user)

@app.route('/get-message', methods=['POST'])
def getMessage():
    user_id = session['user_id']
    session['friend_id'] = None
    friend_id = request.form.get("friend_id")
    if not friend_id:
        flash("User not found!")
        return redirect("/")
    messages = Message.query.filter(db.or_(db.and_(Message.user_id.like(user_id), Message.friend_id.like(friend_id)), db.and_(Message.friend_id.like(user_id), Message.user_id.like(friend_id)))).group_by(Message.date)

    session['friend_id'] = int(friend_id)
    query = db.session.query(Message).filter(db.and_(Message.friend_id.like(user_id), Message.user_id.like(friend_id))).all()
    for c in query:
        c.views = 1
    db.session.commit()
    #return jsonify(messages)
    return render_template('messages.html', messages=messages)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/send-message', methods=['POST'])
def sendMessage():
    user_id = session['user_id']
    friend_id = session['friend_id']
    message = request.form.get("message")
    secret_key_sender_N = request.form.get("secret_key_sender_N")
    secret_key_sender_E = request.form.get("secret_key_sender_E")

    path_temp = ""
    ten_file_temp = ""
    if not message and 'file' not in request.files:
        return render_template('form.html')      
    
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '':
            return "No file selected"
        
        if file and allowed_file(file.filename):
           
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER_TEMP'], filename)
            file.save(path)
            path_temp = path
            ten_file_temp = filename

            # PublicKeyE và N lấy từ database là của Receiver
            friend_info = User.query.filter_by(id=friend_id).first()
            if friend_info:
                publicKey_receiver_E = friend_info.publicKeyE
                publicKey_receiver_N = friend_info.publicKeyN

            # Tạo Signature File
            id = HashToId(path_temp)

            # Mã hoá Signature vừa tạo bằng khoá bí mật của Sender, sau đó lưu vào file
            luuchuoi = Encrypt(id, int(secret_key_sender_E), int(secret_key_sender_N))
            tenfile_sig_enc = "temp/"+ ten_file_temp + ".enc_signature_enc" + ".txt"
            WriteToFiles(tenfile_sig_enc, luuchuoi)

            # Mã hoá file bằng AES
            key = get_random_bytes(32)
            enc = Encryptor(key)
            enc.encrypt_file(str(path_temp))

            # Mã hoá key AES bằng RSA ( dùng khoá công khai của Receiver ), sau đó lưu vào file
            msg = key.decode("latin-1")
            luuchuoiKeyAES = Encrypt(msg,int(publicKey_receiver_E),int(publicKey_receiver_N))
            tenfile_keyaes_enc = "temp/"+ ten_file_temp + ".enc" + "_KeyAES_enc"+ ".txt"
            WriteToFiles(tenfile_keyaes_enc, luuchuoiKeyAES)

    else:
        filename = None
    
    query = Message(user_id=user_id, friend_id=friend_id, send_id=user_id, message=message, attachement=filename) 
    db.session.add(query)
    db.session.commit()
    messages = Message.query.filter(db.or_(db.and_(Message.user_id.like(user_id), Message.friend_id.like(friend_id)), db.and_(Message.friend_id.like(user_id), Message.user_id.like(friend_id))))
    loadData()

    return render_template('form.html', messages=messages)

@app.route('/all-user-message', methods=['GET'])
def getAllUserMessage():
    id = session['user_id']

    friends = db.session.query(Message).filter(db.or_(Message.friend_id.like(id), Message.user_id.like(id))).group_by(Message.send_id).order_by(db.desc(Message.date), db.func.max(Message.date)).all()

    return render_template('friends.html', friends=friends)

@app.route('/temp/<filename>', methods=['GET'])
def download_encrypted_file(filename):
    user_id = session['user_id']
    # Lấy đường dẫn đến tệp cần giải mã
    encrypted_file_path = os.path.join(os.getcwd(), 'temp', filename)

    # Yêu cầu người dùng nhập secret key
    secret_key_rev_N = request.args.get('secret_key_rev_N')
    secret_key_rev_E = request.args.get('secret_key_rev_E')

    # Giải mã tệp
    # Đọc file AESKey.txt của Alice gửi sau đó dùng khoá bí mật của Bob để giải mã
    tenfile_aeskey = "temp/"+filename+"_KeyAES_enc.txt"
    AESKey = ReadKey(tenfile_aeskey,' ')
    AESKeyDecrypt = Decrypt(AESKey, int(secret_key_rev_E), int(secret_key_rev_N)).encode("latin-1")

    # Copy file enc ra 1 bản copy mới
    shutil.copyfile("temp/"+filename, "temp/copy-"+filename)

    # sau đó dùng khoá AES vừa giải mã được cho vào class Encryptor để giải mã file abc.docx.enc
    enc = Encryptor(AESKeyDecrypt)
    enc.decrypt_file(str("temp/copy-"+filename))

    # sau khi giải mã file docx ra thì dùng hàm hash để hash ID của file doc vừa giải mã ra id'
    pathforid = "temp/copy-"+filename.replace('.enc', '')
    IdDocBob = HashToId(pathforid)

    # Lấy PublicKeyE và N từ database của friend và id doc ( đã mã hoá ) được gửi từ Alice
    friend_info = db.session.query(User.publicKeyE, User.publicKeyN)\
    .join(Message, User.id == Message.user_id)\
    .filter(Message.friend_id == user_id, Message.attachement == filename.replace('.enc',''))\
    .first()
    if friend_info:
        publicKey_receiver_E = friend_info.publicKeyE
        publicKey_receiver_N = friend_info.publicKeyN

    IdDocAlice = ReadKey("temp/"+filename+"_signature_enc.txt",' ')

    # rồi dùng khoá công khai của Alice để giải mã Id doc vừa đọc được
    IdDocAlice = Decrypt(IdDocAlice, int(publicKey_receiver_E), int(publicKey_receiver_N))

    # cuối cùng so sánh Id' mà Bob hash ra so với Id Doc ( của Alice ) vừa giải mã ra để so sánh, nếu bằng nhau thì file Doc đúng

    if (IdDocBob == IdDocAlice):
        
        # Trả về tệp đã giải mã để người dùng tải xuống
        file_return = "temp/copy-"+ filename.replace('.enc', '')
        new_filename = file_return.replace('copy-','')
        os.rename(file_return, new_filename)
        response = send_file("temp/"+filename.replace('.enc',''), as_attachment=True)
        os.remove('temp/'+filename.replace('.enc',''))
        return response
    else:
        return "Lỗi khi giải mã tệp."

@app.route('/update-profile', methods=['POST'])
def updateProfile():
    id = session['user_id']
    name = request.form.get("name")
    about = request.form.get("about")
    
    if not name:
        return f"<span style='color:red'>Name cannot be empty!</span>"

    elif not about:
        return ("<span style='color:red'>About cannot be empty!</span>")
    
    user = User.query.filter_by(id=id).first()
    
    if 'file' in request.files:
        
        file = request.files['file']

        if file.filename == '':
            return ("No file selected")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
    else:
        filename = user.image
    
    user.name = name
    user.about = about
    user.image = filename
    db.session.commit()
    loadData()

    return "<span style='color:green'>Profile Updated</span>"


@app.route('/check-count', methods=['POST'])
def checkCount():
    id = session["user_id"]
    friend_id = int(request.form.get("count"))
    count = db.session.query(db.func.count(Message.id)).filter(db.and_(Message.friend_id.like(id), Message.user_id.like(friend_id))).filter(Message.views==0).scalar()
    return render_template("count.html", count=count)

@app.route('/contact-info', methods=['GET'])
def contactInfo():
    session_friend = session['friend_id']
    friend = User.query.filter_by(id=session_friend).first()
    return render_template('contact.html', friend=friend)

@socketio.on('message')
def handle_message(data):
    print(data)

def loadData():
    socketio.emit('dataUpdated', {'data': 42})

def showCount():
    print("Count updated")
    socketio.emit('updateCount', {'data': 42})

@app.route('/delete-message', methods=['POST'])
def deleteMessage():
    messageId = request.form.get("messageId")
    if messageId:
        query = Message.query.filter_by(id=messageId).one()
    db.session.delete(query)
    db.session.commit()
    loadData()
    return render_template('form.html')

@app.route('/<name>/<email>')
def gjsk(name, location):
    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()

    return '<h1>Added New User</h1>' 

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

if __name__ == '__main__':
    socketio.run(app)
