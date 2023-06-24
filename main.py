from flask import Flask, render_template, Response, flash, request, redirect, url_for, session
from config import DevConfig
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import facerec_from_webcam_faster as facerec
from face_rec_verify import Face_rec
import process_movie as proc_movie
import get_single_frame as getframe
import os, cv2
import face_recognition

from PIL import Image
from werkzeug.utils import secure_filename

from time import sleep

UPLOAD_FOLDER = 'static/face_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__, static_folder='./static')
app.config.from_object(DevConfig)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'face_rec_login'

mysql = MySQL(app)
current_id = 0
model = "large"
blur = "no"
noise = "no"
matches_count = 0

def convert_encodings_to_intlist(account):
    
    for i in range(0, len(account)):
        
        string = (account[i][1:len(account[i])-1]) 
        string = string.replace(" ",",")
        string = string.replace(",,",",")
        string = string.replace(",,,",",")
        string = string.replace("\n","")
        account_list = string.split(",")
       
    for i in account_list:
        if i == '':
            account_list.remove(i)

    final_list = [float(ele) for ele in account_list]
    #final_list_doubled = [final_list, final_list]

    return final_list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():

    return render_template('base.html')

@app.route('/admin')
def admin():
    try:
        if session['id'] and session['id'] == 1:
            return render_template('admin.html')
    except:
        return render_template('login.html')

@app.route('/user')
def user():
    try:
        if session['id']:
            return render_template('user_panel.html')
    except:
        return render_template('login.html')
@app.route('/face_rec', methods=['GET', 'POST'])
def face_rec():
    model = "small"
    blur = "no"
    noise = "no"
    if request.method == 'POST':
        if 'model' in request.form:
            if  request.form.get('model') == '5 points':
                model = "small"
            else:
                model = "large"
            return redirect(url_for('video_feeed', model = model))

        if 'model_blur' in request.form:
            if request.form.get('model_blur') == '5 points - blur':
                model = "small"
                blur = "yes"
                noise = "no"
            else:
                model = "large"
                blur = "yes"
                noise = "no"
            return redirect(url_for('video_feeed', model = model, blur = blur, noise = noise))

        if 'model_noise' in request.form:
            if request.form.get('model_noise') == '5 points - noise':
                model = "small"
                noise = "yes"
                blur = "no"
            else:
                model = "large"
                noise = "yes"
                blur = "no"
            return redirect(url_for('video_feeed', model = model, blur = blur, noise = noise))
    
    return render_template('facerec.html')

@app.route('/video_feeed', methods=['GET', 'POST'])
def video_feeed():
    model = "large"
    blur = "no"
    noise = "no"
    remove_noise = 'no'
    if 'blur' in request.args and request.args['blur'] == 'yes':
        blur = request.args['blur']
    else:
        blur = 'no'

    if 'noise' in request.args and request.args['noise'] == 'yes':
        noise = request.args['noise']
    else:
        noise = 'no'   
    if 'remove_noise' in request.form:
        if request.form.get('remove_noise') == 'Median filter':
            remove_noise = 'median'
        elif request.form.get('remove_noise') == 'Gaussian filter':
            remove_noise = 'gauss'
        elif request.form.get('remove_noise') == 'Average filter':
            remove_noise = 'average'
        elif request.form.get('remove_noise') == 'Bilateral filter':
            remove_noise = 'bilateral'
    else:
        remove_noise = 'no'
    try:       
        model = request.args['model']
        message = request.args['message']
    except:
        message = ""        
    finally:       
        return render_template('video_feeed.html', message = message, model = model, blur = blur, noise = noise, remove_noise = remove_noise)
        
    return render_template('video_feeed.html', message = message, model = model, blur = blur, noise = noise, remove_noise = remove_noise)

@app.route('/verify_face', methods = ['GET'])
def verify_face():
    face_rec = Face_rec(0)
    capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    model = "large"
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT face_encodings FROM account WHERE username = % s',(session['username'], ))
    account = cursor.fetchone()               
    if account:
        encodings = convert_encodings_to_intlist(account)
        encodings_doubled = [encodings, encodings]
        username = [session['username']]
        r = face_rec.facerec(capture, model, encodings_doubled, username)   

        if r == True:
            session['loggedin'] = True
            print(session['id'])
            if session['id'] == 1:
                return redirect(url_for('admin'))
            return redirect(url_for('user'))
        else:
            msg = 'Incorrect face'
            return render_template('login.html', msg = msg)
    return render_template('login.html')
    

@app.route('/clean_feed', methods = ['GET'])
def clean_feed():
    face_rec = Face_rec(0)
    capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    model = "large"
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT face_encodings FROM account WHERE username = % s',(session['username'], ))
    account = cursor.fetchone()               
    if account:
        encodings = convert_encodings_to_intlist(account)
        username = [session['username']]
        r = face_rec.facerec(capture, model, encodings, username)   

        if r == True:
            session['loggedin'] = True
            return redirect(url_for('user'))
    return render_template('login.html')

@app.route('/clean_feeed', methods = ['GET'])
def clean_feeed():
    face_rec = Face_rec(0)
    capture = cv2.VideoCapture(0)
    model = "large"
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT face_encodings FROM account WHERE username = % s',(session['username'], ))
    account = cursor.fetchone()               
    if account:
        encodings = convert_encodings_to_intlist(account)
        username = [session['username']]
        r = Response(face_rec.facerec(capture, model, encodings, username), mimetype='multipart/x-mixed-replace; boundary=frame')   
        
        while r:
            return r  
            
    return render_template('login.html')

@app.route('/process_movie', methods = ['GET'])
def process_movie():
    model = 'large'
    proc_movie = Face_rec(0)
    
    #print(file_path)
    print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
    capture = cv2.VideoCapture(file_path,cv2.CAP_DSHOW)
    model = "large"
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT face_encodings FROM faces')
    faces_data = cursor.fetchall()
    face_encodings = []
    print(faces_data)
    for face in range(0, len(faces_data)):
        face_encodings.append(convert_encodings_to_intlist(faces_data[face]))
    #print(face_encodings)
    cursor.execute('SELECT first_name, surname FROM FACES')
    faces_data_names = cursor.fetchall()
    face_names = []
    for name in faces_data_names:
        face_names.append(name[0]+' '+name[1])
    print(face_names)

    r = Response(proc_movie.facerec(capture, model, face_encodings, face_names), mimetype='multipart/x-mixed-replace; boundary=frame')   
    #print(face_encodings) 
    while r:
        print('gitgut')
        return r

@app.route('/on_movie_recognition', methods = ['GET'])
def on_movie_recognition():
    file_path = request.args['file_path']
    print(file_path)
    return render_template('movie_feed.html', file_path = file_path)

@app.route('/video_feed/<model>/<blur>/<noise>/<remove_noise>')
def video_feed(model, blur, noise, remove_noise):
    try:
        capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        #capture = cv2.VideoCapture('faces.mp4')
    except:
        sleep(3)
        capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        #capture = cv2.VideoCapture('faces.mp4')
    print(model, blur, noise)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT face_encodings FROM faces')
    faces_data = cursor.fetchall()
    face_encodings = []
    print(faces_data)
    for face in range(0, len(faces_data)):
        face_encodings.append(convert_encodings_to_intlist(faces_data[face]))
    #print(face_encodings)
    cursor.execute('SELECT first_name, surname FROM FACES')
    faces_data_names = cursor.fetchall()
    face_names = []
    for name in faces_data_names:
        face_names.append(name[0]+' '+name[1])
    r = Response(facerec.facerec(capture, face_encodings, face_names, model, blur, noise, remove_noise), mimetype='multipart/x-mixed-replace; boundary=frame')   
    route = request.url
    print(route)

    while r:
        if 'video_feed' in route:
            return r
        else:
            print("STOP")
            capture.release()
            break
            
@app.route('/get_framee', methods=['GET', 'POST'])
def get_framee():
    print(request)
    
    if request.method == 'POST':
        print(request)
        img_path = './static/face_images/Frame.jpg'
        frame = face_recognition.load_image_file(img_path)
        img_to_save = cv2.imread(img_path)
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        if getframe.is_face_on_frame(frame) == 0 and first_name and surname:
            face_encodings = face_recognition.face_encodings(frame)
            print(getframe.is_face_on_frame(frame))
            face_name = first_name+'_'+surname
            path_to_save = './static/face_images/'+face_name+'.jpg'
            cv2.imwrite(path_to_save, img_to_save)
            cursor = mysql.connection.cursor()        
            cursor.execute('INSERT INTO faces VALUES (NULL, %s, %s, %s, %s)', (first_name, surname, face_encodings, face_name+'.jpg',))
            mysql.connection.commit()

            if os.path.exists(img_path):
                os.remove(img_path)
            message = "Face saved succesfully"
            return redirect(url_for('video_feeed',  message = message, model = 'small')) 
        elif getframe.is_face_on_frame(frame) == 1:
            message = "You can add one face at time"
            return redirect(url_for('video_feeed',  message = message, model = 'small'))
        elif getframe.is_face_on_frame(frame) == 2:
            message = "No face detected"
            return redirect(url_for('video_feeed',  message = message, model = 'small'))
        message = "No face detected"
        return redirect(url_for('video_feeed',  message = message, model = 'small'))
    if is_image_available('Frame.jpg'):  
        img_path = './static/face_images/Frame.jpg'       
        return render_template('save_frame.html', img_path = img_path)
    else:
        message = "No face detected"
        return redirect(url_for('video_feeed',  message = message, model = 'small')) 

@app.route('/get_frame', methods=['GET', 'POST'])
def get_frame():
    single_frame = getframe.singleframe()
    if getframe.is_face_on_frame(single_frame) == 0:
        cropped_face = getframe.crop_face(single_frame)        
        cv2.imwrite('./static/face_images/Frame.jpg', cropped_face)
        return redirect(url_for('get_framee'))
    else:
        message = "No face detected"
        return redirect(url_for('video_feeed',  message = message, model = 'small'))
       
def is_image_available(img_name):
    gallery_path = app.config['UPLOAD_FOLDER']
    if img_name in os.listdir(gallery_path):
        return True
    else:
        return False

@app.route('/uploadface', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):          
            filename = secure_filename(file.filename) 
            print(app.config['UPLOAD_FOLDER'])
            file.save(app.config['UPLOAD_FOLDER']+"/"+filename)
            img = face_recognition.load_image_file(file)
            smaller_img = getframe.get_small_frame(img)
            try:
                if request.args['username']:
                    username = request.args['username']
                    if username and getframe.is_face_on_frame(smaller_img) == 0:         
                        return redirect(url_for('detect_faces_in_image', filename = filename, username = username))
            except:
                

                if getframe.is_face_on_frame(smaller_img) == 0:         
                    return redirect(url_for('detect_faces_in_image', filename = filename))

                elif getframe.is_face_on_frame(smaller_img) == 1:
                    os.remove(app.config['UPLOAD_FOLDER']+"/"+filename)
                    return render_template('uploadface.html', message = "You can add only one face at time")
                else:
                    os.remove(app.config['UPLOAD_FOLDER']+"/"+filename)
                    return render_template('uploadface.html', message = "No face detected")
    try:
        if session['id'] and session['id'] == 1:       
            return render_template('uploadface.html')
    except:
        return render_template('login.html')

@app.route('/saveface', methods=['GET', 'POST'])
def detect_faces_in_image():
    
    file_name = request.args['filename']

    try:
        user_name = request.args['username']
    except:
        user_name = None
    img = face_recognition.load_image_file('static/face_images/'+file_name, )
    
    face_box_coords = face_recognition.face_locations(img)
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    img_path = "static/face_images/"+file_name
    print(img_path)
    #top = face_box_coords[0][0]
    #right = face_box_coords[0][1]
    #bottom = face_box_coords[0][2]
    #left = face_box_coords[0][3]

    if user_name:
        temp_face_encodings = return_face_encodings(img_path, user_name)
        face_encodings = temp_face_encodings['encoding']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM account WHERE username = % s',(user_name, ))
        account = cursor.fetchone()
        print(account)
        if account:
            cursor.execute('UPDATE account SET face_encodings = % s WHERE username = % s',(face_encodings, user_name,))
            mysql.connection.commit()
            os.remove(img_path)
            print(user_name)
            return render_template('login.html')

    cropped = getframe.crop_face(img) # crop to face bounding
    getframe.save_img(img_path, cropped) # save cropped image

    if request.method == 'POST':  
        first_name = request.form.get('firstname')
        surname = request.form.get('surname')
        face_name = first_name +'_'+surname
        if os.path.exists(img_path):
            os.remove(img_path)
            img_path_cropped = 'static/face_images/'+face_name+'.jpg'
            print(img_path_cropped)
            getframe.save_img(img_path_cropped, cropped)
          
            # add person with name, surname and face encodings to database
            face_encodings = face_recognition.face_encodings(img)[0]
            cursor = mysql.connection.cursor()        
            cursor.execute('INSERT INTO faces VALUES (NULL, %s, %s, %s, %s)', (first_name, surname, face_encodings, face_name+'.jpg',))
            mysql.connection.commit()
                                                                        
            
            #os.remove(img_path)
            return render_template('uploadface.html', message = 'Face saved')
    #os.remove(img_path)
    return render_template('save_upload.html', filename = img_path)

def return_face_encodings(img, face_name):
    img = face_recognition.load_image_file(img)
    unknown_face_encodings = face_recognition.face_encodings(img)

    known_faces =  {
            "name" : face_name,
            "encoding" : unknown_face_encodings[0]
        }

    return known_faces

@app.route('/login', methods = ['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = % s AND password = % s',(username, password))
        account = cursor.fetchone()
        if account:
            session['id'] = account['id']
            #session['face_encodings'] = convert_encodings_to_intlist(account['face_encodings'])
            session['username'] = account['username']
            return redirect(url_for('verify_face', username = username))
            #if session['id'] == 1:
            #    return redirect(url_for('admin', msg = msg))
            #msg = 'Logged in succesfully!'
            #return render_template('base.html', msg = msg)
        else:
            msg = 'Incorrect username or password'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('face_encodings', None)
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and  'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        #face_encodings = return_face_encodings(face_image, username)
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM account WHERE username = % s',(username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers'
        elif not username or not password or not email:
            msg = 'Please insert credentials'
        else:
            session['register_username'] = username
            cursor.execute('INSERT INTO account VALUES (NULL, %s, %s, %s, NULL)', (username, password, email,))
            mysql.connection.commit()
            print(username)
            return redirect(url_for('upload_file', username = username))
            
    elif request.method == 'POST':
        msg = 'Please insert credentials'
    return render_template('register.html', msg = msg)

@app.route('/gallery', methods = ['GET', 'POST'])
def gallery():
    # Ścieżka do folderu z galerią zdjęć
    gallery_path = app.config['UPLOAD_FOLDER']
    print(session['visited'])      

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        print(first_name+last_name)
        # Wyszukiwanie zdjęć pasujących do imienia i nazwiska
        image_list = []
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, first_name, surname, img_path FROM faces')
       
        columns = [col[0] for col in cursor.description]
        profile_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for face in profile_data:
            if (first_name.lower() in face['first_name'].lower()) or (last_name.lower() in face['surname'].lower()):
                image_path = os.path.join(gallery_path, face['img_path'])
                face_name = face['first_name']+' '+face['surname']
                image_list.append({'name': face_name, 'path': image_path, 'id': face['id']})
                
        page, paginated_images, total_pages, prev_page, next_page = pagination(image_list, 100)
        return render_template('gallery.html', image_list = paginated_images, page = page, total_pages= total_pages, prev_page = prev_page, next_page= next_page)
    
    else:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, first_name, surname, img_path FROM faces')
       
        columns = [col[0] for col in cursor.description]
        profile_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print(profile_data)
        image_list = []
        for face in profile_data:
            image_path = os.path.join(gallery_path, face['img_path'])
            face_name = face['first_name']+' '+face['surname']
            image_list.append({'name': face_name, 'path': image_path, 'id': face['id']})
        
        print(image_list)
        page, paginated_images, total_pages, prev_page, next_page = pagination(image_list, 10)

        # Zwracanie szablonu HTML i przekazanie listy zdjęć do wyświetlenia         
        return render_template('gallery.html', image_list = paginated_images, page = page, total_pages= total_pages, prev_page = prev_page, next_page= next_page)


def pagination(images, per_page):
    page = int(request.args.get('page', 1))
        
    total_pages = (len(images) // per_page) + (1 if len(images) % per_page > 0 else 0)

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_images = images[start_index:end_index]

    prev_page = page - 1 if page > 1 else page
    next_page = page + 1 if page < total_pages else page

    return page, paginated_images, total_pages, prev_page, next_page

@app.route('/searchface', methods = ['GET', 'POST'])
def searchface():
    if request.method == 'POST':

        gallery_path = app.config['UPLOAD_FOLDER']
        matching_id_list = []
        matching_name_files = []
        face_encodings_intlist = []

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):          
            filename = secure_filename(file.filename) 
            print(app.config['UPLOAD_FOLDER'])
            file.save(app.config['UPLOAD_FOLDER']+"/"+filename)
        
        img = face_recognition.load_image_file(app.config['UPLOAD_FOLDER']+"/"+filename)

        if getframe.is_face_on_frame(img) == 0:
            # get all face encodings from database 
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT face_encodings FROM faces')
            face_encodings_list = cursor.fetchall()                     
            # get all id from database
            cursor.execute('SELECT id FROM faces')
            id_list = cursor.fetchall()
            
            for i in range(0, len(face_encodings_list)):
                #print(face_encodings_list[i][1])
                #print(temp_face_encodings)
                #print(convert_encodings_to_intlist(temp_face_encodings))
                face_encodings_intlist.append({'id': id_list[i][0], 'face_encoding':convert_encodings_to_intlist(face_encodings_list[i])})
            
            unknown_face_encodings = face_recognition.face_encodings(img)
            print(unknown_face_encodings)
            for encoding in face_encodings_intlist:
                
                # check if face matches any face in database
                match_list = face_recognition.compare_faces(np.array(encoding['face_encoding']), unknown_face_encodings)
                print(match_list)
                if True in match_list:
                    # add matching id to id list
                    matching_id_list.append(encoding['id'])

            if len(matching_id_list) == 0:
                message = 'No face in database'
                return render_template('searchbyface.html', message = message)  

            # fetch names of people that id matches encoding
            try:
                for i in matching_id_list:
                    print(i)
                    cursor.execute('SELECT id, first_name, surname FROM faces WHERE id = % s',(i,))
                    name = cursor.fetchone()
                    print(name)
                    matching_name_files.append(name)
                print(matching_name_files)
            except:
                message = 'No face in database'
                return render_template('searchbyface.html', message = message)
        
            
                #return render_template('searchbyface.html')
            # get list of photo's file names to display
            if len(matching_id_list) >= 1:
                matching_photos = []
                for filename in os.listdir(gallery_path):
                    print(filename)
                    for name in matching_name_files:
                        if filename.lower().startswith(f"{name[1].lower()}_{name[2].lower()}"):
                            img_name = os.path.splitext(filename)[0]
                            image_path = os.path.join(gallery_path, filename)
                            face_id = name[0]
                            matching_photos.append({'name': img_name, 'path': image_path, 'id': face_id})
                     
                page, paginated_images, total_pages, prev_page, next_page = pagination(matching_photos, 50)
            return render_template('gallery.html', image_list = paginated_images, page = page, total_pages= total_pages, prev_page = prev_page, next_page= next_page)
    return render_template('searchbyface.html')

    #print(convert_encodings_to_intlist(face_encodings_list))

@app.route('/profile/<user_id>', methods = ['GET', 'POST'])
def profile(user_id):
    if request.method == 'POST':
        print(request)
        id_to_delete = request.form['parametr']
        cursor = mysql.connection.cursor()
        delete_query = "DELETE FROM your_table WHERE id = %s"
        cursor.execute(delete_query, ((id_to_delete),))
        db.commit()
    gallery_path = app.config['UPLOAD_FOLDER']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT first_name, surname, img_path FROM faces WHERE id = % s', (user_id,))
    columns = [col[0] for col in cursor.description]
    profile_data = [dict(zip(columns, row)) for row in cursor.fetchall()][0]
    image_path = os.path.join(gallery_path, profile_data['img_path'])
    print(image_path)
    print(profile_data)
    if profile_data:
        return render_template('profile.html', profile_data = profile_data, image_path = image_path)
    else:
        return 'Użytkownik o podanym ID nie istnieje.'

@app.route('/delete_face', methods= ['GET', 'POST'])
def delete_face():
    if request.method == 'POST':
        print(request)
        id_to_delete = request.form['parametr']
        cursor = mysql.connection.cursor()
        delete_query = "DELETE FROM faces WHERE id = %s"
        cursor.execute(delete_query, ((id_to_delete),))
        mysql.connection.commit()
        return redirect(url_for('gallery'))
    
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 2048  # 16MB

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']

        # Zapisz przesłany plik w katalogu "uploads"
        try:
            file.save('static/face_images/' + file.filename)
            file_path = 'static/face_images/' + file.filename
            print(file.filename)
            session['movie_name'] = file_path
            print('succes')
            return redirect(url_for('on_movie_recognition', file_path = file_path))
        except:
            print('fail')
    return render_template('upload.html')

    
if __name__ == '__main__':
    app.run(host="0.0.0.0")

