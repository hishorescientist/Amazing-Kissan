import streamlit as st

def app():
    st.set_page_config(
        page_title="Amazing Kissan • About",
        page_icon="🌾",
        layout="centered",
        initial_sidebar_state="collapsed",
    )  # [web:42]

    st.markdown("""
    <style>
    .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }

    /* Layout and responsive cards */
    .ak-center { text-align: center; }
    .ak-cards {
      display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 24px;
    }
    /* Use clamp for fluid width; enforce equal heights */
    .ak-card {
      background: #f8f9fa; padding: 22px; border-radius: 14px;
      width: clamp(260px, 32vw, 360px);
      min-height: 210px; /* equal height for both cards */
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      text-align: center; display: flex; flex-direction: column; justify-content: flex-start;
    }
    .ak-card h3 { color: #1F618D; margin: 0 0 10px 0; }
    .ak-card p { font-size: 16px; color: #333; margin: 0; }

    .ak-desc { font-size: 18px; color: #444; line-height: 1.7; }

    /* Tighter divider */
    .ak-hr { margin: 18px 0; border: none; border-top: 1px solid #e5e7eb; }

    /* Tablet tweaks: slightly wider cards */
    @media (max-width: 1024px) {
      .ak-card { width: clamp(260px, 42vw, 380px); }
    }

    /* Mobile: full-width cards with consistent height and spacing */
    @media (max-width: 640px) {
      .ak-cards { gap: 16px; }
      .ak-card { width: 100%; min-height: 220px; }
      .ak-desc { font-size: 17px; }
    }
    </style>
    """, unsafe_allow_html=True)  # [web:46][web:32]

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

    # Mission and Vision (equal-sized, responsive cards)
    st.markdown("""
    <div class='ak-cards'>
      <div class='ak-card'>
        <h3>🎯 Our Mission</h3>
        <p>
          To provide innovative agricultural solutions that help farmers achieve higher productivity,
          better income, and long-term sustainability.
        </p>
      </div>
      <div class='ak-card'>
        <h3>🌱 Our Vision</h3>
        <p>
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