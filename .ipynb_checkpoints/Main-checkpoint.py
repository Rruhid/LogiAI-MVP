import streamlit as st


# Функция для импорта внешнего CSS файла
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Подключаем наш style.css
load_css("pages/style.css")


 



st.set_page_config(
    page_title="LogiAI - Süni İntellekt Logistika Platforması",
    page_icon="🚀",
    layout="wide"
)

 

# Профессиональный SaaS-дизайн (стиль чистого интерфейса)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .hero-section {
        padding: 40px 0px 40px 0px;
        text-align: center;
    }
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 20px;
    }
    .hero-subtitle {
        font-size: 20px;
        color: #64748b;
        max-width: 700px;
        margin: 0 auto 40px auto;
        line-height: 1.5;
    }
    .feature-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        height: 100%;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .cta-box {
        background: #f8fafc;
        padding: 40px;
        border-radius: 16px;
        text-align: center;
        margin-top: 60px;
        border: 1px solid #e2e8f0;
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
        if st.button("Kabinetə Keç ➔", type="primary", use_container_width=True):
            st.switch_page("pages/Merchant_Panel.py")
    else:
        if st.button("Daxil ol", type="primary", use_container_width=True):
            st.switch_page("pages/Login.py")

# Главный блок (Hero)
st.markdown('<div class="hero-section" style="text-align: center !important;"><div class="hero-badge">✨ AI-Powered Logistics Intelligence</div><h1 class="hero-title">Logistika Məlumatlarınızı <span class="typing-text">Süni İntellektlə</span> İdarə Edin</h1><div style="max-width: 720px; margin: 0 auto; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 10px; overflow: hidden;"><div style="display: flex; width: max-content; animation: scrollMarquee 25s linear infinite;"><span style="font-size: 14px !important; color: #cbd5e1 !important; font-weight: 500; white-space: nowrap; padding-right: 40px;">📌 Mürəkkəb Excel cədvəlləri ilə vaxt itirməyin! &nbsp;&nbsp;•&nbsp;&nbsp; ⚡ Sadəcə faylınızı yükləyin, süni intellekt saniyələr ərzində dəqiq hesabatlar və qrafiklər versin.</span><span style="font-size: 14px !important; color: #cbd5e1 !important; font-weight: 500; white-space: nowrap; padding-right: 40px;">📌 Mürəkkəb Excel cədvəlləri ilə vaxt itirməyin! &nbsp;&nbsp;•&nbsp;&nbsp; ⚡ Sadəcə faylınızı yükləyin, süni intellekt saniyələr ərzində dəqiq hesabatlar və qrafiklər versin.</span></div></div></div>', unsafe_allow_html=True)
# Карточки возможностей
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>⚡ Sürətli Təhlil</h3>
        <p>Excel və ya CSV formatındakı daşınma və kuryer məlumatlarınızı dərhal sistemə yükləyin.</p>
    </div>
    """, unsafe_allow_html=True)

 

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 Python Code AI</h3>
        <p>Ana dildə sual verin, AI dəqiq rəqəmləri Python ilə hesablasın.</p>
    </div>
    """, unsafe_allow_html=True)


with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>💳 Çevik Paketlər</h3>
        <p>Kiçik mağazalardan tutmuş böyük logistik şəbəkələərə qədər hər kəsə uyğun billing planları.</p>
    </div>
    """, unsafe_allow_html=True)

# Блок призыва к действию
st.markdown("""
<div class="cta-box">
    <h3>Biznesinizi optimallaşdırmağa hazırsınız?</h3>
    <p>Sistemə daxil olun və ya tarfilərimizlə tanış olun.</p>
</div>
""", unsafe_allow_html=True)

# Кнопки внизу
st.write("") # отступ
col_c1, col_c2 = st.columns([1, 1], gap="medium")
with col_c1:
    if st.button("🔑 Sistemə Giriş Et", use_container_width=True):
        st.switch_page("pages/Login.py")
with col_c2:
    if st.button("💳 Tarifləri Göstər (Billing)", use_container_width=True):
        st.switch_page("pages/Billing.py")