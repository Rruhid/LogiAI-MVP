import streamlit as st 
import os 
import hashlib 
import secrets 
import base64 
import psycopg2 
import datetime 
import extra_streamlit_components as stx 
 
st.set_page_config(page_title="Login / Register", page_icon="🔐", layout="centered") 
 
# --- Инициализация менеджера кук --- 
cookie_manager = stx.CookieManager() 
 
# --- ПОДКЛЮЧЕНИЕ К POSTGRESQL --- 
def get_db_connection():
  # Берем строку подключения из секретов
  db_url = st.secrets["postgres"]["connection_string"]
  return psycopg2.connect(db_url)
 
def hash_password(password, salt=None): 
    if not salt: 
        salt = secrets.token_hex(16) 
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest() 
    return pwd_hash, salt 
 
def verify_password(stored_password, stored_salt, provided_password): 
    pwd_hash, _ = hash_password(provided_password, stored_salt) 
    return pwd_hash == stored_password 
 
def get_user_from_db(email): 
    try: 
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute("SELECT email, password_hash, salt, merchant_name, role, subscription_plan FROM users WHERE email = %s", (email,)) 
        row = cur.fetchone() 
        cur.close() 
        conn.close() 
        if row: 
            return { 
                "email": row[0], 
                "password_hash": row[1], 
                "salt": row[2], 
                "merchant_name": row[3], 
                "role": row[4], 
                "subscription_plan": row[5] 
            } 
    except Exception as e: 
        st.error(f"Database connection error: {e}") 
    return None 
 
def save_user_to_db(email, password, merchant_name, role="merchant", initial_plan="Starter"): 
    pwd_hash, salt = hash_password(password) 
    try: 
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute( 
            "INSERT INTO users (email, password_hash, salt, merchant_name, role, subscription_plan) VALUES (%s, %s, %s, %s, %s, %s)", 
            (email, pwd_hash, salt, merchant_name, role, initial_plan) 
        ) 
        conn.commit() 
        cur.close() 
        conn.close() 
        return True 
    except Exception as e: 
        st.error(f"Error saving user: {e}") 
        return False 
 
def update_user_plan_in_db(email, new_plan): 
    try: 
        conn = get_db_connection() 
        cur = conn.cursor() 
        cur.execute("UPDATE users SET subscription_plan = %s WHERE email = %s", (new_plan, email)) 
        conn.commit() 
        cur.close() 
        conn.close() 
        return True 
    except Exception as e: 
        print(f"Database error updating plan: {e}") 
        return False 
 
# --- АВТОМАТИЧЕСКОЕ ВОССТАНОВЛЕНИЕ СЕССИИ ИЗ КУКИ (F5 / ПЕРЕЗАГРУЗКА) --- 
if not st.session_state.get("logged_in"): 
    saved_email = cookie_manager.get(cookie="user_email") 
    if saved_email: 
        user_data = get_user_from_db(saved_email) 
        if user_data: 
            st.session_state.logged_in = True 
            st.session_state.user_email = saved_email 
            st.session_state.user_role = user_data["role"] 
            st.session_state.current_plan = user_data.get("subscription_plan", "Starter") 
            st.session_state.merchant_name = user_data["merchant_name"] 
            st.switch_page("pages/Merchant_Panel.py") 
 
def get_base64_image(image_path): 
    if os.path.exists(image_path): 
        with open(image_path, "rb") as img_file: 
            return base64.b64encode(img_file.read()).decode() 
    return "" 
 
img_base64 = get_base64_image("background.avif") 
if img_base64: 
    st.markdown(f""" 
    <style> 
        .stApp {{ 
            background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("data:image/avif;base64,{img_base64}") !important; 
            background-size: cover !important; 
            background-position: center !important; 
            background-attachment: fixed !important; 
        }} 
    </style> 
    """, unsafe_allow_html=True) 
 
def load_css(file_name): 
    if os.path.exists(file_name): 
        with open(file_name, "r", encoding="utf-8") as f: 
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True) 
 
load_css("pages/style.css") 
 
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False 
 
st.markdown("<h2 style='text-align: center;'>🔐 LogiAI System Login (PostgreSQL)</h2>", unsafe_allow_html=True) 
 
auth_mode = st.radio("Select mode:", ["Login", "Register"], horizontal=True) 
 
if auth_mode == "Login": 
    with st.form("login_form"): 
        email = st.text_input("Email", placeholder="example@mail.com") 
        password = st.text_input("Password", type="password", placeholder="******") 
        submit = st.form_submit_button("Login", use_container_width=True) 
         
        if submit: 
            user_data = get_user_from_db(email) 
            if user_data and verify_password(user_data["password_hash"], user_data["salt"], password): 
                st.session_state.logged_in = True 
                st.session_state.user_role = user_data["role"] 
                st.session_state.user_email = email 
                st.session_state.merchant_name = user_data["merchant_name"] 
                 
                pending_plan = st.session_state.pop("pending_plan", None) 
                if pending_plan: 
                    update_user_plan_in_db(email, pending_plan) 
                    st.session_state.current_plan = pending_plan 
                else: 
                    st.session_state.current_plan = user_data.get("subscription_plan", "Starter") 
                 
                # Сохраняем куку на 7 дней, чтобы сессия не сбрасывалась при F5 
                cookie_manager.set("user_email", email, expires_at=datetime.datetime.now() + datetime.timedelta(days=7)) 
                 
                st.success("🚀 Successfully logged in! Redirecting to panel...") 
                st.switch_page("pages/Merchant_Panel.py") 
            else: 
                st.error("Invalid email or password!") 
 
else: 
    with st.form("register_form"): 
        st.markdown("### New Partner Registration") 
        reg_merc = st.text_input("Partner / Merchant Name", placeholder="Bravo") 
        reg_email = st.text_input("New Email", placeholder="merchant@baku.az") 
        reg_pass = st.text_input("Create Password", type="password", placeholder="******") 
        reg_pass_confirm = st.text_input("Confirm Password", type="password", placeholder="******") 
        reg_submit = st.form_submit_button("Register", use_container_width=True) 
         
        if reg_submit: 
            if not reg_email or not reg_pass or not reg_merc: 
                st.error("Please fill in all fields!") 
            elif reg_pass != reg_pass_confirm: 
                st.error("Passwords do not match!") 
            elif get_user_from_db(reg_email): 
                st.error("This email is already registered!") 
            else: 
                chosen_plan = st.session_state.pop("pending_plan", "Starter") 
                 
                if save_user_to_db(reg_email, reg_pass, reg_merc, role="merchant", initial_plan=chosen_plan): 
                    st.session_state.logged_in = True 
                    st.session_state.user_role = "merchant" 
                    st.session_state.user_email = reg_email 
                    st.session_state.merchant_name = reg_merc 
                    st.session_state.current_plan = chosen_plan 
                     
                    # Сохраняем куку на 7 дней для нового пользователя 
                    cookie_manager.set("user_email", reg_email, expires_at=datetime.datetime.now() + datetime.timedelta(days=7)) 
                     
                    st.success(f"🎉 Registration completed! Plan: {chosen_plan}. Redirecting...") 
                    st.switch_page("pages/Merchant_Panel.py")   