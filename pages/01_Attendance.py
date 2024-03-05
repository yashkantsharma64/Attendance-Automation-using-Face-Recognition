from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import face_recognition
import os
import streamlit as st
import numpy as np
import datetime
import pandas as pd
import pyrebase


class VideoProcessor:
    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")

        faces = cascade.detectMultiScale(cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY), 1.1, 4)

        for x, y, w, h in faces:
            cv2.rectangle(frm, (x, y), (x+w, y+h), (0, 255, 0), 2)
        encodings = face_recognition.face_encodings(frm)[0]
        # Comparing the encodings to the known encodings.
        results = face_recognition.compare_faces(known_encodings, encodings)
        idx = 0
        attendance_marked = False
        try:
            for i in range(len(results)):
                if results[i]:
                    attendance_marked = True
                    idx = i           
        except:
            st.write("Could not recognize face from the dataset!")
        
        if attendance_marked:
            mark_attendance(known_names[idx])
        else:
            st.warning("Failed to detect face! try again.")
        print("Face recognition results:", results)
        return av.VideoFrame.from_ndarray(frm, format='bgr24')


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
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
known_encodings = []
known_names = []
known_images_dir = 'known_face_encodings'

for file in os.listdir(known_images_dir):
    array = np.load(os.path.join(known_images_dir, file))
    known_encodings.append(array)
    known_names.append(file.split('.')[0])



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
            webrtc_streamer(key="key", video_processor_factory=VideoProcessor,
                rtc_configuration=RTCConfiguration(
                    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
                    )
            )
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
