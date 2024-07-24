import streamlit as st
import requests
from datetime import datetime

# API URLs
SIGNUP_URL = 'http://localhost:8000/signup'
LOGIN_URL = 'http://localhost:8000/login'
PROTECTED_URL = 'http://localhost:8000/protected'

def signup(username, email, password, date_of_birth):
    response = requests.post(SIGNUP_URL, json={
        'username': username,
        'email': email,
        'password': password,
        'date_of_birth': date_of_birth.strftime('%Y-%m-%d')
    })
    if response.status_code == 201:
        st.success('User created successfully')
    else:
        st.error(f'Error creating user: {response.text}')

def login(identifier, password):
    response = requests.post(LOGIN_URL, json={
        'identifier': identifier,
        'password': password
    })
    if response.status_code == 200:
        token = response.json().get('token')
        st.session_state.token = token
        st.session_state.logged_in = True  # Track login status
        st.success('Login successful!')
    else:
        st.error(f'Error logging in: {response.text}')

def access_protected_route():
    if 'token' not in st.session_state:
        st.error('You need to log in first')
        return

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(PROTECTED_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        st.write("Protected data:", data)
    else:
        st.error("Failed to access protected route.")

def home_page():
    st.title('Home Page')
    st.write("Welcome to the home page!")
    st.button('Access Protected Route', on_click=access_protected_route)

# Streamlit interface
st.title('User Authentication')

# Sidebar for navigation
st.sidebar.title('Navigation')
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

options = ['Signup', 'Login']
if st.session_state.logged_in:
    options.append('Home')
    options.append('Access Protected Route')

option = st.sidebar.selectbox('Choose an option', options)

if option == 'Signup':
    st.header('Signup')
    with st.form(key='signup_form'):
        username = st.text_input('Username')
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
        date_of_birth = st.date_input('Date of Birth')

        submit_button = st.form_submit_button('Signup')
        if submit_button:
            if username and email and password and date_of_birth:
                signup(username, email, password, date_of_birth)
            else:
                st.error('Please fill all fields')

elif option == 'Login':
    st.header('Login')
    with st.form(key='login_form'):
        identifier = st.text_input('Username or Email')
        password = st.text_input('Password', type='password')

        login_button = st.form_submit_button('Login')
        if login_button:
            if identifier and password:
                login(identifier, password)
            else:
                st.error('Please fill all fields')

elif option == 'Home':
    home_page()

elif option == 'Access Protected Route':
    st.header('Protected Route')
    if st.button('Access'):
        access_protected_route()
