import streamlit as st

def app():
    # Page configuration
    st.set_page_config(
        page_title="Amazing Kissan • About",
        page_icon="🌾",
        layout="centered",
        initial_sidebar_state="collapsed",
    )  # [web:42]

    # Global CSS: spacing, cards, typography
    st.markdown("""
    <style>
    /* Container spacing */
    .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }

    /* Helpers */
    .ak-center { text-align: center; }
    .ak-muted { color:#6b7280; }
    .ak-subtle { font-size: 15.5px; color:#64748b; }
    .ak-caption { font-size: 14px; }
    .ak-space-xs { margin-top: 6px; }
    .ak-space-sm { margin-top: 10px; }
    .ak-space-md { margin-top: 16px; }
    .ak-space-lg { margin-top: 24px; }

    /* Cards layout */
    .ak-cards {
      display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 24px;
    }
    /* Responsive equal-size cards with fluid width and equal height */
    .ak-card {
      background: #f8f9fa; padding: 22px; border-radius: 14px;
      width: clamp(260px, 32vw, 360px);
      min-height: 210px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      text-align: center; display: flex; flex-direction: column; justify-content: flex-start;
    }
    .ak-card h3 { color: #1F618D; margin: 0 0 10px 0; }
    .ak-card p { font-size: 16px; color: #333; margin: 0; }

    /* Divider */
    .ak-hr { margin: 18px 0; border: none; border-top: 1px solid #e5e7eb; }

    /* Tablet */
    @media (max-width: 1024px) {
      .ak-card { width: clamp(260px, 42vw, 380px); }
    }
    /* Mobile */
    @media (max-width: 640px) {
      .ak-cards { gap: 16px; }
      .ak-card { width: 100%; min-height: 220px; }
    }
    </style>
    """, unsafe_allow_html=True)  # [web:64][web:77]

    # Title
    st.markdown("<h1 class='ak-center' style='color:#2E86C1;'>ℹ️ About Us</h1>", unsafe_allow_html=True)  # [web:27][web:34]

    # Designed subtitle instead of empty spacer
    st.markdown("""
    <p class='ak-center ak-subtle ak-space-xs'>
      Building trustworthy agri-tech for every farmer.
    </p>
    """, unsafe_allow_html=True)  # [web:65][web:75]

    # Description
    st.markdown("""
    <div class='ak-center' style='font-size:18px; color:#444; line-height:1.7;'>
      <b>Amazing Kissan</b> is a growing company focused on empowering farmers
      and revolutionizing agriculture through innovation and technology.<br><br>
      We believe in sustainable growth, smart farming, and building trust with the
      agricultural community. Your support drives us to keep improving every day.
    </div>
    """, unsafe_allow_html=True)  # [web:65][web:75]

    # Caption before cards (replaces another empty spacer)
    st.markdown("""
    <p class='ak-center ak-caption ak-muted ak-space-sm'>
      Mission and vision that guide our journey.
    </p>
    """, unsafe_allow_html=True)  # [web:66][web:74]

    # Mission and Vision cards (equal-sized, responsive)
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

    # Divider and footer
    st.markdown("<hr class='ak-hr'/>", unsafe_allow_html=True)  # [web:61]
    st.markdown("""
    <div class='ak-center' style='color:#555; margin-top:8px;'>
      <small>© 2025 Amazing Kissan. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True)  # [web:65]

if __name__ == "__main__":
    app()  # [web:42]