import streamlit as st
import base64
import psycopg2
import os

st.set_page_config(page_title="Billing & Tariflər", page_icon="💳", layout="wide")

def get_db_connection():
  # Берем строку подключения из секретов
  db_url = st.secrets["postgres"]["connection_string"]
  return psycopg2.connect(db_url)

def get_user_plan_from_db(email):
    if not email:
        return "Starter"
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT subscription_plan FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        print(f"Error fetching plan: {e}")
    return "Starter"

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

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Кодирование фона
try:
    img_base64 = get_base64_image("background.avif")
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
except Exception:
    pass

# Подключаем CSS
try:
    with open("pages/style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

is_logged_in = st.session_state.get("logged_in", False)
user_email = st.session_state.get("user_email", None)

st.markdown("""
<style>
    .pricing-card {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        text-align: center;
        border-top: 4px solid #0066cc;
        height: 100%;
    }
    .price-num { font-size: 32px; font-weight: bold; color: #222; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

st.title("💳 Subscription and Pricing Plans (Billing)")
st.markdown('<p class="swing-text"> Choose the right plan according to the scale of your business and expand your capabilities.</p>', unsafe_allow_html=True)

# Получаем актуальный план
if is_logged_in and user_email:
    current_plan = get_user_plan_from_db(user_email)
    st.session_state.current_plan = current_plan
else:
    current_plan = st.session_state.get("current_plan", "Starter")

st.info(f"Your current active plan: **{current_plan}**")

col1, col2, col3 = st.columns(3)

# Универсальная функция для отрисовки карточки и кнопок
def render_pricing_column(plan_name, price, description, features, stripe_url, key_suffix, is_popular=False):
    border_style = 'border: 2px solid #10b981 !important;' if is_popular else ''
    
    st.markdown(f"""
    <div class="pricing-card" style="height: 520px; display: flex; flex-direction: column; justify-content: space-between; {border_style}">
        <div>
            <h3>{plan_name}</h3>
            <p>{description}</p>
            <div class="price-num">{price} $ <span style="font-size:14px; color:gray;">/mo</span></div>
            <hr>
            {''.join([f'<p>{f}</p>' for f in features])}
        </div>
    """, unsafe_allow_html=True)
    
    if is_logged_in:
        # Кнопка обновляет базу данных при клике
        if st.button(f"Select {plan_name}", key=f"btn_{key_suffix}", use_container_width=True):
            update_user_plan_in_db(user_email, plan_name)
            st.session_state.current_plan = plan_name
            st.rerun()  # Мгновенно перезагружаем страницу, чтобы обновить интерфейс
            
        # Показываем ссылку на оплату ТОЛЬКО для текущего выбранного/активного плана
        if current_plan == plan_name:
            st.markdown(f"""
                <a href="{stripe_url}" target="_blank" style="display: block; text-align: center; background-color: #0066cc; color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 8px;">
                    Proceed to Payment ➔
                </a>
            """, unsafe_allow_html=True)
    else:
        if st.button(f"Get {plan_name}", key=f"btn_unlogged_{key_suffix}", use_container_width=True):
            st.session_state.pending_plan = plan_name
            st.switch_page("pages/Login.py")
            
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    render_pricing_column(
        "Starter", "19", "For small shops and testing",
        ["✅ 1,000 row limit", "✅ 50 AI queries / mo", "✅ Basic AI analytics"],
        "https://buy.stripe.com/test_9B69ATehi8UseJ667204800", "starter"
    )

with col2:
    render_pricing_column(
        "Standard", "79", "For growing companies",
        ["✅ 25,000 row limit", "✅ 300 AI queries / mo", "✅ Full AI & Python Code"],
        "https://buy.stripe.com/test_7sY14n8WYgmUdF27b604801", "standard", is_popular=True
    )

with col3:
    render_pricing_column(
        "Pro Enterprise", "249", "For networks & large logistics",
        ["✅ 100,000+ row limit", "✅ 1,000 AI queries / mo", "✅ Priority support & custom approach"],
        "https://buy.stripe.com/test_dRmdR9c9a5Ig44sfHC04802", "pro"
    )

st.markdown("---")
if st.button("🏠 Back to Home"):
    st.switch_page("Main.py")