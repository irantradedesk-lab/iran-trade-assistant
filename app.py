
import streamlit as st
from groq import Groq
from tavily import TavilyClient
import google.generativeai as genai

# --- راه‌اندازی کلاینت‌ها ---
groq_client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://groq-proxy.irantradedesk.workers.dev/"
)
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


def ask_groq(messages, model_name="openai/gpt-oss-120b"):
    response = groq_client.chat.completions.create(
        messages=messages,
        model=model_name
    )
    return response.choices[0].message.content


def ask_gemini(messages, model_name="gemini-3.8-flash"):
    gemini_model = genai.GenerativeModel(model_name)
    history = []
    for msg in messages:
        if msg["role"] == "system":
            continue
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    response = gemini_model.generate_content(history)
    return response.text


# --- رابط کاربری Streamlit ---
st.set_page_config(page_title="Iran Trade Services", page_icon="🌍", layout="wide")
st.title("🌍 Iran Trade Services")
st.caption("دستیار هوشمند تجارت بین‌الملل")

with st.sidebar:
    st.header("تنظیمات")
    provider = st.radio("ارائه‌دهنده مدل:", ("Groq (سریع)", "Gemini (پایدار)"))

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "تو دستیار شخصی من هستی. فارسی، دقیق و مفید پاسخ بده."}
    ]
if "display" not in st.session_state:
    st.session_state.display = []

for msg in st.session_state.display:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("سوالت رو بنویس...")

if user_input:
    st.session_state.display.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("در حال فکر کردن..."):
            try:
                search = tavily_client.search(query=user_input, max_results=5)
                context = "\n".join([f"- {r['title']}: {r['content']}" for r in search['results']])
                full_msg = f"سوال: {user_input}\n\nنتایج جستجو:\n{context}\n\nپاسخ فارسی و دقیق بده."
            except Exception:
                full_msg = user_input

            st.session_state.messages.append({"role": "user", "content": full_msg})

            try:
                if provider == "Groq (سریع)":
                    answer = ask_groq(st.session_state.messages)
                else:
                    answer = ask_gemini(st.session_state.messages)
            except Exception as e:
                answer = f"خطا در پاسخ‌دهی: {str(e)}"

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.display.append({"role": "assistant", "content": answer})
            st.write(answer)
