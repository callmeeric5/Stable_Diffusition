import streamlit as st
from utils import init_session_state, signup, login, logout

st.set_page_config(page_title="Image Generation App", layout="wide")

init_session_state()

def main():
    st.title("Welcome to the Image Generation App")

    if not st.session_state.logged_in:
        login_signup()
    else:
        logged_in_view()

def login_signup():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.header("Sign Up")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        email = st.text_input('Email', key='email')
        date_of_birth = st.date_input('Date of Birth',key='date_of_birth')

        if st.button("Sign Up"):
            if signup(new_username, new_password, email, date_of_birth):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists")

def logged_in_view():
    st.write(f"Welcome, {st.session_state.current_user}!")
    st.write("Use the sidebar to navigate between the Generate and Gallery pages.")

    if st.button("Logout"):
        logout()
        st.rerun()

    st.sidebar.success("Select a page above.")

if __name__ == "__main__":
    main()