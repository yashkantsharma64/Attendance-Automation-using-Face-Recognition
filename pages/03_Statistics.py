import streamlit as st
import plotly.graph_objects as go
import pyrebase



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

st.title("Statistics")

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
        rno = st.text_input("Search by Roll Number")
        total_classes = 0
        attended_classes = 0
        name = ''

        if rno:
          if rno != '22021345':
            for parent in db.get().each():
              if parent.key() == rno:
                d = db.child(parent.key()).get()
                for e in d.each():
                    if e.key() == 'Name':
                      name = e.val()
                data = db.child(parent.key()).child("Dates").get()
                for entry in data.each():
                    total_classes += 1
                    if entry.val() == 'Present':
                      attended_classes += 1
        else:
          st.write("Please choose a roll number.")
        percentage = 0
        if attended_classes!=0 and total_classes==0:
          st.write("No data to show.")
        elif attended_classes!=0 and total_classes!=0:
          percentage = (attended_classes/total_classes)*100
          percentage = round(percentage, 2)

          st.write("Name : ", name)
          st.write("Total Attendance Percentage : ", str(percentage))
          label = ['Present', 'Absent']
          dat = [percentage, 100-percentage]
          fig = go.Figure(go.Pie(labels = label, values = dat, hoverinfo = "label+percent", textinfo = "value"))
          st.header("Attendence Distribution")
          st.plotly_chart(fig)
      #Student
      else:
        total_classes = 0
        attended_classes = 0
        name = ''
        for parent in db.get().each():
          d = db.child(parent.key()).get()
          for e in d.each():
            if e.val() ==st.session_state['em']:
              for en in d.each():
                if en.key() == 'Name':
                  name = en.val()
              data = db.child(parent.key()).child("Dates").get()
              for entry in data.each():
                  total_classes += 1
                  if entry.val() == 'Present':
                          attended_classes += 1
    
        percentage = 0
        if attended_classes!=0 and total_classes==0:
          st.write("No data to show.")
        elif attended_classes!=0 and total_classes!=0:
          percentage = (attended_classes/total_classes)*100
          percentage = round(percentage, 2)

          st.write("Name : ", name)
          st.write("Total Attendance Percentage : ", str(percentage))
          label = ['Present', 'Absent']
          dat = [percentage, 100-percentage]
          fig = go.Figure(go.Pie(labels = label, values = dat, hoverinfo = "label+percent", textinfo = "value"))
          st.subheader("Attendence Distribution")
          st.plotly_chart(fig)
  f.close()
else:
    st.warning("Please Login/SignUp")
            