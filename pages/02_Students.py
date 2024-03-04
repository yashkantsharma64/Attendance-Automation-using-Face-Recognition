import streamlit as st
import pandas as pd
import pyrebase
import plotly.express as px


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
        if flag == 1:
            st.title("Students")
            students = []
            # current_date = datetime.date.today().strftime("%Y-%m-%d")
            for parent in db.get().each():
                firebase_data = db.child('/'+parent.key()).get()
                if firebase_data:
                    # Append each entry as a dictionary into the students list
                    flag = 0
                    for entry in firebase_data.each():
                        if entry.val() == 'Aaditya Kumar':
                            flag = 1
                    if not flag:
                        students.append(firebase_data.val())

            rd = st.radio(
                "Select an option",["Total enrolled students", "Students' statistics"]
            )
            if rd == "Total enrolled students":
                st.header("Enrolled Students")
                if students:
                    final_df = pd.DataFrame(students)  # Convert the list of dictionaries into a DataFrame
                    final_df = final_df.loc[:, ['Name','Roll No','Section','Course','Year','Email ID']]
                    search = st.text_input("Search")
                    if search:
                        final = final_df[final_df['Name'].str.contains(search)]
                    else:
                        final = final_df  
                    st.dataframe(final)
                else:
                    st.write("No data retrieved from Firebase.")
            else:
                st.header("Statistics")
                total_classes = 0
                attended_classes = 0
                per = []
                for parent in db.get().each():
                    data = db.child(parent.key()).child("Dates").get()
                    total_classes = 0
                    attended_classes = 0
                    for entry in data.each():
                        total_classes += 1
                        if entry.val() == 'Present':
                            attended_classes += 1
                    if attended_classes!=0 and total_classes!=0:
                        percentage = (attended_classes/total_classes)*100
                        per.append(percentage)
                    else:
                        per.append(0)
                names = []
                for parent in db.get().each():
                    data = db.child(parent.key()).get()
                    for entry in data.each():
                        if entry.key() == "Name" and entry.val() != "Aaditya":
                            names.append(entry.val())
                dict = {
                    'Students': names,
                    'Total Attendance(%)': per
                }
                d_frame = pd.DataFrame(dict)
                d_frame = d_frame.loc[0:1, ['Students', 'Total Attendance(%)']]
                fig = px.bar(
                    d_frame,
                    x = "Students",
                    y = "Total Attendance(%)",
                    title = "Bar Graph for comparative analysis"
                )
                st.plotly_chart(fig) 
        else:
            st.write("Only Admin can access this page.")
else:
    st.warning("Please Login/SignUp")