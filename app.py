import streamlit as st
from supabase import create_client, Client
import pandas as pd
import hashlib
from datetime import datetime, date, timedelta
import uuid
import re

# ----------------- PAGE SETUP & THEME -----------------
st.set_page_config(
    page_title="LuxeSalon OS | Studio Management",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fresh, Bright, High-Contrast Professional Salon Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Clean, bright luxury background */
    .stApp {
        background: linear-gradient(135deg, #F8F9FB 0%, #F3F4F8 50%, #FAF7F2 100%);
        color: #1E293B;
    }
    
    /* Global text clarity */
    h1, h2, h3, h4, h5, p, label, span {
        color: #1E293B !important;
    }
    
    /* Prominent, readable Metric Cards */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #D4A338;
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800;
        font-size: 1.85rem;
    }

    /* ALL PRIMARY BUTTONS: Crisp, High-Contrast Gold */
    div.stButton > button {
        background: linear-gradient(135deg, #E6B447 0%, #D4A338 100%) !important;
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px;
        border: 1px solid #C49329 !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 2px 6px rgba(212, 163, 56, 0.3) !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #F5C55A 0%, #E6B447 100%) !important;
        color: #000000 !important;
        box-shadow: 0 4px 12px rgba(212, 163, 56, 0.45) !important;
        transform: translateY(-1px);
    }
    
    /* Secondary/Action Log-Off button */
    button[key*="logout"] {
        background: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px solid #FCA5A5 !important;
    }
    button[key*="logout"]:hover {
        background: #FECACA !important;
        color: #7F1D1D !important;
    }

    /* High-contrast forms & inputs */
    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 28px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    }
    
    input, select, textarea {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }

    /* Lookbook Styling */
    .haircut-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .haircut-card:hover {
        transform: translateY(-4px);
    }
    .haircut-card img {
        width: 100%;
        height: 250px;
        object-fit: cover;
    }
    .haircut-info {
        padding: 16px;
    }

    /* Footer Branding */
    .brand-footer {
        text-align: center;
        padding: 24px 0 10px 0;
        color: #64748B;
        font-size: 0.92rem;
        font-weight: 500;
        border-top: 1px solid #E2E8F0;
        margin-top: 50px;
    }
    .brand-highlight {
        color: #B45309;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- DB CONNECTION -----------------
@st.cache_resource
def init_supabase() -> Client:
    raw_url = st.secrets["supabase"]["url"].strip()
    clean_url = raw_url.replace("/rest/v1/", "").replace("/rest/v1", "").rstrip("/")
    key = st.secrets["supabase"]["key"].strip()
    return create_client(clean_url, key)

supabase = init_supabase()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def clean_phone_number(phone_raw: str) -> str:
    """Extracts only digits and returns 10-digit number if valid."""
    digits = re.sub(r"\D", "", phone_raw)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return digits

# ----------------- SESSION STATE -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# ----------------- WELCOMING LOGIN SCREEN -----------------
def login_screen():
    c_pad1, col_login, c_pad2 = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='text-align: center; margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size: 3rem;'>✨ ✂️ ✨</span>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #0F172A; font-size: 2.2rem; margin-bottom: 4px;'>Welcome to LuxeSalon OS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 1.02rem; margin-bottom: 22px;'>Smart Salon Management & Point-of-Sale Suite</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<h4 style='color: #0F172A; margin-bottom: 12px;'>Sign In to Your Salon</h4>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="e.g. Admin_Vikram, SalonOwner, or Staff").strip()
            password = st.text_input("Password", type="password", placeholder="Enter your secret password")
            
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            btn = st.form_submit_button("Sign In to Salon OS", use_container_width=True)

            if btn:
                if not username or not password:
                    st.error("Please enter both your username and password.")
                    return

                hashed = hash_password(password)
                resp = supabase.table("users").select("*").eq("username", username).eq("password_hash", hashed).execute()
                
                if resp.data:
                    user_data = resp.data[0]
                    # Verify Store Status & Validity for non-admin accounts
                    if user_data["role"] != "admin":
                        store_res = supabase.table("stores").select("*").eq("store_id", user_data["store_id"]).execute()
                        if not store_res.data:
                            st.error("Store account not found. Please contact administration.")
                            return
                        store_info = store_res.data[0]
                        if store_info.get("status") != "active":
                            st.error("⛔ This salon store has been deactivated. Please contact support.")
                            return
                        
                        trial_end = datetime.strptime(store_info["trial_end"], "%Y-%m-%d").date()
                        if date.today() > trial_end:
                            st.error(f"⛔ Your plan expired on {trial_end}. Please renew with the Admin.")
                            return

                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.current_page = "admin_clients" if user_data["role"] == "admin" else "home"
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.")

        st.markdown("""
        <div style='text-align: center; margin-top: 25px; color: #64748B; font-size: 0.9rem;'>
            Developed & Powered by <span style='font-weight: 700; color: #B45309;'>Global Wealth International</span>
        </div>
        """, unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# Context
user = st.session_state.user
role = user["role"]
store_id = user["store_id"]

# ----------------- LOG OFF HELPER & NAVIGATION -----------------
def perform_logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.current_page = "home"
    st.rerun()

# Sidebar Log Off & Profile
with st.sidebar:
    st.markdown(f"### 👤 {user['name']}")
    st.markdown(f"**Username:** `{user['username']}`")
    st.markdown(f"**Role:** `{role.upper()}`")
    st.caption("Engineered by **Global Wealth International**")
    st.write("---")
    if st.button("🚪 Log Off Account", key="sidebar_logout_btn", use_container_width=True):
        perform_logout()

# Top Header Navigation Bar
if role == "admin":
    nav1, nav2, nav3, nav4 = st.columns([4.5, 2.5, 2, 1.5])
    with nav1:
        st.markdown(f"<h3 style='margin:0; font-weight:800; color:#0F172A;'>🛡️ Super Admin | {user['name']}</h3>", unsafe_allow_html=True)
    with nav2:
        if st.button("🏢 Manage Salon Clients", use_container_width=True):
            st.session_state.current_page = "admin_clients"
            st.rerun()
    with nav3:
        if st.button("💇 Trending Styles", use_container_width=True):
            st.session_state.current_page = "lookbook"
            st.rerun()
    with nav4:
        if st.button("🚪 Log Off", key="top_admin_logout", use_container_width=True):
            perform_logout()
else:
    nav1, nav2, nav3, nav4, nav5, nav6 = st.columns([3, 2, 2, 2, 2, 1.5])
    with nav1:
        st.markdown(f"<h3 style='margin:0; font-weight:800; color:#0F172A;'>💈 {user['name']}</h3>", unsafe_allow_html=True)
    with nav2:
        if st.button("🏠 POS / Billing", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with nav3:
        if st.button("💇 Trending Styles", use_container_width=True):
            st.session_state.current_page = "lookbook"
            st.rerun()
    with nav4:
        if role == "client":
            if st.button("💸 Expenses", use_container_width=True):
                st.session_state.current_page = "expenses"
                st.rerun()
    with nav5:
        if role == "client":
            if st.button("⚙️ Store Config", use_container_width=True):
                st.session_state.current_page = "settings"
                st.rerun()
    with nav6:
        if st.button("🚪 Log Off", key="top_user_logout", use_container_width=True):
            perform_logout()

st.write("---")

# =========================================================
# MODAL DIALOG: CONFIRM CLIENT ONBOARDING
# =========================================================
@st.dialog("📋 Confirm New Salon Onboarding")
def confirm_client_modal(client_data):
    st.markdown("Please review the salon details before creating the account:")
    
    review_info = {
        "Salon / Shop Name": client_data["salon_name"],
        "Owner Name": client_data["owner_name"],
        "Mobile Number": f"+91 {client_data['owner_phone']}",
        "Login Username": client_data["username"],
        "Login Password": "•" * len(client_data["password"]),
        "Subscription Plan": client_data["plan_option"],
        "Validity Ends On": str(client_data["trial_end"])
    }
    
    st.dataframe(pd.DataFrame(list(review_info.items()), columns=["Field", "Details"]), use_container_width=True, hide_index=True)
    
    st.write("---")
    st.warning("⚠️ Once confirmed, the login credentials and initial rate card will be generated.")
    
    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("✅ Yes, Confirm & Create", type="primary", use_container_width=True):
            try:
                # 1. Insert store
                supabase.table("stores").insert({
                    "store_id": client_data["store_id"],
                    "store_name": client_data["salon_name"],
                    "owner_name": client_data["owner_name"],
                    "owner_phone": client_data["owner_phone"],
                    "trial_start": client_data["trial_start"].isoformat(),
                    "trial_end": client_data["trial_end"].isoformat(),
                    "status": "active",
                    "plan_name": client_data["plan_option"]
                }).execute()

                # 2. Insert owner user
                supabase.table("users").insert({
                    "user_id": client_data["user_id"],
                    "username": client_data["username"],
                    "password_hash": hash_password(client_data["password"]),
                    "role": "client",
                    "store_id": client_data["store_id"],
                    "name": client_data["owner_name"],
                    "status": "active"
                }).execute()

                # 3. Seed initial starter services
                starter_services = [
                    {"service_id": f"SRV-{uuid.uuid4().hex[:5].upper()}", "store_id": client_data["store_id"], "service_name": "Haircut & Styling", "price": 200},
                    {"service_id": f"SRV-{uuid.uuid4().hex[:5].upper()}", "store_id": client_data["store_id"], "service_name": "Beard Grooming", "price": 120},
                    {"service_id": f"SRV-{uuid.uuid4().hex[:5].upper()}", "store_id": client_data["store_id"], "service_name": "Facial Clean-up", "price": 500},
                ]
                supabase.table("services").insert(starter_services).execute()

                st.success(f"🎉 Salon '{client_data['salon_name']}' successfully registered!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to register client: {e}")

    with col_cancel:
        if st.button("❌ Cancel / Edit", use_container_width=True):
            st.rerun()

# =========================================================
# MODAL DIALOG: EDIT SALON, OWNER, & CREDENTIALS
# =========================================================
@st.dialog("✏️ Edit Salon Client & Login Credentials")
def edit_salon_modal(store):
    s_id = store["store_id"]
    current_name = store.get("store_name", "")
    current_owner = store.get("owner_name", "")
    current_phone = store.get("owner_phone", "")
    current_plan = store.get("plan_name", "Free Trial - 30 Days")
    
    # Query owner account from users table
    owner_user_res = supabase.table("users").select("user_id, username").eq("store_id", s_id).eq("role", "client").execute()
    owner_user_data = owner_user_res.data[0] if owner_user_res.data else {}
    current_uid = owner_user_data.get("user_id", "N/A")
    current_username = owner_user_data.get("username", "")

    try:
        current_expiry = datetime.strptime(store.get("trial_end", ""), "%Y-%m-%d").date()
    except Exception:
        current_expiry = date.today()

    st.markdown(f"**Store ID:** `{s_id}` &nbsp;|&nbsp; **User Internal ID:** `{current_uid}`")
    
    with st.form(f"edit_form_{s_id}"):
        st.markdown("##### 🏢 Salon Information")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            edit_name = st.text_input("Salon / Business Name *", value=current_name).strip()
            edit_owner = st.text_input("Owner Full Name *", value=current_owner).strip()
        with col_s2:
            edit_phone = st.text_input("Owner Mobile Number (10 Digits) *", value=current_phone).strip()

        col_p, col_d = st.columns(2)
        with col_p:
            plan_choices = [
                "Free Trial - 30 Days",
                "Quarterly - 3 Months (90 Days)",
                "Half-Yearly - 6 Months (180 Days)",
                "Annual - 1 Year (365 Days)",
                "Custom Plan"
            ]
            default_p_idx = plan_choices.index(current_plan) if current_plan in plan_choices else 4
            edit_plan = st.selectbox("Assigned Plan", plan_choices, index=default_p_idx)
        with col_d:
            edit_expiry = st.date_input("Plan Expiry Date", value=current_expiry)

        st.write("---")
        st.markdown("##### 🔑 Login Credentials")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            edit_username = st.text_input("Owner Login Username *", value=current_username).strip()
        with col_u2:
            edit_password = st.text_input("Set New Password (leave blank to keep current)", type="password", placeholder="Enter new password to change")

        st.caption("ℹ️ Note: Database passwords are encrypted with SHA-256. To reset this client's password, type a new password above.")

        btn_save = st.form_submit_button("💾 Save All Changes", use_container_width=True)

        if btn_save:
            clean_p = clean_phone_number(edit_phone)
            if not edit_name or not edit_owner or not edit_phone or not edit_username:
                st.error("Please fill in all mandatory fields.")
            elif len(clean_p) != 10:
                st.error("Invalid Mobile Number! Please enter a valid 10-digit number.")
            elif edit_password and len(edit_password) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                if edit_username != current_username:
                    dup_chk = supabase.table("users").select("username").eq("username", edit_username).execute()
                    if dup_chk.data:
                        st.error(f"Username '{edit_username}' is already taken by another account.")
                        return

                try:
                    # 1. Update Store Record
                    supabase.table("stores").update({
                        "store_name": edit_name,
                        "owner_name": edit_owner,
                        "owner_phone": clean_p,
                        "plan_name": edit_plan,
                        "trial_end": edit_expiry.isoformat()
                    }).eq("store_id", s_id).execute()

                    # 2. Update Owner Record in Users Table
                    user_update_payload = {
                        "name": edit_owner,
                        "username": edit_username
                    }
                    if edit_password:
                        user_update_payload["password_hash"] = hash_password(edit_password)

                    if owner_user_data:
                        supabase.table("users").update(user_update_payload).eq("user_id", current_uid).execute()
                    else:
                        supabase.table("users").update(user_update_payload).eq("store_id", s_id).eq("role", "client").execute()

                    st.toast("✅ Salon details and credentials saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update details: {e}")

# =========================================================
# PAGE: TRENDING HAIRCUTS LOOKBOOK GALLERY
# =========================================================
if st.session_state.current_page == "lookbook":
    st.markdown("<h2 style='font-weight:800;'>💇 Fresh & Trending Men's Haircuts & Grooming</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Showcase these trending styles to your walk-in clients so they can effortlessly choose their next look.</p>", unsafe_allow_html=True)

    styles_catalog = [
        {
            "name": "Textured Modern Crop & High Fade",
            "category": "Urban Short / Modern",
            "desc": "Short blunt fringe with textured layers on top and a skin-tight high fade. Low maintenance, sharp look.",
            "face_shape": "Oval, Round, Square",
            "img": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=700&q=80"
        },
        {
            "name": "Classic Slicked Pompadour & Fade",
            "category": "Timeless Executive",
            "desc": "High volume top brushed upward and back, paired with a neat mid taper fade. Highly elegant.",
            "face_shape": "Oval, Heart",
            "img": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=700&q=80"
        },
        {
            "name": "Messy Textured Quiff + Clean Taper",
            "category": "Casual / Party",
            "desc": "Effortless, natural texture with medium top length and a soft scissor/clipper taper. Easy to style with matte clay.",
            "face_shape": "Round, Square",
            "img": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=700&q=80"
        },
        {
            "name": "Curly Drop Fade & Beard Shape",
            "category": "Curls & Volume",
            "desc": "Maintains natural curly bounce on top while dropping cleanly behind the ear into a shaped luxury beard.",
            "face_shape": "Oval, Diamond",
            "img": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=700&q=80"
        },
        {
            "name": "Clean Buzz Fade + Line Up",
            "category": "Athletic / Minimalist",
            "desc": "Precision razor-edge line up with a uniform buzz on top and a seamless gradient skin fade.",
            "face_shape": "Square, Chiseled",
            "img": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=700&q=80"
        },
        {
            "name": "Sleek Side-Part Comb Over",
            "category": "Corporate / Professional",
            "desc": "A defined surgical or natural part with a clean side sweep. Perfectly suited for formal occasions.",
            "face_shape": "All Face Shapes",
            "img": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=700&q=80"
        }
    ]

    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]

    for idx, item in enumerate(styles_catalog):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="haircut-card">
                <img src="{item['img']}" alt="{item['name']}">
                <div class="haircut-info">
                    <span style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#D4A338;">{item['category']}</span>
                    <h3 style="margin: 6px 0; font-size: 1.25rem;">{item['name']}</h3>
                    <p style="color: #64748B; font-size: 0.88rem; line-height: 1.4; margin-bottom: 8px;">{item['desc']}</p>
                    <div style="font-size: 0.82rem; font-weight: 600; color: #0F172A;">
                        Best For: <span style="font-weight: 400; color: #475569;">{item['face_shape']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# SUPER ADMIN: CLIENT ONBOARDING & SUBSCRIPTION MANAGER
# =========================================================
elif role == "admin" and st.session_state.current_page == "admin_clients":
    st.markdown("<h2 style='font-weight:700;'>🏢 Salon Client Licensing & Activation</h2>", unsafe_allow_html=True)

    tab_list, tab_create = st.tabs(["📋 Registered Salon Stores & Access Control", "➕ Onboard New Salon Client"])

    # --- TAB 1: MANAGE STORES, ACTIVE/INACTIVE & EDIT DETAILS ---
    with tab_list:
        st.subheader("Salon Accounts & Live Subscription Status")
        stores_res = supabase.table("stores").select("*").order("trial_end", desc=False).execute().data
        
        if stores_res:
            for store in stores_res:
                s_id = store["store_id"]
                s_name = store.get("store_name", "Unnamed Salon")
                s_owner = store.get("owner_name", "N/A")
                s_phone = store.get("owner_phone", "N/A")
                s_status = store.get("status", "active")
                s_plan = store.get("plan_name", "Custom Plan")
                s_end = store.get("trial_end", "N/A")

                # Visual status styling
                is_active = (s_status == "active")
                status_badge = "🟢 ACTIVE" if is_active else "🔴 INACTIVE"
                border_color = "#D4A338" if is_active else "#EF4444"

                with st.container():
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left: 6px solid {border_color}; padding:16px 20px; border-radius:10px; margin-bottom:12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; font-size:1.25rem; color:#0F172A;">{s_name} <span style="font-size:0.85rem; font-weight:700; margin-left:10px;">{status_badge}</span></h3>
                                <p style="margin:4px 0 0 0; color:#64748B; font-size:0.9rem;">
                                    <b>Owner:</b> {s_owner} | <b>Phone:</b> {s_phone} | <b>Plan:</b> {s_plan} | <b>Expires:</b> {s_end}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 2])
                    with c_btn1:
                        if is_active:
                            if st.button(f"⛔ Deactivate Store", key=f"deact_{s_id}", use_container_width=True):
                                supabase.table("stores").update({"status": "inactive"}).eq("store_id", s_id).execute()
                                st.toast(f"Deactivated {s_name}!")
                                st.rerun()
                        else:
                            if st.button(f"✅ Activate Store", key=f"act_{s_id}", use_container_width=True):
                                supabase.table("stores").update({"status": "active"}).eq("store_id", s_id).execute()
                                st.toast(f"Activated {s_name}!")
                                st.rerun()

                    with c_btn2:
                        if st.button("✏️ Edit Details & Password", key=f"edit_btn_{s_id}", use_container_width=True):
                            edit_salon_modal(store)

                    with c_btn3:
                        if st.button(f"➕ Extend 30 Days", key=f"ext_{s_id}", use_container_width=True):
                            try:
                                curr_end = datetime.strptime(s_end, "%Y-%m-%d").date()
                            except Exception:
                                curr_end = date.today()
                            new_end = max(curr_end, date.today()) + timedelta(days=30)
                            supabase.table("stores").update({"trial_end": new_end.isoformat()}).eq("store_id", s_id).execute()
                            st.toast(f"Extended {s_name} until {new_end}!")
                            st.rerun()

                    st.write("")
        else:
            st.info("No salon stores registered yet. Click 'Onboard New Salon Client' tab to add your first client.")

    # --- TAB 2: ONBOARD NEW CLIENT WITH VALIDATIONS & CONFIRMATION POPUP ---
    with tab_create:
        st.subheader("Register a New Salon & Set Plan")
        with st.form("add_client_form", clear_on_submit=False):
            col_a, col_b = st.columns(2)
            with col_a:
                salon_name = st.text_input("Salon / Business Name *", placeholder="e.g. Royal Unisex Salon").strip()
                owner_name = st.text_input("Owner Full Name *", placeholder="e.g. Ramesh Kumar").strip()
                owner_phone = st.text_input("Owner Mobile Number (10 Digits) *", placeholder="e.g. 9876543210").strip()
            with col_b:
                client_username = st.text_input("Owner Login Username *", placeholder="e.g. royal_salon_pune").strip()
                client_password = st.text_input("Owner Login Password (min 6 chars) *", type="password")
                plan_option = st.selectbox("Subscription Plan Validity", [
                    "Free Trial - 30 Days",
                    "Quarterly - 3 Months (90 Days)",
                    "Half-Yearly - 6 Months (180 Days)",
                    "Annual - 1 Year (365 Days)"
                ])

            plan_days_map = {
                "Free Trial - 30 Days": 30,
                "Quarterly - 3 Months (90 Days)": 90,
                "Half-Yearly - 6 Months (180 Days)": 180,
                "Annual - 1 Year (365 Days)": 365
            }

            submit_onboard = st.form_submit_button("🚀 Create Client Account", use_container_width=True)

        if submit_onboard:
            if not salon_name or not owner_name or not owner_phone or not client_username or not client_password:
                st.error("❌ Please fill in all mandatory fields.")
            elif len(clean_phone_number(owner_phone)) != 10:
                st.error("❌ Invalid Mobile Number! Please enter a valid 10-digit mobile number.")
            elif len(client_password) < 6:
                st.error("❌ Password is too short! Please enter at least 6 characters.")
            else:
                existing_user = supabase.table("users").select("username").eq("username", client_username).execute()
                if existing_user.data:
                    st.error(f"❌ Username '{client_username}' is already taken! Please choose a different username.")
                else:
                    t_start = date.today()
                    t_end = t_start + timedelta(days=plan_days_map[plan_option])
                    client_payload = {
                        "store_id": f"STORE-{uuid.uuid4().hex[:6].upper()}",
                        "user_id": f"U{uuid.uuid4().hex[:5].upper()}",
                        "salon_name": salon_name,
                        "owner_name": owner_name,
                        "owner_phone": clean_phone_number(owner_phone),
                        "username": client_username,
                        "password": client_password,
                        "plan_option": plan_option,
                        "trial_start": t_start,
                        "trial_end": t_end
                    }
                    confirm_client_modal(client_payload)

# =========================================================
# CLIENT / WORKER: HOME POS & BILLING (MULTI-SERVICE SELECTION)
# =========================================================
elif st.session_state.current_page == "home":
    today_str = date.today().isoformat()
    first_of_month = date.today().replace(day=1).isoformat()

    txns_data = supabase.table("transactions").select("*").eq("store_id", store_id).execute().data
    txns_df = pd.DataFrame(txns_data)

    today_sales, month_sales, today_entries = 0.0, 0.0, 0
    if not txns_df.empty:
        txns_df["amount"] = pd.to_numeric(txns_df["amount"], errors="coerce")
        txns_df["date"] = pd.to_datetime(txns_df["timestamp"]).dt.strftime("%Y-%m-%d")
        
        today_records = txns_df[txns_df["date"] == today_str]
        today_sales = today_records["amount"].sum()
        today_entries = len(today_records)

        month_records = txns_df[txns_df["date"] >= first_of_month]
        month_sales = month_records["amount"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Today's Customers", today_entries)
    m2.metric("Today's Total Sales", f"₹ {today_sales:,.2f}")
    m3.metric("Current Month Sales", f"₹ {month_sales:,.2f}")

    st.write("---")

    col_entry, col_view = st.columns([1.1, 1.4])

    staff_res = supabase.table("users").select("name").eq("store_id", store_id).execute().data
    staff_options = [s["name"] for s in staff_res] if staff_res else [user["name"]]
    default_staff_idx = staff_options.index(user["name"]) if user["name"] in staff_options else 0

    services_res = supabase.table("services").select("service_name, price").eq("store_id", store_id).execute().data
    services_dict = {item["service_name"]: float(item["price"]) for item in services_res} if services_res else {"Basic Haircut": 150.0}
    service_names = list(services_dict.keys())

    # Multi-service auto-calculation sync
    def sync_multi_services():
        selected = st.session_state.selected_services_list
        calc_total = sum(services_dict.get(s, 0.0) for s in selected)
        st.session_state.service_amount_input = calc_total

    if "selected_services_list" not in st.session_state:
        st.session_state.selected_services_list = [service_names[0]] if service_names else []
    if "service_amount_input" not in st.session_state:
        st.session_state.service_amount_input = services_dict.get(service_names[0], 0.0) if service_names else 0.0

    with col_entry:
        st.subheader("⚡ Quick POS Entry")
        c_staff, c_cust = st.columns(2)
        with c_staff:
            worker_selected = st.selectbox("Staff / Stylist", staff_options, index=default_staff_idx)
        with c_cust:
            customer = st.text_input("Customer Name / Mobile *", placeholder="e.g. Amit Sharma")

        # Multi-select component allowing 1 or more services
        selected_services = st.multiselect(
            "Services Performed (Select 1 or more)",
            options=service_names,
            default=st.session_state.selected_services_list,
            key="selected_services_list",
            on_change=sync_multi_services,
            placeholder="Choose services..."
        )

        c_amt, c_pay = st.columns(2)
        with c_amt:
            amount = st.number_input(
                "Total Amount (₹) [Auto-Calculated]",
                min_value=0.0,
                step=50.0,
                key="service_amount_input",
                help="Sum of selected services. You can edit this amount for custom pricing/discounts."
            )
        with c_pay:
            payment = st.selectbox("Payment Mode", ["UPI", "Cash", "Card"])

        if st.button("💾 Record & Save Bill", use_container_width=True):
            if not customer:
                st.error("Please enter a customer name or mobile number.")
            elif not selected_services:
                st.error("Please select at least one service.")
            elif amount <= 0:
                st.error("Please enter a valid bill amount.")
            else:
                combined_services = ", ".join(selected_services)
                new_txn = {
                    "txn_id": f"TXN-{uuid.uuid4().hex[:6].upper()}",
                    "store_id": store_id,
                    "logged_by_user": user["username"],
                    "worker_name": worker_selected,
                    "customer_name": customer,
                    "service": combined_services,
                    "amount": amount,
                    "payment_mode": payment
                }
                supabase.table("transactions").insert(new_txn).execute()
                st.toast(f"✅ Saved: ₹{amount} for {customer}", icon="🎉")
                st.rerun()

    with col_view:
        st.subheader("📋 Today's Entries")
        if not txns_df.empty:
            today_view = txns_df[txns_df["date"] == today_str]
            if role == "worker":
                today_view = today_view[today_view["worker_name"] == user["name"]]
            if not today_view.empty:
                st.dataframe(today_view[["timestamp", "customer_name", "service", "worker_name", "amount", "payment_mode"]], use_container_width=True, hide_index=True)
            else:
                st.info("No bills entered today yet.")
        else:
            st.info("No transactions logged yet.")

# =========================================================
# EXPENSES PAGE
# =========================================================
elif st.session_state.current_page == "expenses" and role in ["admin", "client"]:
    st.markdown("<h2 style='font-weight:700;'>💸 Store Expenses & Purchases</h2>", unsafe_allow_html=True)
    col_exp_form, col_exp_list = st.columns([1, 1.4])

    with col_exp_form:
        st.subheader("Log an Expense")
        category = st.selectbox("Expense Category", [
            "Salon Material / Supplies", 
            "Shop Rent", 
            "Employee Salary", 
            "Electricity & Utilities", 
            "Maintenance & Repairs",
            "Other"
        ])
        desc = st.text_input("Expense Description / Vendor", placeholder="e.g. Shampoo stock, Monthly shop rent")
        exp_amount = st.number_input("Amount Paid (₹)", min_value=0.0, step=100.0)
        exp_date = st.date_input("Date", value=date.today())

        if st.button("Record Expense", use_container_width=True):
            if exp_amount <= 0:
                st.error("Please enter a valid amount.")
            else:
                new_exp = {
                    "expense_id": f"EXP-{uuid.uuid4().hex[:6].upper()}",
                    "store_id": store_id,
                    "category": category,
                    "description": desc if desc else category,
                    "amount": exp_amount,
                    "expense_date": exp_date.isoformat(),
                    "logged_by": user["username"]
                }
                supabase.table("expenses").insert(new_exp).execute()
                st.toast("Expense logged successfully!")
                st.rerun()

    with col_exp_list:
        st.subheader("Expense Breakdown")
        exp_res = supabase.table("expenses").select("*").eq("store_id", store_id).order("expense_date", desc=True).execute().data
        if exp_res:
            exp_df = pd.DataFrame(exp_res)
            exp_df["amount"] = exp_df["amount"].astype(float)
            st.metric("Total Expenses Logged", f"₹ {exp_df['amount'].sum():,.2f}")
            
            cat_summary = exp_df.groupby("category")["amount"].sum().reset_index()
            cat_summary.columns = ["Category", "Total (₹)"]
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
            st.write("---")
            st.dataframe(exp_df[["expense_date", "category", "description", "amount", "logged_by"]], use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded yet.")

# =========================================================
# STORE CONFIG (RATES & STAFF)
# =========================================================
elif st.session_state.current_page == "settings" and role in ["admin", "client"]:
    st.markdown("<h2 style='font-weight:700;'>⚙️ Store Configuration</h2>", unsafe_allow_html=True)
    tab_serv, tab_emp = st.tabs(["💇 Services & Rates Catalog", "👥 Employees / Staff"])

    with tab_serv:
        st.subheader("Custom Services & Auto-Fill Rates")
        services_db = supabase.table("services").select("*").eq("store_id", store_id).execute().data
        if services_db:
            s_df = pd.DataFrame(services_db)
            st.dataframe(s_df[["service_name", "price"]], use_container_width=True, hide_index=True)
            del_serv = st.selectbox("Select Service to Remove", s_df["service_name"].tolist())
            if st.button("Delete Service"):
                supabase.table("services").delete().eq("store_id", store_id).eq("service_name", del_serv).execute()
                st.rerun()

        st.write("---")
        st.subheader("➕ Add New Service Rate")
        c1, c2 = st.columns(2)
        with c1:
            new_sname = st.text_input("Service Name (e.g. Keratin Treatment)")
        with c2:
            new_sprice = st.number_input("Standard Rate (₹)", min_value=0.0, step=50.0)
        if st.button("Save Rate to Catalog"):
            if new_sname and new_sprice > 0:
                supabase.table("services").insert({
                    "service_id": f"SRV-{uuid.uuid4().hex[:5].upper()}",
                    "store_id": store_id,
                    "service_name": new_sname.strip(),
                    "price": new_sprice
                }).execute()
                st.rerun()

    with tab_emp:
        st.subheader("Salon Staff Accounts")
        staff_records = supabase.table("users").select("username, name, role, status").eq("store_id", store_id).execute().data
        if staff_records:
            st.dataframe(pd.DataFrame(staff_records), use_container_width=True, hide_index=True)
        with st.expander("➕ Add New Staff Account"):
            emp_name = st.text_input("Staff Full Name")
            emp_user = st.text_input("Staff Login Username")
            emp_pass = st.text_input("Staff Login Password", type="password")
            if st.button("Create Staff Login"):
                if emp_name and emp_user and emp_pass:
                    supabase.table("users").insert({
                        "user_id": f"U{uuid.uuid4().hex[:5].upper()}",
                        "username": emp_user.strip(),
                        "password_hash": hash_password(emp_pass),
                        "role": "worker",
                        "store_id": store_id,
                        "name": emp_name,
                        "status": "active"
                    }).execute()
                    st.rerun()

# ----------------- GLOBAL FOOTER BRANDING -----------------
st.markdown("""
<div class="brand-footer">
    Developed & Engineered by <span class="brand-highlight">Global Wealth International</span> • All Rights Reserved
</div>
""", unsafe_allow_html=True)