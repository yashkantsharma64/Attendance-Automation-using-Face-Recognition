import streamlit as st
import pandas as pd
import numpy as np
import face_recognition
import cv2
import datetime
import time
import os
import pyrebase


def face_rec():
    known_encodings = []
    known_names = []
    known_images_dir = 'known_face_encodings'
    frame_placeholder = st.empty()

    for file in os.listdir(known_images_dir):
        array = np.load(os.path.join(known_images_dir, file))
        known_encodings.append(array)
        known_names.append(file.split('.')[0])
    
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    t0 = time.time()
    attendance_marked = False
    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = str(datetime.datetime.now())
        frame = cv2.putText(frame, text, (10, 13), font, 0.5, (0,255,0), 1, cv2.LINE_AA)

        # Converting BGR image to Gray scale image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        frame_copy = frame.copy()
        for(x, y, w, h) in faces:
            cv2.rectangle(frame_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Displaying Frame
        frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_copy, channels ="RGB")

        # Generating face_encodings of the current frame
        encodings = face_recognition.face_encodings(frame)[0]

        # Comparing the encodings to the known encodings.
        results = face_recognition.compare_faces(known_encodings, encodings)

        idx = 0
        try:
            for i in range(len(results)):
                if results[i]:
                    # (top, right, bottom, left) = face_recognition.face_locations(frame)[0]
                    attendance_marked = True
                    idx = i           
        except:
            break
        t1 = time.time()
        if t1-t0 > 5:
            break
        cv2.waitKey(1) & 0xFF
    if attendance_marked:
        mark_attendance(known_names[idx])
    else:
        print("Failed to detect face! try again.")
    print(results)
    cap.release()
    cv2.destroyAllWindows()

# Maring attendance function
def mark_attendance(name):
    with open('attendance.csv', 'r+') as file:
        lines = file.readlines()
        name_list = []
        for line in lines:
            entry = line.split(",")
            name_list.append(entry[0])
        if name not in name_list:
            with open('Students.csv', 'r') as f:
                reader = f.readlines()
                for row in reader:
                    n = row.split(",")
                    if name == n[0]:
                        file.write(f'{n[0]},{n[1]},{n[2]},{n[3]},{n[4][:-1]},{str(datetime.date.today().strftime("%Y-%m-%d"))},{"Present"}\n')
                        st.success("Attendance marked for "+name)
                        break
            f.close()
        else:
            st.warning("Attendance Already Marked!")
    file.close()


#main
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

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

db = firebase.database()

if st.session_state.runpage:
    flag = 0
    with open('Students.csv', 'r') as f:
        reader = f.readlines()

        for row in reader:
            n = row.split(",")
            if n[4] == st.session_state["em"] and n[-1].strip() == 'Admin':
                flag = 1
                break
        #Admin
        if flag == 1:
            st.header("Attendance")

            d = st.date_input("Attendance for", datetime.date.today())
            d = d.strftime("%Y-%m-%d")
            student = []
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            for parent in db.get().each():
                firebase_data = db.child('/'+parent.key()).get()
                if firebase_data:
                    flag = 0
                    for entry in firebase_data.each():
                        if entry.val() == 'Aaditya Kumar':
                            flag = 1
                    if not flag:
                        student.append(firebase_data.val())
            if student:
                final_df = pd.DataFrame(student)  # Convert the list of dictionaries into a DataFrame

                final_df['Date'] = final_df['Dates'].apply(lambda x: x.get(d, 'Not Found'))
    
                # Select desired columns for display
                final_df = final_df[['Name', 'Roll No', 'Section', 'Course', 'Year', 'Email ID', 'Date']]

                st.dataframe(final_df)
            else:
                st.write("No data retrieved from Firebase.")
        #Student
        else:
            st.header("Attendance")
            a = st.button("Mark Attendance", key='b1')
            if a:
                try:
                    face_rec()
                except:
                    st.warning("Failed to detect face! Try again in a well lit environment.")
                with open("attendance.csv", 'r') as file:
                    reader = file.readlines()
                    for line in reader:
                        k = line.split(',')
                        current_date = datetime.date.today().strftime("%Y-%m-%d")
                        for parent in db.get().each():
                            dat = db.child('/'+parent.key()).get()
                            for entry in dat.each():
                                if entry.key() == 'Name' and k[0] == entry.val():
                                    db.child(parent.key()).child("Dates").child(current_date).set("Present") 
                                    break                   # Exit loop if found
                file.close()
    f.close()
else:
    st.warning("Please Login/SignUp")