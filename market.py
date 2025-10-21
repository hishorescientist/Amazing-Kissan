import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date

# ---------------- GOOGLE SHEET SETUP ----------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def connect_google_sheet(sheet_name):
    if "google" not in st.secrets or "secrets_creds" not in st.secrets["google"]:
        st.warning("⚠️ Google credentials missing in secrets.")
        return None
    try:
        creds_json = st.secrets["google"]["secrets_creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet(sheet_name)
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {e}")
        return None


# ---------------- MARKET PAGE ----------------
def app():
    st.title("🌾 Agricultural Market System")

    # --- LOGIN CHECK ---
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Please log in first.")
        st.stop()

    user = st.session_state.user
    username = user.get("username", "Unknown User")
    address = user.get("address", "")
    phone = user.get("phone", "")
    email = user.get("email", "")

    # --- STATE VARIABLE FOR ALERT PAGE ---
    st.session_state.setdefault("view_order_alerts", False)

    # --- CONNECT SHEETS ---
    market_sheet = connect_google_sheet("Sheet5")  # Crops
    orders_sheet = connect_google_sheet("Sheet6")  # Orders
    if not market_sheet or not orders_sheet:
        st.error("❌ Unable to connect to Google Sheets.")
        return

    # =====================================================
    # 🔔 ORDER ALERT PAGE (All Orders Stay Visible)
    # =====================================================
    if st.session_state.view_order_alerts:
        st.header("📣 Order Alerts")

        try:
            all_orders = orders_sheet.get_all_records()
            all_orders = [{k.strip(): v for k, v in row.items()} for row in all_orders]
            my_sales = [o for o in all_orders if o.get("Farmer Name") == username]

            if my_sales:
                for order in my_sales:
                    order_id = order.get("Order ID")
                    status = order.get("Status", "Pending")
                    delivery_type = order.get("Delivery Option", "Pickup")

                    st.markdown("---")
                    cols = st.columns([4, 1, 1])
                    cols[0].write(
                        f"**Buyer:** {order['Buyer Name']} wants {order['Quantity']} kg of {order['Crop Name']} "
                        f"for ₹{order['Price']} | **Delivery:** {delivery_type} | **Status:** {status}"
                    )

                    # --- STATUS HANDLER ---
                    if status.startswith("Accepted"):
                        st.success(f"✅ Order accepted ({status})")
                    elif status == "Rejected":
                        st.error("❌ Order rejected.")
                    else:
                        # ---------------- PICKUP ORDERS ----------------
                        if delivery_type == "Pickup":
                            if cols[1].button("✅ Accept", key=f"pickup_accept_{order_id}"):
                                try:
                                    row_index = next(i + 2 for i, r in enumerate(all_orders) if r.get("Order ID") == order_id)
                                    orders_sheet.update_cell(row_index, 8, "Accepted (Pickup)")
                                    st.success(f"✅ Order {order_id} accepted for pickup.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating pickup order: {e}")

                            if cols[2].button("❌ Reject", key=f"pickup_reject_{order_id}"):
                                try:
                                    row_index = next(i + 2 for i, r in enumerate(all_orders) if r.get("Order ID") == order_id)
                                    orders_sheet.update_cell(row_index, 8, "Rejected")
                                    st.warning(f"❌ Order {order_id} rejected.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error rejecting order: {e}")

                        # ---------------- HOME DELIVERY ORDERS ----------------
                        else:
                            if cols[1].button("✅ Accept", key=f"home_accept_{order_id}"):
                                with st.expander(f"🚚 Delivery Setup for Order {order_id}", expanded=True):
                                    delivery_choice = st.radio(
                                        "Choose Delivery Type:",
                                        ["I will deliver to home directly", "Courier"],
                                        key=f"choice_{order_id}"
                                    )

                                    if delivery_choice == "Courier":
                                        courier_company = st.text_input("Courier Company Name", key=f"courier_{order_id}")
                                        tracking_number = st.text_input("Tracking Number", key=f"track_{order_id}")
                                        expected_date = st.date_input("Expected Delivery Date", min_value=date.today(), key=f"date_{order_id}")

                                        if st.button("📦 Confirm Courier Delivery", key=f"confirm_{order_id}"):
                                            try:
                                                row_index = next(i + 2 for i, r in enumerate(all_orders) if r.get("Order ID") == order_id)
                                                orders_sheet.update_cell(row_index, 8, "Accepted (Courier)")
                                                orders_sheet.update_cell(row_index, 9, courier_company)
                                                orders_sheet.update_cell(row_index, 10, tracking_number)
                                                orders_sheet.update_cell(row_index, 11, str(expected_date))
                                                st.success("✅ Courier details saved.")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error saving courier details: {e}")

                                    elif delivery_choice == "I will deliver to home directly":
                                        if st.button("🚚 Confirm Direct Delivery", key=f"direct_{order_id}"):
                                            try:
                                                row_index = next(i + 2 for i, r in enumerate(all_orders) if r.get("Order ID") == order_id)
                                                orders_sheet.update_cell(row_index, 8, "Accepted (Home Delivery)")
                                                st.success("✅ Marked as direct home delivery.")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error updating delivery: {e}")

                            if cols[2].button("❌ Reject", key=f"home_reject_{order_id}"):
                                try:
                                    row_index = next(i + 2 for i, r in enumerate(all_orders) if r.get("Order ID") == order_id)
                                    orders_sheet.update_cell(row_index, 8, "Rejected")
                                    st.warning(f"❌ Order {order_id} rejected.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error rejecting order: {e}")
            else:
                st.info("No orders yet.")
        except Exception as e:
            st.error(f"❌ Failed to load orders: {e}")

        if st.button("⬅️ Back to Market"):
            st.session_state.view_order_alerts = False
            st.rerun()
        return

    # =====================================================
    # 🔔 ALERT BUTTON (TOP OF PAGE)
    # =====================================================
    try:
        all_orders = orders_sheet.get_all_records()
        all_orders = [{k.strip(): v for k, v in row.items()} for row in all_orders]
        my_sales = [o for o in all_orders if o.get("Farmer Name") == username and o.get("Status") == "Pending"]
        if my_sales:
            if st.button(f"📣 You have {len(my_sales)} pending order(s)! Click to view"):
                st.session_state.view_order_alerts = True
                st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to load order alerts: {e}")

    # =====================================================
    # 🛒 MAIN TABS
    # =====================================================
    tab1, tab2, tab3 = st.tabs(["Sell Crops", "View Market", "My Orders"])

    # SELL CROPS
    with tab1:
        st.subheader("🧑‍🌾 Post Your Crop for Sale")
        st.text_input("Your Name", value=username, disabled=True)
        st.text_input("Location (Address)", value=address, disabled=True)
        st.text_input("Phone Number", value=phone, disabled=True)

        crop_options = ["Paddy", "Wheat", "Maize", "Millet", "Sugarcane", "Cotton",
                        "Groundnut", "Vegetables", "Fruits", "Other"]
        crop = st.selectbox("🌱 Select Crop Name", crop_options)
        if crop == "Other":
            crop = st.text_input("Enter Crop Name")

        quantity = st.number_input("Quantity (kg)", min_value=1)
        price = st.number_input("Price (₹ per kg)", min_value=1)

        if st.button("✅ Post to Market", use_container_width=True):
            try:
                market_sheet.append_row([username, crop, quantity, price, address, phone, email])
                st.success("🌾 Crop posted successfully!")
            except Exception as e:
                st.error(f"❌ Failed to post crop: {e}")

    # VIEW MARKET
    with tab2:
        st.subheader("📈 Available Crops in Market")
        try:
            data = market_sheet.get_all_records()
            data = [{k.strip(): v for k, v in row.items()} for row in data]

            if not data:
                st.info("No crops listed yet.")
            else:
                for idx, row in enumerate(data):
                    st.write(
                        f"**Seller:** {row.get('Farmer Name','')} | "
                        f"**Crop:** {row.get('Crop Name','')} | "
                        f"**Qty:** {row.get('Quantity (kg)','')} kg | "
                        f"**Price:** ₹{row.get('Price (₹/kg)','')}"
                    )
                    st.write(f"**Location:** {row.get('Location','')} | **Phone:** {row.get('Phone','')}")

                    delivery_option = st.selectbox(
                        f"Choose Delivery Option for {row.get('Crop Name')}",
                        ["Pickup", "Home Delivery"],
                        key=f"delivery_{idx}"
                    )

                    buy_button = st.button(f"💰 Buy {row.get('Crop Name','')}", key=f"buy_{idx}")
                    if buy_button:
                        order_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        orders_sheet.append_row([
                            order_id, row.get("Crop Name"), row.get("Quantity (kg)"),
                            row.get("Price (₹/kg)"), username, email,
                            row.get("Farmer Name"), "Pending", "", "", "", delivery_option
                        ])
                        st.success("✅ Order placed! Seller will confirm soon.")
                    st.markdown("---")
        except Exception as e:
            st.error(f"❌ Failed to load market data: {e}")

    # MY ORDERS
    with tab3:
        st.subheader("📦 My Orders (Buyer View)")
        try:
            all_orders = orders_sheet.get_all_records()
            my_orders = [o for o in all_orders if o.get("Buyer Name") == username]
            if not my_orders:
                st.info("No orders placed yet.")
            else:
                for order in my_orders:
                    st.write(f"**Crop:** {order['Crop Name']} | **Status:** {order['Status']}")
                    st.write(f"**Farmer:** {order['Farmer Name']} | **Delivery:** {order.get('Delivery Option','')}")
                    if "Courier" in order.get("Status", ""):
                        st.write(f"📦 Courier: {order.get('Courier Company','N/A')}")
                        st.write(f"🔢 Tracking No.: {order.get('Tracking Number','N/A')}")
                        st.write(f"📅 Expected: {order.get('Expected Delivery','N/A')}")
                    st.markdown("---")
        except Exception as e:
            st.error(f"❌ Failed to load your orders: {e}")