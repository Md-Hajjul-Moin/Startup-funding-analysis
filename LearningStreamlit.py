import streamlit as st
import pandas as pd
import time

st.title("Learning Streamlit")

st.header("I am a novice to streamlit")

st.subheader("Its feels to easy in reference to the react")

st.write("Write function is used to write something in the website")

st.markdown("""
### My hobbies
- Cricket
- Badminton
- Learning new concepts of AI
""")

st.code("""
#code function is used to write code in the website
import numpy as np
def pythagoras(a,b):
    return np.sqrt(a**2+b**2)
c = pythagoras(3,4)
""")

st.latex(""" e^(i\pi) + 1 = 0""")

df = pd.DataFrame({"name":["alpha","beta","gamma"],
              "experience":[3,4,8],
              "package":[20,1.2,2.9]})
st.dataframe(df)

st.metric("Revenue","Rs. 3cr","5%")
st.metric("Revenue","Rs. 2cr","-25%")

st.json({"name":["alpha","beta","gamma"],
              "experience":[3,4,8],
              "package":[20,1.2,2.9]})

st.image("alpha.jpg")
st.video("beta.mp4")

st.sidebar.title("Sidebar Title")

col1, col2 = st.columns(2)
with col1 :
    st.video("beta.mp4")
with col2:
    st.video("gamma.mp4")

st.error("Login Failed")
st.success("Login successful")
st.warning("Something may go wrong!")

st.write("Progress function is use when some task is in progress and may require some time.")
bar = st.progress(0)
for i in range(1,101):
    time.sleep(0.005)
    bar.progress(i)

st.text_input("Enter email: ")
st.number_input("Enter number: ")
st.date_input("Enter reg date:")

email = st.text_input("Enter email:")
password = st.text_input("Enter password:",type="password")
gender = st.selectbox("Gender",["male","female","rather not to say"])
button = st.button("Login")
if button:
    if email == "alpha@gmail.com" and password == "Mahagama@123":
        st.balloons()
        st.success("Login successful, Yo you have cracked the password")
        st.write(gender)
    else :
        st.error("password or email is incorrect")

file = st.file_uploader("Upload a csv file:")

if file is not None:
    df = pd.read_csv(file)
    st.dataframe(df.describe())

