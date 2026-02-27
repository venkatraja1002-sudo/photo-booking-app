import streamlit as st
import pandas as pd
import base64
import urllib.parse
import os
from db import init_db, seed_packages_if_empty, get_conn

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Photography Booking", page_icon="📸", layout="wide")

# ----------------- STYLES (Wedding Luxury) -----------------
st.markdown("""
<style>
.big-title { text-align: center; font-size: 36px; font-weight: 800; }
.subtitle { text-align: center; font-size: 18px; margin-top: 10px; color: rgba(40,40,40,0.75); }

/* --- Wedding Luxury section styles --- */
.lux-wrap { max-width: 980px; margin: 0 auto; }
.lux-card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(212, 175, 55, 0.35);
  border-radius: 18px;
  padding: 26px 26px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.08);
}
.lux-title {
  text-align: center;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: 0.5px;
  margin: 0 0 10px 0;
}
.lux-divider {
  height: 1px;
  width: 140px;
  margin: 12px auto 18px auto;
  background: linear-gradient(90deg, rgba(212,175,55,0), rgba(212,175,55,0.95), rgba(212,175,55,0));
}
.lux-text { text-align: center; font-size: 16px; line-height: 1.7; color: rgba(35,35,35,0.90); }
.lux-pill-row { display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-top: 14px; }
.lux-pill {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(212, 175, 55, 0.45);
  background: rgba(255, 250, 235, 0.75);
  font-size: 14px;
}
.lux-cta-row { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-top: 18px; }
.lux-btn {
  display:inline-block;
  padding: 12px 22px;
  border-radius: 14px;
  text-decoration:none;
  font-weight: 900;
  border: 1px solid rgba(212, 175, 55, 0.7);
  background: linear-gradient(180deg, rgba(255,250,235,0.95), rgba(255,245,220,0.85));
  color: rgba(25,25,25,0.95);
  transition: all 0.35s ease;
}

/* Hover Animation */
.lux-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(212, 175, 55, 0.45);
  background: linear-gradient(180deg, rgba(255,245,220,1), rgba(255,230,180,0.9));
}
}
.lux-note { text-align:center; font-size: 13px; color: rgba(50,50,50,0.65); margin-top: 10px; }

.stButton>button {
  height: 56px;
  font-size: 17px;
  font-weight: 900;
  border-radius: 14px;
  border: 1px solid rgba(212, 175, 55, 0.6);
  background: linear-gradient(180deg, #fff8e8, #fff2cc);
  color: #222;
  transition: all 0.35s ease;
}

/* Hover Effect */
.stButton>button:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4);
  background: linear-gradient(180deg, #fff2cc, #ffe4a3);
  border: 1px solid rgba(212, 175, 55, 0.9);
}
</style>
""", unsafe_allow_html=True)

# ----------------- HELPERS -----------------
def add_bg_image(image_file: str):
    """
    Banner image using base64.
    Put your banner at: images/banner.jpg
    """
    if not os.path.exists(image_file):
        st.warning(f"Banner image not found: {image_file}")
        return

    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>
        .banner {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            height: 380px;
            border-radius: 15px;
            margin-bottom: 18px;
        }}
        </style>
        <div class="banner"></div>
        """,
        unsafe_allow_html=True
    )

def whatsapp_link(phone_number: str, message: str) -> str:
    phone = phone_number.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone = phone[1:]
    # If user enters 10 digits, assume India (+91)
    if len(phone) == 10:
        phone = "91" + phone

    text = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={text}"

# ----------------- DB INIT -----------------
init_db()
seed_packages_if_empty()

# ----------------- DB FUNCTIONS -----------------
def fetch_packages():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM packages WHERE is_active=1 ORDER BY price ASC", conn)
    conn.close()
    return df

def fetch_all_packages_admin():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM packages ORDER BY id DESC", conn)
    conn.close()
    return df

def add_package(name, price, duration_hours, includes, delivery_days, is_active=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO packages (name, price, duration_hours, includes, delivery_days, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, int(price), int(duration_hours), includes, int(delivery_days), int(is_active)))
    conn.commit()
    conn.close()

def update_package(pkg_id, name, price, duration_hours, includes, delivery_days, is_active):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE packages
        SET name=?, price=?, duration_hours=?, includes=?, delivery_days=?, is_active=?
        WHERE id=?
    """, (name, int(price), int(duration_hours), includes, int(delivery_days), int(is_active), int(pkg_id)))
    conn.commit()
    conn.close()

def set_package_active(pkg_id, active: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE packages SET is_active=? WHERE id=?", (int(active), int(pkg_id)))
    conn.commit()
    conn.close()

def create_booking(data):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings (customer_name, phone, email, event_type, event_date, location, package_id, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["customer_name"], data["phone"], data["email"],
        data["event_type"], data["event_date"], data["location"],
        data["package_id"], data["message"]
    ))
    conn.commit()
    conn.close()

def fetch_bookings():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT b.id, b.customer_name, b.phone, b.email, b.event_type, b.event_date, b.location,
               p.name AS package_name, b.status, b.created_at, b.message
        FROM bookings b
        JOIN packages p ON b.package_id = p.id
        ORDER BY b.created_at DESC
    """, conn)
    conn.close()
    return df

def update_booking_status(booking_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status=? WHERE id=?", (status, int(booking_id)))
    conn.commit()
    conn.close()

# ----------------- STATE INIT -----------------
if "home_view" not in st.session_state:
    st.session_state.home_view = "home"  # home | packages | book

# ----------------- SIDEBAR -----------------
st.sidebar.title("📸 Menu")
main_page = st.sidebar.radio("Navigate", ["🏠 Home", "🔐 Admin"])

# ----------------- HOME -----------------
if main_page == "🏠 Home":

    # ---- HOME MAIN SCREEN ----
    if st.session_state.home_view == "home":
        # Banner (make sure this file exists in repo)
        add_bg_image(os.path.join("images", "banner.jpg"))

        st.markdown("<div class='big-title'>📸 Welcome to EAGLE DIGITAL AND GRAPHICS</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='subtitle'>
        🤍 <b>Congratulations to the couple!</b><br><br>
        We specialize in capturing natural, candid moments and timeless portraits.<br>
        Explore our packages and book your date today.
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### Choose an option below 👇")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📦 Packages")
            st.write("See package details and pricing.")
            if st.button("Open Packages", use_container_width=True):
                st.session_state.home_view = "packages"
                st.rerun()

        with col2:
            st.markdown("### 📝 Book Now")
            st.write("Book your event quickly.")
            if st.button("Open Book Now", use_container_width=True):
                st.session_state.home_view = "book"
                st.rerun()

        # ---- Wedding Luxury About/Contact ----
        st.divider()
        st.markdown("<div class='lux-wrap'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="lux-card">
          <div class="lux-cta-row">
             <a class="lux-btn" href="https://wa.me/918072123858" target="_blank">💬 WhatsApp</a>
             <a class="lux-btn" href="tel:+918072123858">📞 Call Now</a>
             <a class="lux-btn" href="mailto:venkatraja1002@gmail.com">📧 Email</a>
          </div>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---- PACKAGES PAGE ----
    elif st.session_state.home_view == "packages":
        st.title("📦 Packages")

        if st.button("⬅ Back to Home"):
            st.session_state.home_view = "home"
            st.rerun()

        packages = fetch_packages()
        if packages.empty:
            st.warning("No packages available.")
        else:
            for _, row in packages.iterrows():
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    with left:
                        st.markdown(f"### {row['name']}")
                        st.write(row["includes"])
                        st.caption(f"Duration: {row['duration_hours']} hrs • Delivery: {row['delivery_days']} days")
                    with right:
                        st.markdown(f"## ₹{row['price']}")

        st.info("Want to book? Go back and open **Book Now**.")

    # ---- BOOK NOW PAGE ----
    elif st.session_state.home_view == "book":
        st.title("📝 Book Now")

        if st.button("⬅ Back to Home"):
            st.session_state.home_view = "home"
            st.rerun()

        packages = fetch_packages()
        if packages.empty:
            st.warning("Packages not available. Please add packages first.")
        else:
            package_options = {f"{r['name']} (₹{r['price']})": int(r["id"]) for _, r in packages.iterrows()}

            with st.form("booking_form"):
                customer_name = st.text_input("Your Name *")
                phone = st.text_input("Phone Number *")
                email = st.text_input("Email (optional)")
                event_type = st.selectbox("Event Type *", ["Wedding", "Pre-Wedding", "Birthday", "Outdoor", "Baby Shoot", "Other"])
                event_date = st.date_input("Event Date *")
                event_date_str = str(event_date)
                location = st.text_input("Location *")
                package_label = st.selectbox("Select Package *", list(package_options.keys()))
                message = st.text_area("Message / Requirements (optional)")
                submitted = st.form_submit_button("Submit Booking ✅")

            if submitted:
                if not customer_name.strip() or not phone.strip() or not location.strip():
                    st.error("Please fill all required fields (*)")
                else:
                    create_booking({
                        "customer_name": customer_name.strip(),
                        "phone": phone.strip(),
                        "email": email.strip(),
                        "event_type": event_type,
                        "event_date": event_date_str,
                        "location": location.strip(),
                        "package_id": package_options[package_label],
                        "message": message.strip(),
                    })

                    st.success("Booking request submitted! ✅ We will contact you soon.")

                    # Photographer WhatsApp number (10 digits OK; +91 auto added)
                    PHOTOGRAPHER_WA = "8072123858"

                    wa_msg = (
                        f"Hi, I want to book a photography event.\n\n"
                        f"Name: {customer_name.strip()}\n"
                        f"Phone: {phone.strip()}\n"
                        f"Event: {event_type}\n"
                        f"Date: {event_date_str}\n"
                        f"Location: {location.strip()}\n"
                        f"Package: {package_label}\n\n"
                        f"Message: {message.strip() if message.strip() else 'N/A'}"
                    )

                    wa_url = whatsapp_link(PHOTOGRAPHER_WA, wa_msg)
                    st.markdown(f"👉 **Instant confirmation:** [Message us on WhatsApp]({wa_url})")

# ----------------- ADMIN -----------------
else:
    st.title("🔐 Admin Panel")

    password = st.text_input("Admin Password", type="password")
    admin_pw = st.secrets.get("ADMIN_PASSWORD", "")
    if password != admin_pw:
        st.warning("Wrong password.")
        st.stop()

    tab1, tab2 = st.tabs(["📋 Bookings", "📦 Manage Packages"])

    with tab1:
        st.subheader("📋 All Bookings")
        bookings = fetch_bookings()
        st.dataframe(bookings, use_container_width=True)

        st.subheader("✅ Update Booking Status")
        if not bookings.empty:
            booking_id = st.selectbox("Select Booking ID", bookings["id"].tolist())
            new_status = st.selectbox("Status", ["pending", "confirmed", "rejected"])
            if st.button("Update Status"):
                update_booking_status(booking_id, new_status)
                st.success(f"Updated booking {booking_id} to {new_status}")
                st.rerun()

    with tab2:
        st.subheader("📦 Manage Packages")
        all_pkgs = fetch_all_packages_admin()
        st.dataframe(all_pkgs, use_container_width=True)

        st.divider()
        st.markdown("### ➕ Add New Package")
        with st.form("add_pkg_form"):
            n = st.text_input("Package Name")
            p = st.number_input("Price (₹)", min_value=0, step=500, value=10000)
            d = st.number_input("Duration (hours)", min_value=1, step=1, value=4)
            inc = st.text_area("Includes (one line or bullet text)")
            deliv = st.number_input("Delivery Days", min_value=1, step=1, value=7)
            active = st.checkbox("Active (visible to customers)", value=True)
            add_submit = st.form_submit_button("Add Package ✅")

        if add_submit:
            if not n.strip():
                st.error("Package name is required.")
            else:
                add_package(n.strip(), p, d, inc.strip(), deliv, 1 if active else 0)
                st.success("Package added!")
                st.rerun()

        st.divider()
        st.markdown("### ✏️ Edit Package")
        if not all_pkgs.empty:
            pkg_id = st.selectbox("Select Package ID", all_pkgs["id"].tolist())
            pkg = all_pkgs[all_pkgs["id"] == pkg_id].iloc[0]

            with st.form("edit_pkg_form"):
                en = st.text_input("Package Name", value=str(pkg["name"]))
                ep = st.number_input("Price (₹)", min_value=0, step=500, value=int(pkg["price"]))
                ed = st.number_input("Duration (hours)", min_value=1, step=1, value=int(pkg["duration_hours"] or 1))
                einc = st.text_area("Includes", value=str(pkg["includes"] or ""))
                edeliv = st.number_input("Delivery Days", min_value=1, step=1, value=int(pkg["delivery_days"] or 1))
                eactive = st.checkbox("Active", value=bool(pkg["is_active"]))
                save_btn = st.form_submit_button("Save Changes 💾")

            colA, colB = st.columns(2)
            with colA:
                if st.button("✅ Activate", use_container_width=True):
                    set_package_active(int(pkg_id), 1)
                    st.success("Package activated.")
                    st.rerun()
            with colB:
                if st.button("⛔ Deactivate", use_container_width=True):
                    set_package_active(int(pkg_id), 0)
                    st.success("Package deactivated.")
                    st.rerun()

            if save_btn:
                if not en.strip():
                    st.error("Package name is required.")
                else:
                    update_package(int(pkg_id), en.strip(), ep, ed, einc.strip(), edeliv, 1 if eactive else 0)
                    st.success("Package updated!")
                    st.rerun()
        else:
            st.info("No packages available yet.")