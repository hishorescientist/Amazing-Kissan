import streamlit as st

def app():
    # Page configuration
    st.set_page_config(
        page_title="Amazing Kissan • About",
        page_icon="🌾",
        layout="centered",
        initial_sidebar_state="collapsed",
    )  # [web:42]

    # Typography and layout CSS
    st.markdown("""
    <style>
      /* Container rhythm */
      .block-container { padding-top: 1.1rem; padding-bottom: 1.2rem; }

      /* Color tokens */
      :root{
        --ak-primary:#2E86C1;
        --ak-accent:#1F618D;
        --ak-text:#374151;
        --ak-muted:#6b7280;
        --ak-soft:#f8f9fa;
        --ak-border:#e5e7eb;
      }

      /* Type scale */
      .ak-hero    { font-size: clamp(28px, 4vw, 40px); font-weight: 700; color: var(--ak-primary); line-height: 1.15; }
      .ak-kicker  { font-size: clamp(14px, 1.6vw, 16px); color: #64748b; }
      .ak-body    { font-size: clamp(16px, 1.9vw, 18px); color: #444; line-height: 1.7; }
      .ak-caption { font-size: 14px; color: var(--ak-muted); }
      .ak-h3      { font-size: clamp(18px, 2vw, 20px); color: var(--ak-accent); font-weight: 700; margin: 0 0 8px 0; }
      .ak-p       { font-size: 16px; color: #333; margin: 0; }

      /* Utilities */
      .ak-center { text-align: center; }
      .ak-hr { margin: 18px 0; border: none; border-top: 1px solid var(--ak-border); }
      .ak-space-xs { margin-top: 6px; }
      .ak-space-sm { margin-top: 10px; }
      .ak-space-md { margin-top: 16px; }
      .ak-space-lg { margin-top: 24px; }

      /* Cards layout */
      .ak-cards { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
      .ak-card {
        background: var(--ak-soft); padding: 22px; border-radius: 14px;
        width: clamp(260px, 32vw, 360px);
        min-height: 220px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: left;
        display: flex; flex-direction: column; justify-content: flex-start; gap: 6px;
      }

      /* Mobile tweaks */
      @media (max-width: 640px) {
        .ak-cards { gap: 16px; }
        .ak-card { width: 100%; min-height: 230px; }
      }
    </style>
    """, unsafe_allow_html=True)  # [web:64][web:75]

    # Hero title
    st.markdown("<h1 class='ak-center ak-hero'>ℹ️ About Us</h1>", unsafe_allow_html=True)  # [web:65][web:79]
    # Kicker (subtitle) instead of empty spacer
    st.markdown("<p class='ak-center ak-kicker ak-space-xs'>Building trustworthy agri‑tech for every farmer.</p>", unsafe_allow_html=True)  # [web:65][web:75]

    # Body description
    st.markdown("""
    <div class='ak-center ak-body ak-space-md'>
      <b>Amazing Kissan</b> is a growing company focused on empowering farmers and revolutionizing agriculture through innovation and technology.<br><br>
      We believe in sustainable growth, smart farming, and building trust with the agricultural community. Your support drives us to keep improving every day.
    </div>
    """, unsafe_allow_html=True)  # [web:65][web:75]

    # Section caption
    st.markdown("<p class='ak-center ak-caption ak-space-sm'>Mission and vision that guide our journey.</p>", unsafe_allow_html=True)  # [web:66][web:74]

    # Cards
    st.markdown("""
    <div class='ak-cards'>
      <div class='ak-card'>
        <h3 class='ak-h3'>🎯 Our Mission</h3>
        <p class='ak-p'>
          To provide innovative agricultural solutions that help farmers achieve higher productivity,
          better income, and long-term sustainability.
        </p>
      </div>
      <div class='ak-card'>
        <h3 class='ak-h3'>🌱 Our Vision</h3>
        <p class='ak-p'>
          To become a trusted leader in agri-tech innovation, helping every farmer
          embrace smarter and more sustainable farming methods.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)  # [web:32][web:46]

    # Divider
    st.markdown("<hr class='ak-hr'/>", unsafe_allow_html=True)  # [web:61]

    # Footer
    st.markdown("""
    <div class='ak-center ak-caption' style='color:#555; margin-top:8px;'>
      <small>© 2025 Amazing Kissan. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True)  # [web:65]

if __name__ == "__main__":
    app()  # [web:42]