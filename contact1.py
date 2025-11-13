import streamlit as st

def app():
    st.set_page_config(page_title="Contact Us", page_icon="📞", layout="centered")

    # Main Title
    st.markdown("<h1 style='text-align: center; color: #2E86C1;'>📞 Contact Us</h1>", unsafe_allow_html=True)
    st.write("")

    # Description
    st.markdown(
        """
        <div style='text-align: center; font-size:18px; color:#444;'>
            We'd love to hear from you! <br>
            Reach out to us through any of the contact numbers below.
        </div>
        """, unsafe_allow_html=True
    )
    st.write("")

    # Contact Details - Styled Cards
    st.markdown(
        """
        <div style='display: flex; justify-content: center; gap: 40px; margin-top: 30px;'>
            <div style='background-color: #f5f5f5; padding: 20px 40px; border-radius: 15px; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;'>
                <h3 style='color: #1F618D;'>📱 Contact Number 1</h3>
                <p style='font-size: 20px; font-weight: bold;'>+91 83443 73555</p>
            </div>
            <div style='background-color: #f5f5f5; padding: 20px 40px; border-radius: 15px; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;'>
                <h3 style='color: #1F618D;'>📱 Contact Number 2</h3>
                <p style='font-size: 20px; font-weight: bold;'>+91 85249 46296</p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #555; margin-top: 15px;'>
            <small>© 2025 Your Company Name. All rights reserved.</small>
        </div>
        """, unsafe_allow_html=True
    )