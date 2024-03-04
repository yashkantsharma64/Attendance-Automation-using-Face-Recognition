import streamlit as st
import numpy as np
import face_recognition
import cv2
import datetime
import time
import pyrebase


def signup(name):   
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    t0 = time.time()
    img_dir = "./known_face_encodings/"
    frame_placeholder = st.empty()
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = str(datetime.datetime.now())
            frame = cv2.putText(frame, text, (10, 13), font, 0.5, (0,255,0), 1, cv2.LINE_AA)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            frame_copy = frame.copy()
            for(x, y, w, h) in faces:
                # face_offset = frame[y-5:y+h+5, x-5:x+w+5]
                # face_select = cv2.resize(face_offset, (100, 100))
                cv2.rectangle(frame_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # cv2.imshow('Frame', frame)
            frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_copy, channels ="RGB")
            
            encodings = face_recognition.face_encodings(frame)[0]

            t1 = time.time()
            num_seconds = t1-t0

            if num_seconds > 7:
                break
            cv2.waitKey(1) & 0xFF
        else:
            print("Cannot open camera!")
            break
    encodings = np.array(encodings)
    np.save(img_dir+name, encodings)
    cap.release()
    cv2.destroyAllWindows()


#main program
firebaseConfig = {
  'apiKey': "AIzaSyCuNoXmU_YUMFGCPE4EkuzeN2f8V0wG8rg",
  'authDomain': "attendance-automation-data.firebaseapp.com",
  'projectId': "attendance-automation-data",
  'databaseURL': "https://attendance-automation-data-default-rtdb.asia-southeast1.firebasedatabase.app/",
  'storageBucket': "attendance-automation-data.appspot.com",
  'messagingSenderId': "525232309925",
  'appId': "1:525232309925:web:dba7b34597573b43f8af4c",
  'measurementId': "G-H18R2SXZMM"
}
#initializing firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
#creating object to access realtime database of firebase
db = firebase.database()

st.title("Home")
if 'runpage' not in st.session_state:
    st.session_state.runpage = False
if 'em' not in st.session_state:
            st.session_state["em"] = "none"


email = ""
# When user is not logged in
if not st.session_state.runpage:
    ch = st.selectbox("Sign up/Sign in", ('Sign up', 'Sign in'))
    #Sign Up
    if ch == 'Sign up':
        name = st.text_input("Name")
        Section = st.text_input("Section")
        Rno = st.text_input("University Roll Number")
        course = st.selectbox('Course', ('B.tech', 'B.CA', 'B.Com'))
        if course == 'B.tech':  
            year = st.number_input("Year",1, 4, 1)
        elif course == 'B.CA' or course == 'B.Com':  
            year = st.number_input("Year",1, 3, 1)
        email = st.text_input("Email ID")
        pas = st.text_input("Password", type = 'password')
        c = st.columns((4, 1))
        with c[1]:
            signup = st.button("Create Account")
        if signup:
            signup(name)
            user = auth.create_user_with_email_and_password(email, pas)
            st.success("Account created successfully")
            db.child(Rno).child("Name").set(name)
            db.child(Rno).child("Section").set(Section)
            db.child(Rno).child("Roll No").set(Rno)
            db.child(Rno).child("Course").set(course)
            db.child(Rno).child("Year").set(year)
            db.child(Rno).child("Email ID").set(email)
            with open('Students.csv', 'a') as f:
                f.write(f'{name},{Section},{Rno},{course},{email},{"none"}\n')
                f.close()
    #signin/Login
    elif ch == 'Sign in':
        email = st.text_input("Email ID")
        pas = st.text_input("Password", type = 'password')
        l = st.columns((8, 1))
        with l[1]:
            signin = st.button("Login")
        if signin or st.session_state.runpage:
            try:
                #Logging in
                user = auth.sign_in_with_email_and_password(email, pas)
                st.session_state.runpage = True
                st.session_state["em"] = email
                st.success("Logged in successfully!")
            except:
                st.warning("Wrong Username or Password")
                st.session_state.runpage = False
                st.session_state["em"] = "none"

# When user is logged in        
elif st.session_state.runpage:
    for parent in db.get().each():
        d = db.child(parent.key()).get()
        for e in d.each():
            if e.val() ==st.session_state['em']:
                for en in d.each():
                    if en.key() == "Name" and en.val() == "Aaditya Kumar":
                        st.write("Admin")
                        if en.key() == 'Name' or en.key() == 'Email ID':
                            st.write(en.key()," : ", str(en.val()))
                    else:
                        if(en.key() != 'Dates'):
                            st.write(en.key()," : ", str(en.val()))

    if st.button("Logout"):
        
        st.session_state.runpage = False
        st.session_state["em"] = "none"