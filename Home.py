import streamlit as st

# Safety gate
import streamlit_authenticator as stauth
import copy

st.set_page_config(
    page_title="Access Control System",
    page_icon="🔐",
    layout="wide"
)

# 🔑 Convert secrets to mutable dict
config = {
    "credentials": {
        "usernames": {
            user: dict(st.secrets["credentials"]["usernames"][user])
            for user in st.secrets["credentials"]["usernames"]
        }
    },
    "cookie": dict(st.secrets["cookie"]),
}

# Authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

st.title("🏠 Access Control")

login_result = authenticator.login(key="Login", location="main")

if login_result is None:
    st.stop()

name, auth_status, username = login_result

if auth_status is False:
    st.error("❌ Username/password is incorrect")
    st.stop()

if auth_status is None:
    st.warning("Please enter your username and password")
    st.stop()

# ✅ Authenticated user
st.success(f"Welcome {name}")

# ✅ Redirect logic
if username == "scanner":
    st.switch_page("pages/1_📷_Scanner_App.py")
elif username == "viewer":
    st.switch_page("pages/2_📊_POB_Dashboard")
