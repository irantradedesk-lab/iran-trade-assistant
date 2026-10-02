
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
    system_prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
            continue
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    
    if system_prompt:
        gemini_model = genai.GenerativeModel(
            model_name,
            system_instruction=system_prompt
        )
    
    response = gemini_model.generate_content(history)
    return response.text


def ask(messages, provider):
    if provider == "Groq (سریع)":
        return ask_groq(messages)
    else:
        return ask_gemini(messages)


# --- تنظیمات صفحه ---
st.set_page_config(page_title="Iran Trade Services", page_icon="🌍", layout="wide")
st.title("🌍 Iran Trade Services")
st.caption("دستیار هوشمند تجارت بین‌الملل")

# --- نوار کناری ---
with st.sidebar:
    st.header("⚙️ تنظیمات")
    provider = st.radio("موتور هوش مصنوعی:", ("Groq (سریع)", "Gemini (پایدار)"))
    st.markdown("---")
    mode = st.radio("حالت کار:", ("💬 چت آزاد", "📱 تولید محتوای شبکه‌های اجتماعی"))

# ============================================================
# حالت ۱: چت آزاد
# ============================================================
if mode == "💬 چت آزاد":
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
                    answer = ask(st.session_state.messages, provider)
                except Exception as e:
                    answer = f"خطا: {str(e)}"

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.display.append({"role": "assistant", "content": answer})
                st.write(answer)

# ============================================================
# حالت ۲: تولید محتوای شبکه‌های اجتماعی
# ============================================================
else:
    st.subheader("📱 استودیوی تولید محتوا")
    st.write("پلتفرم، نوع محتوا و موضوع رو انتخاب کن، من محتوای حرفه‌ای برات می‌سازم.")

    col1, col2 = st.columns(2)

    with col1:
        platform = st.selectbox(
            "🌐 پلتفرم:",
            ["LinkedIn", "Instagram", "Twitter/X", "Telegram", "Facebook", "WhatsApp Status"]
        )
        content_type = st.selectbox(
            "📝 نوع محتوا:",
            [
                "پست کامل",
                "کپشن کوتاه",
                "تقویم محتوای هفتگی",
                "ایده‌های محتوا (۱۰ ایده)",
                "سناریوی Reels",
                "هشتگ‌های مرتبط"
            ]
        )

    with col2:
        tone = st.selectbox(
            "🎭 لحن:",
            ["حرفه‌ای", "دوستانه", "آموزشی", "تبلیغاتی", "الهام‌بخش"]
        )
        language = st.selectbox(
            "🌍 زبان:",
            ["فارسی", "انگلیسی", "دوزبانه (فارسی + انگلیسی)"]
        )

    topic = st.text_area(
        "📌 موضوع یا توضیح:",
        placeholder="مثلاً: خدمات ترخیص کالا از گمرک، صادرات زعفران، مشاوره واردات از چین...",
        height=100
    )

    extra = st.text_area(
        "💡 توضیحات اضافه (اختیاری):",
        placeholder="هر نکته، هدف، مخاطب خاص یا جزئیاتی که می‌خوای رعایت بشه",
        height=80
    )

    if st.button("✨ تولید محتوا", type="primary"):
        if not topic.strip():
            st.warning("لطفاً موضوع رو وارد کن.")
        else:
            with st.spinner("در حال تولید محتوا..."):
                prompt = f"""تو یک متخصص تولید محتوای حرفه‌ای شبکه‌های اجتماعی برای یک شرکت تجارت بین‌المللی به نام «Iran Trade Services» هستی.

اطلاعات درخواست:
- پلتفرم: {platform}
- نوع محتوا: {content_type}
- لحن: {tone}
- زبان: {language}
- موضوع: {topic}
- توضیحات اضافه: {extra if extra else "ندارد"}

محتوای حرفه‌ای، جذاب و متناسب با الگوریتم‌های {platform} تولید کن. از اموجی‌ها به شکل مناسب استفاده کن، هشتگ‌های مرتبط اضافه کن، و در صورت نیاز Call-to-Action حرفه‌ای بذار.

محتوای نهایی رو به صورت آماده کپی و واضح ارائه بده."""

                messages = [
                    {"role": "system", "content": "تو یک متخصص تولید محتوای شبکه‌های اجتماعی هستی."},
                    {"role": "user", "content": prompt}
                ]

                try:
                    result = ask(messages, provider)
                    st.markdown("---")
                    st.markdown("### 📄 محتوای تولید شده:")
                    st.markdown(result)
                    st.markdown("---")
                    st.caption("💡 می‌تونی این متن رو کپی کنی و مستقیم توی پلتفرم منتشر کنی.")
                except Exception as e:
                    st.error(f"خطا در تولید محتوا: {str(e)}")
