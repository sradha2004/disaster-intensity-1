from flask import Flask, render_template, flash, request, session, send_file
from flask import render_template, redirect, url_for, request
import os
import mysql.connector
import warnings
import datetime
import cv2
import pickle
import numpy as np
# Load trained model
model = pickle.load(open('Earth/prediction-gb-model.pkl', 'rb'))

from flask import Flask, render_template, request, jsonify



app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'



@app.route("/")
def homepage():
    return render_template('index.html')


@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')

    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb ")
    data = cur.fetchall()

    return render_template('AdminHome.html', data=data)


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['pas'] == 'admin':
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb")
            data = cur.fetchall()
            flash('You are Logged In...!')
            return render_template('AdminHome.html', data=data)
        else:
            flash("UserName or Password Incorrect!")

            return render_template('AdminLogin.html')




@app.route("/NewUser")
def NewUser():
    return render_template('NewUser.html')


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['uname']
        Password = request.form['pas']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' ")
        data = cursor.fetchone()
        if data is None:

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
            cursor = conn.cursor()
            cursor.execute(
                "insert into regtb values('','" + name + "','" + age + "','" + mobile + "','" + email + "','" + address + "','" +
                username + "','" + Password + "')")
            conn.commit()
            conn.close()
            flash('Record Saved...!')
            return render_template('UserLogin.html')


        else:
            flash('Already Register Username')
            return render_template('NewUser.html')


@app.route('/UserLogin')
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':

        username = request.form['uname']
        password = request.form['pas']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('UserLogin.html')

        else:
            session['address'] = data[5]
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')

            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where UserName='"+ username +"'")
            data = cur.fetchall()
            flash('You are Logged In...!')
            return render_template('UserHome.html', data=data)



@app.route("/UserHome")
def UserHome():
    username = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where UserName='" + username + "'")
    data = cur.fetchall()
    return render_template('UserHome.html', data=data)


@app.route("/UReports")
def UReports():
    username = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM reporttb where UserName='" + username + "'")
    data = cur.fetchall()
    return render_template('UReports.html', data=data)


@app.route("/AReports")
def AReports():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM reporttb")
    data = cur.fetchall()
    return render_template('AReports.html', data=data)


@app.route("/Prediction")
def Prediction():
    return render_template('Prediction.html')


@app.route("/testimage", methods=['GET', 'POST'])
def testimage():
    if request.method == 'POST':
        import datetime
        import time
        username = session['uname']
        address = session['address']
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        import random
        pn = random.randint(1111, 9999)

        file = request.files['fileupload']
        file.save('static/Out/'+str(pn)+".jpg")

        img = cv2.imread('static/Out/'+str(pn)+".jpg")
        if img is None:
            print('no data')

        img1 = cv2.imread('static/Out/'+str(pn)+".jpg")
        print(img.shape)
        img = cv2.resize(img, ((int)(img.shape[1] / 5), (int)(img.shape[0] / 5)))
        original = img.copy()
        neworiginal = img.copy()
        cv2.imshow('original', img1)
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

        img1S = cv2.resize(img1, (960, 540))

        cv2.imshow('Original image', img1S)
        grayS = cv2.resize(gray, (960, 540))
        cv2.imshow('Gray image', grayS)

        gry = 'static/Out/gry.jpg'

        cv2.imwrite(gry, grayS)
        from PIL import ImageOps, Image

        im = Image.open(file)

        im_invert = ImageOps.invert(im)
        inv = 'static/Out/inv.jpg'
        im_invert.save(inv, quality=95)

        dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
        cv2.imshow("Nosie Removal", dst)
        noi = 'static/Out/noi.jpg'

        cv2.imwrite(noi, dst)

        import warnings
        warnings.filterwarnings('ignore')

        import tensorflow as tf
        classifierLoad = tf.keras.models.load_model('model.h5')

        import numpy as np
        from keras.preprocessing import image

        test_image = image.load_img('static/Out/'+str(pn)+".jpg", target_size=(200, 200))
        #img1 = cv2.imread('static/Out/Test.jpg')
        # test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis=0)
        result = classifierLoad.predict(test_image)
        image = 'static/Out/'+str(pn)+".jpg"
        out = ''
        pre = ''
        if result[0][0] == 1:
            out = "Cyclone"
            color = '#1E90FF'  # Dodger Blue (strong wind / ocean)
            sendmsg('9074458220', out + " For More info Visit in Site")
            sendmail("sradhasreekumar2004@gmail.com", "Disaster Name-" + out,image)

        elif result[0][1] == 1:
            out = "Earthquake"
            color = '#B22222'  # FireBrick Red (danger / alert)
            sendmsg('9074458220', out + " For More info Visit in Site")
            sendmail("sradhasreekumar2004@gmail.com", "Disaster Name-" + out,image)

        elif result[0][2] == 1:
            out = "Flood"
            color = '#0077BE'  # Deep Water Blue
            sendmsg('9074458220', out + " For More info Visit in Site")
            sendmail("sradhasreekumar2004@gmail.com", "Disaster Name-" + out,image)

        elif result[0][3] == 1:
            out = "Wildfire"
            color = '#FF4500'  # Orange Red (fire)
            sendmsg('9074458220', out + " For More info Visit in Site")
            sendmail("sradhasreekumar2004@gmail.com", "Disaster Name-" + out,image)

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1naturaldisasterdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into reporttb values('','" + username + "','" + address + "','" + date + "','" + timeStamp + "','" + out + "','" +str(pn)+".jpg"+ "')")
        conn.commit()
        conn.close()
        flash('Record Saved...!')
        org = 'static/Out/Test.jpg'
        gry = 'static/Out/gry.jpg'
        inv = 'static/Out/inv.jpg'
        noi = 'static/Out/noi.jpg'

        return render_template('Prediction.html', result=out, org=org, gry=gry, inv=inv, noi=noi,color=color)




@app.route("/EarthPredict")
def EarthPredict():
    return render_template('EarthPredict.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form values
        features = [
            float(request.form['magnitude']),
            float(request.form['cdi']),
            float(request.form['mmi']),
            float(request.form['tsunami']),
            float(request.form['sig']),
            float(request.form['nst']),
            float(request.form['dmin']),
            float(request.form['gap']),
            float(request.form['depth']),
            float(request.form['latitude']),
            float(request.form['longitude'])
        ]

        final_features = np.array([features])

        prediction = model.predict(final_features)[0]

        # Convert numeric prediction to label
        alert_map = {
            0: "Green",
            1: "Yellow",
            2: "Orange",
            3: "Red"
        }

        result = alert_map.get(prediction, "Unknown")
        if result == "Green":
            color = 'green'
        elif result == "Yellow":
            color = 'yellow'
        elif result == "Orange":
            color = 'orange'
        elif result == "Red":
            color = 'red'
        #sendmail("sradhasreekumar2004@gmail.com", f"Earth Quake Alert Level: {result}")
        sendmsg('9074458220',f"Earth Quake: {result}")
        return render_template('EarthPredict.html', prediction_text=f"Alert Level: {result}",color=color)

    except Exception as e:
        return render_template('EarthPredict.html', prediction_text=f"Error: {str(e)}")




def sendmsg(targetno,message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")


def sendmail(Mailid,message,image):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr =  Mailid

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    # string to store the body of the mail
    body = message

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = image
    attachment = open(image, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "kkvz xxke jmeb pcyb")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
