from flask import Flask, render_template, Response, flash, request, redirect, url_for, session
from config import DevConfig
import facerec_from_webcam_faster as facerec
import get_single_frame as getframe
import os, cv2
import face_recognition
import json, codecs, numpy as np
from PIL import Image
from werkzeug.utils import secure_filename

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
VC = cv2.VideoCapture(0)

app = Flask(__name__, static_folder='./static')
app.config.from_object(DevConfig)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('base.html')

@app.route('/video_feeed', methods=['GET', 'POST'])
def video_feeed():
    try:
        message = request.args['message']
    except:
        message = ""
    finally:
        return render_template('video_feeed.html', message = message)

@app.route('/get_framee', methods=['GET', 'POST'])
def get_framee():
    if request.method == 'POST':
        img_path = './static/img/Frame.jpg'
        frame = face_recognition.load_image_file(img_path)
        unknown_face_encodings = face_recognition.face_encodings(frame)
        print(getframe.is_face_on_frame(frame))
    
        if getframe.is_face_on_frame(frame) == 0:
            unknown_face_encodings = face_recognition.face_encodings(frame)
            print(getframe.is_face_on_frame(frame))
            face_name = request.form.get('facename')
                      
            known_faces =  {
                "name" : face_name,
                "encoding" : unknown_face_encodings[0]
            }
                                                                       
            with open('known_faces.json', 'r+') as file:
                # First we load existing data into a dict.
                file_data = json.load(file)
                # Join new_data with file_data inside emp_details
                file_data["known_faces"].append(known_faces)
                # Sets file's current position at offset.
                file.seek(0)
                # convert back to json.
                json.dump(file_data, file, indent = 4, cls = NumpyEncoder)
            if os.path.exists(img_path):
                os.remove(img_path)
            message = "Face saved succesfully"
            return redirect(url_for('video_feeed',  message = message)) 
        elif getframe.is_face_on_frame(frame) == 1:
            message = "You can add one face at time"
            return redirect(url_for('video_feeed',  message = message))
        elif getframe.is_face_on_frame(frame) == 2:
            message = "No face detected"
            return redirect(url_for('video_feeed',  message = message))
       
    return render_template('saveface.html')

@app.route('/get_frame')
def get_frame():
    frame_rect = getframe.draw_rect(getframe.singleframe())
    cv2.imwrite('./static/img/Frame.jpg', frame_rect)
    return Response(getframe.frame_to_bytes(getframe.frame_rbg(frame_rect)), mimetype="image/jpg; boundary=frame")

@app.route('/video_feed')
def video_feed():
    r = Response(facerec.facerec(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    if r.status_code > 400:
        cv2.destroyAllWindows()
        print("STOP")
        return render_template('base.html')
    else:
        return r

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
            if getframe.is_face_on_frame(smaller_img) == 0:         
                return redirect(url_for('detect_faces_in_image', filename = filename))

            elif getframe.is_face_on_frame(smaller_img) == 1:
                os.remove(filename)
                return render_template('uploadface.html', message = "You can add only one face at time")
            else:
                os.remove(filename)
                return render_template('uploadface.html', message = "No face detected")
            
    return render_template('uploadface.html')
   
@app.route('/saveface', methods=['GET', 'POST'])
def detect_faces_in_image():   
    file_name = request.args['filename']
    img = face_recognition.load_image_file('static/img/'+file_name, )
    
    face_box_coords = face_recognition.face_locations(img)
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    img_path = "static/img/"+file_name
    print(img_path)
    #top = face_box_coords[0][0]
    #right = face_box_coords[0][1]
    #bottom = face_box_coords[0][2]
    #left = face_box_coords[0][3]

    #face_box_img = img_to_display.crop((left, top, right, bottom))
    unknown_face_encodings = face_recognition.face_encodings(img) 
    if os.path.exists(img_path):
        os.remove(img_path)
        getframe.draw_rect(img)
        getframe.save_img(img_path, img)

    if request.method == 'POST':  
        face_name = request.form.get('facename')
                      
        known_faces =  {
            "name" : face_name,
            "encoding" : unknown_face_encodings[0]
        }
                                                                       
        with open('known_faces.json', 'r+') as file:
                # First we load existing data into a dict.
            file_data = json.load(file)
                # Join new_data with file_data inside emp_details
            file_data["known_faces"].append(known_faces)
                # Sets file's current position at offset.
            file.seek(0)
                # convert back to json.
            json.dump(file_data, file, indent = 4, cls = NumpyEncoder)

    return render_template('save_upload.html', filename = img_path)

                    
if __name__ == '__main__':
    app.run(host="0.0.0.0")

