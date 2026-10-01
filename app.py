
import streamlit as st
from groq import Groq
from tavily import TavilyClient

groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])

st.set_page_config(page_title="Iran Trade Services", page_icon="🌍", layout="wide")
st.title("🌍 Iran Trade Services")
st.caption("دستیار هوشمند تجارت بین‌الملل")

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
            except:
                full_msg = user_input
            
            st.session_state.messages.append({"role": "user", "content": full_msg})
            response = groq_client.chat.completions.create(
                messages=st.session_state.messages,
                model="openai/gpt-oss-120b"
            )
            answer = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.display.append({"role": "assistant", "content": answer})
            st.write(answer)
