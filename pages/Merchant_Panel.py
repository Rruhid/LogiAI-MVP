import streamlit as st
import pandas as pd
import plotly.express as px
import os
import psycopg2

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

 
import extra_streamlit_components as stx
cookie_manager = stx.CookieManager()


# 1. Настройка страницы
st.set_page_config(page_title="AI Data Agent (Pro)", layout="wide")



st.markdown("""
<style>
    /* Универсальный и читаемый стиль для инлайн-кода (тегов в тексте) */
    code {
        background-color: rgba(150, 150, 150, 0.2) !important;
        color: #ff4b4b !important; /* фирменный красный цвет Streamlit или поставьте #2e8540 для зеленого */
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)




def get_db_connection():
  # Берем строку подключения из секретов
  db_url = st.secrets["postgres"]["connection_string"]
  return psycopg2.connect(db_url)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_history_logs (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255),
                role VARCHAR(50),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS datasets_log (
                id SERIAL PRIMARY KEY,
                user_email VARCHAR(255),
                file_name VARCHAR(255),
                row_count INT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

init_db()

def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("pages/style.css")

def get_user_from_db(email):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email, merchant_name, role, subscription_plan FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {
                "email": row[0],
                "merchant_name": row[1],
                "role": row[2],
                "subscription_plan": row[3]
            }
    except Exception:
        pass
    return None

# --- ИСПРАВЛЕННАЯ БЕЗОПАСНАЯ ПРОВЕРКА СЕССИИ И СМЕНЫ АККАУНТА ---
query_params = st.query_params
url_email = query_params.get("user")
current_session_email = st.session_state.get("user_email")

# Если передан новый email в URL — принудительно сбрасываем старую сессию и историю
if url_email and url_email != current_session_email:
    user_data = get_user_from_db(url_email)
    if user_data:
        st.session_state.logged_in = True
        st.session_state.user_email = url_email
        st.session_state.user_role = user_data["role"]
        st.session_state.merchant_name = user_data["merchant_name"]
        st.session_state.current_plan = user_data.get("subscription_plan", "Starter")
        
        # Полный сброс истории и файлов для изоляции аккаунтов
        st.session_state.messages = []
        st.session_state.messages_owner = url_email
        st.session_state.stored_df = None
        st.session_state.stored_filename = ""
        
        st.query_params.clear()
        st.rerun()
    else:
        st.warning("⚠️ User not found in database.")
        st.stop()

# Если сессия вообще не активна
if not st.session_state.get("logged_in", False):
    if url_email:
        user_data = get_user_from_db(url_email)
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user_email = url_email
            st.session_state.user_role = user_data["role"]
            st.session_state.merchant_name = user_data["merchant_name"]
            st.session_state.current_plan = user_data.get("subscription_plan", "Starter")
            st.session_state.messages = []
            st.session_state.messages_owner = url_email
            st.query_params.clear()
        else:
            st.warning("⚠️ User not found in database.")
            st.stop()
    else:
        st.warning("⚠️ Please log in first (from the Login page).")
        st.stop()

# Очищаем лишние параметры в URL (например, после F5)
if "user" in st.query_params:
    st.query_params.clear()

current_role = st.session_state.get("user_role", "merchant")
current_merchant = st.session_state.get("merchant_name", "Admin Panel")
user_email = st.session_state.get("user_email", "user@example.com")

# Инициализация стейта для ключа и файла
if "gemini_key_input" not in st.session_state:
    st.session_state.gemini_key_input = ""
if "stored_df" not in st.session_state:
    st.session_state.stored_df = None
if "stored_filename" not in st.session_state:
    st.session_state.stored_filename = ""

# Сайдбар
st.sidebar.markdown(f"""
<div class="user-profile-card">
    <div class="user-profile-title">Management Menu</div>
    <div class="user-info-row">
        <span class="user-icon">👤</span>
        <div class="user-text">
            <span class="user-label">User</span>
            <span class="user-value">{user_email}</span>
        </div>
    </div>
    <div class="user-info-row" style="margin-top: 8px;">
        <span class="user-icon">🏢</span>
        <div class="user-text">
            <span class="user-label">Partner</span>
            <span class="partner-badge">{current_merchant}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation:", ["📊 Overview (Dashboard)", "🤖 AI Analyst"])

def update_gemini_key():
    st.session_state.gemini_key_input = st.session_state.temp_gemini_key

gemini_key = st.sidebar.text_input(
    "Enter Gemini API Key", 
    type="password", 
    value=st.session_state.gemini_key_input,
    key="temp_gemini_key",
    on_change=update_gemini_key
)

if gemini_key:
    st.session_state.gemini_key_input = gemini_key
else:
    gemini_key = st.session_state.gemini_key_input

if st.sidebar.button("🚪 Log Out"):
    # Безопасное удаление куки (проверяем, есть ли она вообще перед удалением)
    try:
        if cookie_manager.get("user_email") is not None:
            cookie_manager.delete("user_email")
    except Exception:
        pass
    
    # Сбрасываем стейт
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.messages = []
    st.session_state.stored_df = None
    st.session_state.stored_filename = ""
    st.query_params.clear()
    st.rerun()
    
st.sidebar.markdown("---")
st.title("🚀 Business Analytics Agent (AI-Powered)")

uploaded_file = st.sidebar.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

# Если загружен новый файл — считываем и сохраняем в session_state
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.stored_df = pd.read_csv(uploaded_file)
        else:
            st.session_state.stored_df = pd.read_excel(uploaded_file)
            
        st.session_state.stored_filename = uploaded_file.name
        
        # Записываем лог в базу
        if st.session_state.get("last_uploaded_file") != uploaded_file.name:
            st.session_state.last_uploaded_file = uploaded_file.name
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO datasets_log (user_email, file_name, row_count) VALUES (%s, %s, %s)", 
                            (user_email, uploaded_file.name, len(st.session_state.stored_df)))
                conn.commit()
                cur.close()
                conn.close()
            except Exception:
                pass
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Основная переменная df для работы на страницах
df = st.session_state.stored_df

# Проверка наличия файла
if df is not None:
    st.sidebar.success(f"📁 Active: {st.session_state.stored_filename}")
    
    # Страница 1: Дашборд
    if page == "📊 Overview (Dashboard)":
        st.subheader("Data Overview")
        st.dataframe(df.head(20), use_container_width=True)
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            x_col = st.selectbox("X axis", df.columns, key="overview_x_axis")
            y_col = st.selectbox("Y axis", numeric_cols, key="overview_y_axis")
            st.plotly_chart(px.bar(df, x=x_col, y=y_col), use_container_width=True)

    # Страница 2: AI-Аналитика
    elif page == "🤖 AI Analyst":
        st.subheader("🤖 Chat with AI Analyst")
        
        # Надежная загрузка истории чата строго под текущего пользователя
        if "messages" not in st.session_state or st.session_state.get("messages_owner") != user_email:
            st.session_state.messages = []
            st.session_state.messages_owner = user_email
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT role, content FROM chat_history_logs WHERE user_email = %s ORDER BY id ASC", (user_email,))
                rows = cur.fetchall()
                for r, c in rows:
                    if r == "user":
                        st.session_state.messages.append({"role": "user", "content": c})
                    elif r == "assistant":
                        st.session_state.messages.append({"role": "assistant", "content": c, "ai_text": c, "result": None})
                cur.close()
                conn.close()
            except Exception:
                pass
        
        # Отрисовка истории с вашей логикой разделения графиков и скаляров
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.markdown(message["content"])
                elif message["role"] == "assistant":
                    if message.get("ai_text"):
                        st.markdown(message["ai_text"])
                    
                    res = message.get("result")
                    if res is not None:
                        is_real_table = isinstance(res, pd.DataFrame) and len(res.columns) >= 2 and len(res) > 1
                        
                        if is_real_table:
                            selected_views = st.multiselect(
                                "Display elements:",
                                ["Bar Chart", "Line Chart", "Pie Chart", "Data Table"],
                                default=["Bar Chart", "Line Chart", "Pie Chart", "Data Table"],
                                key=f"msg_filter_{idx}"
                            )
                            
                            cols = res.columns.tolist()
                            fig_b = px.bar(res, x=cols[0], y=cols[1])
                            fig_l = px.line(res, x=cols[0], y=cols[1], markers=True)
                            fig_p = px.pie(res, names=cols[0], values=cols[1])
                            
                            tabs_list = []
                            if "Bar Chart" in selected_views: tabs_list.append("📊 Bar Chart")
                            if "Line Chart" in selected_views: tabs_list.append("📈 Line Chart")
                            if "Pie Chart" in selected_views: tabs_list.append("🥧 Pie Chart")
                            if "Data Table" in selected_views: tabs_list.append("📋 Data Table")
                            
                            if tabs_list:
                                tbs = st.tabs(tabs_list)
                                t_idx = 0
                                if "Bar Chart" in selected_views:
                                    with tbs[t_idx]: st.plotly_chart(fig_b, use_container_width=True, key=f"bar_{idx}")
                                    t_idx += 1
                                if "Line Chart" in selected_views:
                                    with tbs[t_idx]: st.plotly_chart(fig_l, use_container_width=True, key=f"line_{idx}")
                                    t_idx += 1
                                if "Pie Chart" in selected_views:
                                    with tbs[t_idx]: st.plotly_chart(fig_p, use_container_width=True, key=f"pie_{idx}")
                                    t_idx += 1
                                if "Data Table" in selected_views:
                                    with tbs[t_idx]: st.dataframe(res, use_container_width=True, hide_index=True)
                        else:
                            if isinstance(res, pd.DataFrame):
                                clean_val = res.iloc[0, 0] if res.size > 0 else str(res)
                                st.markdown(str(clean_val))
                            elif isinstance(res, pd.Series):
                                clean_val = res.iloc[0] if len(res) > 0 else str(res)
                                st.markdown(str(clean_val))
                            else:
                                st.markdown(str(res))

        # Ввод нового запроса
        if prompt := st.chat_input("Type your query regarding the data..."):
            if not gemini_key:
                st.error("Please enter the API key!")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO chat_history_logs (user_email, role, content) VALUES (%s, %s, %s)", 
                                (user_email, "user", prompt))
                    conn.commit()
                    cur.close()
                    conn.close()
                except Exception:
                    pass
                    
                st.rerun()

        # Генерация ответа ассистента с вашим системным промптом
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            last_prompt = st.session_state.messages[-1]["content"]
            
            with st.chat_message("assistant"):
                with st.spinner("Analyst is writing and executing the answer:"):
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-3.6-flash", 
                            google_api_key=gemini_key,
                            temperature=0.1
                        )
                        
                        df_info = df.dtypes.to_string()
                        df_head = df.head(3).to_string()
                        structure_context = f"\n\nTABLE STRUCTURE:\n{df_info}\n DATA SAMPLE\n{df_head}"
                        
                        system_prompt = f"""
                        You are a professional, helpful, and friendly senior data analyst expert talking directly to a business stakeholder. Your goal is to answer the user's query precisely and naturally.

                        RULES:
                        1. DETECT LANGUAGE: Always respond in the exact same language that the user used in their latest question (e.g., if the user asks in English, reply in English; if in Azerbaijani, reply in Azerbaijani; if in Russian, reply in Russian).
                        2. HUMAN-LIKE TONE (CRITICAL): Write a friendly, conversational, and natural business commentary in text *before* the code block. Talk like a real colleague or expert analyst (e.g., "По результатам анализа данных лидером по количеству смен является..." или "Based on the data analysis, the top city is..."). Never sound like a cold robot.
                        3. Then write the precise Python code for the calculation inside a ```python ... ``` block.
                        4. Store the final output variable strictly as 'result' (can be a DataFrame, Series, or a single number/string).
                        5. If the result is a table, use .reset_index() and keep clean column names.
                        6. NOTE: Even if the user asks in English, Azerbaijani, or another language, the actual column names in the provided dataset might be in Russian (e.g., 'Тип_авто', 'Общее кол-во доставленных заказов'). Map the semantic meaning to the actual dataset columns intelligently. Never invent non-existent column names like 'status'.
                        7. SUPERLATIVE QUESTIONS: If the user asks for a single best, most popular, maximum, or minimum item, calculate and return strictly the final scalar value in the 'result' variable (e.g., a string like "Москва" or a number), while your conversational text above fully presents the answer nicely to the user.
                        8. NO CODE ANNOUNCEMENTS: Never write phrases like "Here is the Python code to compute this result", "Here is the code", or any technical preamble right before the code block. Transition directly from your conversational explanation into the ```python ... ``` block.
                        {structure_context}
                        """
                        
                        # Собираем историю диалога для LangChain (всё, кроме последнего сообщения пользователя)
                        chat_history_objs = []
                        for msg in st.session_state.messages[:-1]:
                            role = msg.get("role")
                            content = msg.get("content") or msg.get("ai_text", "")
                            if role == "user":
                                chat_history_objs.append(HumanMessage(content=content))
                            elif role == "assistant":
                                chat_history_objs.append(AIMessage(content=content))

                        prompt_template = ChatPromptTemplate.from_messages([
                            ("system", system_prompt),
                            MessagesPlaceholder(variable_name="chat_history"),
                            ("human", "Sual: {user_query}")
                        ])
                        
                        chain = prompt_template | llm | StrOutputParser()
                        full_text = chain.invoke({
                            "user_query": last_prompt,
                            "chat_history": chat_history_objs
                        })
                        
                        if "```python" in full_text and "```" in full_text.split("```python")[1]:
                            ai_text = full_text.split("```python")[0].strip()
                            code = full_text.split("```python")[1].split("```")[0].strip()
                        else:
                            ai_text = "Results of your query:"
                            code = full_text.replace("```", "").strip()

                        local_scope = {"df": df, "pd": pd, "result": None}
                        exec(code, {}, local_scope)
                        result = local_scope.get("result")
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": ai_text,
                            "ai_text": ai_text,
                            "result": result
                        })
                        
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("INSERT INTO chat_history_logs (user_email, role, content) VALUES (%s, %s, %s)", 
                                        (user_email, "assistant", ai_text))
                            conn.commit()
                            cur.close()
                            conn.close()
                        except Exception:
                            pass
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Calculation error: {e}")
else:
    st.info("📁 Please upload a file from the left sidebar.")