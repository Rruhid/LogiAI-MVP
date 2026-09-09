import streamlit as st
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Кодируем картинку
img_base64 = get_base64_image("background.avif")

# Вставляем через base64 в стили
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



# Функция для импорта внешнего CSS файла
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Подключаем наш style.css
load_css("pages/style.css")


 



st.set_page_config(
    page_title="LogiAI - AI Business Intelligence",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Фоновое изображение с темным фильтром */
    .stApp {
        background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("background.avif");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .hero-section {
        padding: 40px 0px 40px 0px;
        text-align: center;
    }
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        font-size: 20px;
        color: #94a3b8;
        max-width: 700px;
        margin: 0 auto 40px auto;
        line-height: 1.5;
    }
    
    /* Эффект стекла для карточек (Glassmorphism) */
    .feature-card {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(12px);
        padding: 30px;
        border-radius: 16px;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        height: 100%;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        border-color: rgba(16, 185, 129, 0.8);
    }
    .cta-box {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(12px);
        padding: 40px;
        border-radius: 16px;
        text-align: center;
        margin-top: 60px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

 
# Инициализация сессии
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Верхняя панель навигации
col_logo, col_btn = st.columns([4, 1])
with col_logo:
    st.markdown("### 🚀 LogiAI Platform")
with col_btn:
    if st.session_state.logged_in:
        if st.button("🔑 System Login ➔", type="primary", use_container_width=True):
            st.switch_page("pages/Merchant_Panel.py")
    else:
        if st.button("🔑 System Login ➔", type="primary", use_container_width=True):
            st.switch_page("pages/Login.py")

# Главный блок (Hero)
st.markdown('<div class="hero-section" style="text-align: center !important;"><div class="hero-badge">✨ AI-Powered Logistics Intelligence (LangChain & LLM) </div><h1 class="hero-title">Manage Your Data with <span class="typing-text">Artificial Intelligence</span></h1><div style="max-width: 720px; margin: 0 auto; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 10px; overflow: hidden;"><div style="display: flex; width: max-content; animation: scrollMarquee 25s linear infinite;"><span style="font-size: 14px !important; color: #cbd5e1 !important; font-weight: 500; white-space: nowrap; padding-right: 40px;">📌 Don\'t waste time with complex Excel spreadsheets! &nbsp;&nbsp;•&nbsp;&nbsp; ⚡ Just upload your file, and AI will provide precise reports and charts in seconds.</span><span style="font-size: 14px !important; color: #cbd5e1 !important; font-weight: 500; white-space: nowrap; padding-right: 40px;">📌 Don\'t waste time with complex Excel spreadsheets! &nbsp;&nbsp;•&nbsp;&nbsp; ⚡ Just upload your file, and AI will provide precise reports and charts in seconds.</span></div></div></div>', unsafe_allow_html=True)

 

# Карточки возможностей
col1, col2, col3 = st.columns(3, gap="large")

# Замени стемминг колонок Streamlit на этот адаптивный HTML-контейнер
st.markdown("""
<div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; align-items: stretch; margin-top: 20px;">
    <div class="feature-card" style="flex: 1; min-width: 300px; max-width: 360px; min-height: 230px; display: flex; flex-direction: column; justify-content: space-between;">
        <h3>⚡ Fast Analysis</h3>
        <p>Instantly upload your transport and courier data in Excel or CSV format for rapid analysis.</p>
    </div>
    <div class="feature-card" style="flex: 1; min-width: 300px; max-width: 360px; min-height: 230px; display: flex; flex-direction: column; justify-content: space-between;">
        <h3>🤖 Python Code AI</h3>
        <p>Ask complex operational questions in plain language and let AI agent calculate precise figures.</p>
    </div>
    <div class="feature-card" style="flex: 1; min-width: 300px; max-width: 360px; min-height: 230px; display: flex; flex-direction: column; justify-content: space-between;">
        <h3>💳 Flexible Plans</h3>
        <p>Choose enterprise billing tiers seamlessly tailored to match operational scales of any business size.</p>
    </div>
</div>
""", unsafe_allow_html=True)


# Блок призыва к действию
st.markdown("""
<div class="cta-box">
    <h3>Ready to Optimize Your Business?</h3>
    <p>Log in to the system or check out our pricing plans.</p>
</div>
""", unsafe_allow_html=True)

# Кнопки внизу
st.write("") # отступ
col_c1, col_c2 = st.columns([1, 1], gap="medium")
with col_c1:
    if st.button("🔑 System Login", use_container_width=True):
        st.switch_page("pages/Login.py")
with col_c2:
    if st.button("💳 Show Pricing (Billing)", use_container_width=True):
        st.switch_page("pages/Billing.py")