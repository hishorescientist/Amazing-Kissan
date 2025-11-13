import streamlit as st

# Page setup (must be first)
st.set_page_config(page_title="About Us", page_icon="ℹ️", layout="centered")

# Title
st.markdown("<h1 style='text-align:center; color:#2E86C1;'>ℹ️ About Us</h1>", unsafe_allow_html=True)
st.write("")

# Description
st.markdown(
    """
    <div style='text-align:center; font-size:18px; color:#444; line-height:1.7;'>
        <b>Amazing Kissan</b> is a growing company focused on empowering farmers 
        and revolutionizing agriculture through innovation and technology.<br><br>
        We believe in sustainable growth, smart farming, and building trust with the
        agricultural community. Your support drives us to keep improving every day.
    </div>
    """, unsafe_allow_html=True
)

st.write("")

# Mission and Vision cards
st.markdown(
    """
    <div style='display:flex; justify-content:center; gap:40px; margin-top:40px; flex-wrap:wrap;'>

        <div style='background-color:#f8f9fa; padding:25px; border-radius:15px; width:280px; 
                    box-shadow:0 4px 10px rgba(0,0,0,0.1); text-align:center;'>
            <h3 style='color:#1F618D;'>🎯 Our Mission</h3>
            <p style='font-size:16px; color:#333;'>
                To provide innovative agricultural solutions that help farmers achieve higher productivity, 
                better income, and long-term sustainability.
            </p>
        </div>

        <div style='background-color:#f8f9fa; padding:25px; border-radius:15px; width:280px; 
                    box-shadow:0 4px 10px rgba(0,0,0,0.1); text-align:center;'>
            <h3 style='color:#1F618D;'>🌱 Our Vision</h3>
            <p style='font-size:16px; color:#333;'>
                To become a trusted leader in agri-tech innovation, helping every farmer 
                embrace smarter and more sustainable farming methods.
            </p>
        </div>

    </div>
    """, unsafe_allow_html=True
)

st.write("")
st.markdown("<hr>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div style='text-align:center; color:#555; margin-top:15px;'>
        <small>© 2025 Amazing Kissan. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True
)