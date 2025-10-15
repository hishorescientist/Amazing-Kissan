import streamlit as st
from datetime import datetime

def app():
    """Agricultural Market Integration Page"""
    st.title("🌾 Agricultural Marketplace Hub")
    st.caption("Find and compare the best platforms to buy and sell agricultural products online.")

    # Require login first
    if not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please login to access the market hub.")
        st.stop()

    user = st.session_state.get("user", {})
    st.success(f"👋 Welcome, {user.get('username', 'Farmer')}!")

    st.markdown("---")
    st.subheader("🛒 Partnered Marketplaces")

    # Grid layout for site cards
    col1, col2 = st.columns(2)

    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=120)
        st.markdown("**Amazon Agriculture Section**")
        st.write("Buy fertilizers, seeds, tools, and farm essentials directly from Amazon.")
        if st.button("Visit Amazon", key="amazon", use_container_width=True):
            st.markdown(
                "<meta http-equiv='refresh' content='0; url=https://www.amazon.in/s?k=agriculture+products'>",
                unsafe_allow_html=True,
            )

        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1f/Flipkart_logo.png", width=120)
        st.markdown("**Flipkart Agri Store**")
        st.write("Explore a wide range of farming equipment and seeds at competitive prices.")
        if st.button("Visit Flipkart", key="flipkart", use_container_width=True):
            st.markdown(
                "<meta http-equiv='refresh' content='0; url=https://www.flipkart.com/search?q=agriculture+products'>",
                unsafe_allow_html=True,
            )

    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/b/bf/Bigbasket_logo.png", width=120)
        st.markdown("**BigBasket Farmers Market**")
        st.write("Sell your organic produce directly to BigBasket’s supply network.")
        if st.button("Visit BigBasket", key="bigbasket", use_container_width=True):
            st.markdown(
                "<meta http-equiv='refresh' content='0; url=https://www.bigbasket.com/cl/fruits-vegetables/'>",
                unsafe_allow_html=True,
            )

        st.image("https://upload.wikimedia.org/wikipedia/en/4/4d/Agribazaar_logo.png", width=120)
        st.markdown("**AgriBazaar Official**")
        st.write("India’s top B2B marketplace for grains, pulses, and agri-commodities.")
        if st.button("Visit AgriBazaar", key="agribazaar", use_container_width=True):
            st.markdown(
                "<meta http-equiv='refresh' content='0; url=https://www.agribazaar.com/'>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.subheader("🌍 Featured Categories")
    st.markdown("""
    - 🌱 Seeds & Fertilizers  
    - 🚜 Farm Machinery  
    - 🍅 Organic Produce  
    - 🐄 Animal Feed & Dairy Supplies  
    - 💧 Irrigation & Tools
    """)

    st.info("💡 Tip: Use these trusted platforms to compare prices and availability for your agricultural needs.")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")