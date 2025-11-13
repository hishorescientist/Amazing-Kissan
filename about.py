import streamlit as st

def app():
    # Page configuration (keep as the first Streamlit call inside the function for single-page usage)
    st.set_page_config(
        page_title="Amazing Kissan • About",
        page_icon="🌾",
        layout="centered",
        initial_sidebar_state="collapsed",
    )  # [web:42][web:51]

    # Minimal CSS
    st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    .ak-center { text-align: center; }
    .ak-cards { display: flex; justify-content: center; gap: 28px; flex-wrap: wrap; margin-top: 28px; }
    .ak-card {
      background: #f8f9fa; padding: 22px; border-radius: 14px; width: 280px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center;
    }
    .ak-card h3 { color: #1F618D; margin-bottom: 10px; }
    .ak-desc { font-size: 18px; color: #444; line-height: 1.7; }
    .ak-hr { margin: 18px 0; border: none; border-top: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)  # [web:46][web:27]

    # Title
    st.markdown("<h1 class='ak-center' style='color:#2E86C1;'>ℹ️ About Us</h1>", unsafe_allow_html=True)  # [web:27][web:34]
    st.write("")

    # Description
    st.markdown("""
    <div class='ak-center ak-desc'>
      <b>Amazing Kissan</b> is a growing company focused on empowering farmers
      and revolutionizing agriculture through innovation and technology.<br><br>
      We believe in sustainable growth, smart farming, and building trust with the
      agricultural community. Your support drives us to keep improving every day.
    </div>
    """, unsafe_allow_html=True)  # [web:46][web:27]

    st.write("")

    # Mission and Vision
    st.markdown("""
    <div class='ak-cards'>
      <div class='ak-card'>
        <h3>🎯 Our Mission</h3>
        <p style='font-size:16px; color:#333;'>
          To provide innovative agricultural solutions that help farmers achieve higher productivity,
          better income, and long-term sustainability.
        </p>
      </div>
      <div class='ak-card'>
        <h3>🌱 Our Vision</h3>
        <p style='font-size:16px; color:#333;'>
          To become a trusted leader in agri-tech innovation, helping every farmer
          embrace smarter and more sustainable farming methods.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)  # [web:32][web:46]

    st.markdown("<hr class='ak-hr'/>", unsafe_allow_html=True)  # [web:27]

    # Footer
    st.markdown("""
    <div class='ak-center' style='color:#555; margin-top:8px;'>
      <small>© 2025 Amazing Kissan. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True)  # [web:27]

if __name__ == "__main__":
    app()  # [web:42]