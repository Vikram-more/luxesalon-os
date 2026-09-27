import streamlit as st
from supabase import create_client, Client
import pandas as pd
import hashlib
from datetime import datetime, date, timedelta
import uuid
import re
import altair as alt

# ----------------- PAGE SETUP & THEME -----------------
st.set_page_config(
    page_title="LuxeSalon OS | Studio & Parlour Management",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #F8F9FB 0%, #F3F4F8 50%, #FAF7F2 100%);
        color: #1E293B;
    }
    
    h1, h2, h3, h4, h5, p, label, span {
        color: #1E293B !important;
    }
    
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #D4A338;
        padding: 16px 20px;
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

    div.stButton > button {
        background: linear-gradient(135deg, #E6B447 0%, #D4A338 100%) !important;
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        border: 1px solid #C49329 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.1rem !important;
        box-shadow: 0 2px 6px rgba(212, 163, 56, 0.3) !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #F5C55A 0%, #E6B447 100%) !important;
        color: #000000 !important;
        box-shadow: 0 4px 12px rgba(212, 163, 56, 0.45) !important;
        transform: translateY(-1px);
    }
    
    button[key*="logout"], button[key*="del_"], button[key*="rej_"] {
        background: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px solid #FCA5A5 !important;
    }
    button[key*="logout"]:hover, button[key*="del_"]:hover, button[key*="rej_"]:hover {
        background: #FECACA !important;
        color: #7F1D1D !important;
    }

    .user-profile-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #D4A338;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .pricing-card {
        background: #FFFFFF;
        border: 2px solid #D4A338;
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(212, 163, 56, 0.12);
        margin-bottom: 18px;
    }

    .receipt-box {
        background: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
    }

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

# ----------------- DB SETUP -----------------
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
    digits = re.sub(r"\D", "", phone_raw)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return digits

# ----------------- TRANSLATIONS -----------------
TRANSLATIONS = {
    "English": {
        "welcome_title": "Welcome to LuxeSalon OS",
        "welcome_subtitle": "Smart Salon & Beauty Parlour Suite",
        "portal_signin": "Portal Sign In",
        "select_salon_type": "Select Parlour / Salon Type",
        "username": "Username",
        "password": "Password",
        "btn_signin": "Sign In to Salon OS",
        "btn_request_access": "✨ Request New Salon Access / Get Started",
        "log_off": "Log Off",
        "nav_pos": "Billing POS",
        "nav_pnl": "Month PnL (Earnings vs Exp)",
        "nav_expenses": "Expenses",
        "nav_config": "Store Config",
        "nav_admin_txns": "Live Transactions",
        "nav_admin_salons": "Manage Salons & Parlours",
        "metric_today_cust": "Today's Customers",
        "metric_today_sales": "Today's Total Sales",
        "metric_month_sales": "Current Month Sales",
        "metric_my_today_sales": "My Sales Today",
        "metric_my_today_cust": "My Customers Today",
        "trend_7days": "Past 7 Days Earnings Trend",
        "emp_recognition": "Employee Sales & Recognition",
        "btn_reveal_top3": "Reveal Top 3 Performers & Celebrate",
        "quick_pos": "Quick POS Entry",
        "staff_stylist": "Staff / Stylist",
        "cust_name_mobile": "Customer Name / Mobile *",
        "services_rendered": "Services Rendered (Multi-Service)",
        "total_bill": "Total Bill (₹)",
        "payment_mode": "Payment Mode",
        "btn_save_sale": "🧾 Generate Bill & Confirm",
        "today_entries": "Today's Entries",
        "no_bills_today": "No bills entered today yet.",
        "pnl_title": "Current Month: Total Earnings vs Expenses",
        "total_rev": "Month Revenue (Earnings)",
        "total_exp": "Month Expenses Incurred",
        "net_profit": "Month Net Profit",
        "rev_by_mode": "Month Revenue by Payment Mode",
        "exp_by_cat": "Month Expenses by Category",
        "expenses_title": "Store Expenses & Purchases",
        "log_expense": "Log Expense",
        "exp_cat": "Category",
        "exp_desc": "Description / Notes",
        "exp_amount": "Amount (₹)",
        "exp_date": "Date",
        "btn_save_exp": "Save Expense",
        "exp_history": "Expense Records & Deletion",
        "store_config_title": "Store Configuration",
        "tab_services": "Services & Rates",
        "tab_employees": "Employees / Staff",
        "add_new_service": "Add New Service",
        "service_name": "Service Name",
        "standard_rate": "Standard Rate (₹)",
        "btn_save_service": "Save New Service Rate",
        "add_new_staff": "Add New Staff Stylist",
        "staff_full_name": "Stylist Full Name *",
        "staff_username": "Staff Login Username *",
        "staff_password": "Staff Login Password *",
        "btn_save_staff": "Submit Staff Account",
        "admin_txns_title": "Central Transactions Stream",
        "admin_txns_sub": "Live stream of customer billings across all registered salons and parlours.",
        "admin_salons_title": "Salons & Parlours Directory",
        "onboard_salon": "Onboard New Salon / Parlour",
        "btn_edit_info": "Edit Information",
        "btn_extend_30": "Extend 30 Days",
        "btn_delete_salon": "Delete Salon",
        "btn_save_changes": "Save Updated Information",
        "btn_cancel": "Cancel / Back",
        "celebration_modal_title": "Top 3 Star Performers Recognition",
        "celebration_sub": "Recognizing dedication, customer love, and outstanding sales performance.",
        "champ_1st": "1st Place Champion",
        "star_2nd": "2nd Place Star",
        "achiever_3rd": "3rd Place Achiever",
        "sales_delivered": "Total Sales Delivered",
        "clients_attended": "Clients Attended",
        "btn_close": "Close Window"
    },
    "हिन्दी (Hindi)": {
        "welcome_title": "लक्स सैलून ओएस में आपका स्वागत है",
        "welcome_subtitle": "स्मार्ट सैलून एवं ब्यूटी पार्लर प्रबंधन सॉफ्टवेयर",
        "portal_signin": "पोर्टल लॉगिन",
        "select_salon_type": "सैलून / पार्लर का प्रकार चुनें",
        "username": "यूज़रनेम (Username)",
        "password": "पासवर्ड (Password)",
        "btn_signin": "सैलून ओएस में लॉगिन करें",
        "btn_request_access": "✨ नए सैलून एक्सेस हेतु आवेदन करें",
        "log_off": "लॉग आउट करें",
        "nav_pos": "बिलिंग / नया बिल (POS)",
        "nav_pnl": "इस महीने का लाभ व हानि (PnL)",
        "nav_expenses": "दुकान के खर्चे",
        "nav_config": "दुकान सेटिंग",
        "nav_admin_txns": "लाइव बिलिंग लेनदेन",
        "nav_admin_salons": "सैलून और पार्लर प्रबंधन",
        "metric_today_cust": "आज के कुल ग्राहक",
        "metric_today_sales": "आज की कुल बिक्री",
        "metric_month_sales": "इस महीने की बिक्री",
        "metric_my_today_sales": "मेरी आज की बिक्री",
        "metric_my_today_cust": "मेरे आज के ग्राहक",
        "trend_7days": "पिछले 7 दिनों की कमाई का रुझान",
        "emp_recognition": "कर्मचारी बिक्री और सम्मान",
        "btn_reveal_top3": "🏆 टॉप 3 कर्मचारी देखें व सम्मानित करें",
        "quick_pos": "⚡ त्वरित ग्राहक बिलिंग",
        "staff_stylist": "स्टाफ / कारीगर चुनें",
        "cust_name_mobile": "ग्राहक का नाम / मोबाइल नंबर *",
        "services_rendered": "दी गई सेवाएं (Multi-Service चुनें)",
        "total_bill": "कुल बिल राशि (₹)",
        "payment_mode": "भुगतान माध्यम (Payment Mode)",
        "btn_save_sale": "🧾 बिल बनाएं व पुष्टि करें",
        "today_entries": "आज के बिल की सूची",
        "no_bills_today": "आज अभी तक कोई बिल दर्ज नहीं हुआ है।",
        "pnl_title": "चालू माह: कुल कमाई बनाम खर्चे (लाभ व हानि)",
        "total_rev": "माह की कुल कमाई",
        "total_exp": "माह के कुल खर्चे",
        "net_profit": "माह की शुद्ध बचत / लाभ",
        "rev_by_mode": "माह की भुगतान माध्यम अनुसार कमाई",
        "exp_by_cat": "माह के श्रेणी अनुसार खर्चे",
        "expenses_title": "दुकान के खर्चे और खरीदारी",
        "log_expense": "नया खर्चा दर्ज करें",
        "exp_cat": "खर्चे की श्रेणी",
        "exp_desc": "विवरण / सामान का नाम",
        "exp_amount": "राशि (₹)",
        "exp_date": "तारीख",
        "btn_save_exp": "खर्चा सेव करें",
        "exp_history": "खर्चों का रिकॉर्ड एवं हटाना",
        "store_config_title": "सैलून एवं स्टाफ सेटिंग्स",
        "tab_services": "सर्विस और रेट लिस्ट",
        "tab_employees": "स्टाफ / कर्मचारी",
        "add_new_service": "नई सर्विस जोड़ें",
        "service_name": "सर्विस का नाम",
        "standard_rate": "दर / रेट (₹)",
        "btn_save_service": "नई सर्विस रेट सेव करें",
        "add_new_staff": "नया स्टाफ सदस्य जोड़ें",
        "staff_full_name": "स्टाफ का पूरा नाम *",
        "staff_username": "लॉगिन यूज़रनेम *",
        "staff_password": "लॉगिन पासवर्ड *",
        "btn_save_staff": "स्टाफ खाता विवरण सबमिट करें",
        "admin_txns_title": "केंद्रीय लेनदेन नियंत्रण",
        "admin_txns_sub": "सभी सैलून और पार्लरों की लाइव बिलिंग।",
        "admin_salons_title": "सैलून और ब्यूटी पार्लर डायरेक्टरी",
        "onboard_salon": "नया सैलून / पार्लर जोड़ें",
        "btn_edit_info": "जानकारी बदलें (Edit)",
        "btn_extend_30": "30 दिन वैधता बढ़ाएं",
        "btn_delete_salon": "सैलून हटाएं (Delete)",
        "btn_save_changes": "बदलाव सेव करें",
        "btn_cancel": "रद्द करें / वापस",
        "celebration_modal_title": "सर्वश्रेष्ठ 3 कर्मचारियों का अभिनंदन",
        "celebration_sub": "मेहनत, बेहतरीन ग्राहक सेवा और शानदार बिक्री का सम्मान।",
        "champ_1st": "🥇 प्रथम स्थान विजेता",
        "star_2nd": "🥈 द्वितीय स्थान सितारा",
        "achiever_3rd": "🥉 तृतीय स्थान अचीवर",
        "sales_delivered": "कुल दर्ज बिक्री",
        "clients_attended": "अटेंड किए गए ग्राहक",
        "btn_close": "विंडो बंद करें"
    },
    "मराठी (Marathi)": {
        "welcome_title": "लक्स सलून ओएस मध्ये आपले स्वागत आहे",
        "welcome_subtitle": "स्मार्ट सलून आणि ब्युटी पार्लर व्यवस्थापन प्रणाली",
        "portal_signin": "पोर्टल लॉगिन",
        "select_salon_type": "सलून / पार्लरचा प्रकार निवडा",
        "username": "वापरकर्ता नाव (Username)",
        "password": "पासवर्ड (Password)",
        "btn_signin": "सलून ओएस मध्ये लॉगिन करा",
        "btn_request_access": "✨ नवीन सलून ॲक्सेससाठी अर्ज करा",
        "log_off": "लॉग आउट करा",
        "nav_pos": "बिलिंग / नवीन बिल (POS)",
        "nav_pnl": "चालू महिन्याचा नफा आणि तोटा (PnL)",
        "nav_expenses": "दुकानाचे खर्च",
        "nav_config": "दुकान सेटिंग्ज",
        "nav_admin_txns": "थेट व्यवहार प्रवाह",
        "nav_admin_salons": "सलून व पार्लर व्यवस्थापन",
        "metric_today_cust": "आजचे एकूण ग्राहक",
        "metric_today_sales": "आजची एकूण विक्री",
        "metric_month_sales": "या महिन्याची विक्री",
        "metric_my_today_sales": "माझी आजची विक्री",
        "metric_my_today_cust": "माझे आजचे ग्राहक",
        "trend_7days": "मागील ७ दिवसांचा कमाईचा आलेख",
        "emp_recognition": "कर्मचारी कामगिरी आणि सन्मान",
        "btn_reveal_top3": "🏆 सर्वोत्तम ३ कर्मचारी पहा व सन्मान करा",
        "quick_pos": "⚡ जलद बिलिंग नोंद",
        "staff_stylist": "स्टाफ / कारागीर निवडा",
        "cust_name_mobile": "ग्राहकाचे नाव / मोबाईल नंबर *",
        "services_rendered": "दिलेल्या सेवा (एकाधिक सेवा निवडा)",
        "total_bill": "एकूण बिल रक्कम (₹)",
        "payment_mode": "पेमेंट मोड (Payment Mode)",
        "btn_save_sale": "🧾 बिल तयार करा व पुष्टी करा",
        "today_entries": "आजच्या बिलांची यादी",
        "no_bills_today": "आज अजून एकही बिल नोंदवलेले नाही.",
        "pnl_title": "चालू महिना: एकूण कमाई आणि खर्च (नफा-तोटा)",
        "total_rev": "महिन्याची एकूण कमाई",
        "total_exp": "महिन्याचे एकूण खर्च",
        "net_profit": "महिन्याचा निव्वळ शिल्लक नफा",
        "rev_by_mode": "पेमेंट पद्धतीनुसार महिन्याची कमाई",
        "exp_by_cat": "प्रकारानुसार महिन्याचे खर्च",
        "expenses_title": "दुकानाचे खर्च व खरेदी",
        "log_expense": "नवीन खर्च नोंदवा",
        "exp_cat": "खर्चाचा प्रकार",
        "exp_desc": "तपशील / साहित्याचे नाव",
        "exp_amount": "रक्कम (₹)",
        "exp_date": "तारीख",
        "btn_save_exp": "खर्च जतन करा",
        "exp_history": "खर्चाची नोंद व डिलीट पर्याय",
        "store_config_title": "सलून आणि स्टाफ रचना",
        "tab_services": "सेवा आणि दरपत्रक",
        "tab_employees": "कर्मचारी वर्ग",
        "add_new_service": "नवीन सेवा जोडा",
        "service_name": "सेवेचे नाव",
        "standard_rate": "दर / किंमत (₹)",
        "btn_save_service": "नवीन सेवा दर जतन करा",
        "add_new_staff": "नवीन कर्मचारी जोडा",
        "staff_full_name": "कर्मचाऱ्याचे पूर्ण नाव *",
        "staff_username": "लॉगिन नाव (Username) *",
        "staff_password": "लॉगिन पासवर्ड *",
        "btn_save_staff": "कर्मचारी खाते सबमिट करा",
        "admin_txns_title": "केंद्रीय बिलिंग व्यवहार नियंत्रण",
        "admin_txns_sub": "सर्व सलून आणि पार्लर्सचे थेट बिलिंग.",
        "admin_salons_title": "सलून आणि ब्युटी पार्लर यादी",
        "onboard_salon": "नवीन सलून / पार्लर नोंदणी",
        "btn_edit_info": "माहिती बदला (Edit)",
        "btn_extend_30": "३० दिवस मुदत वाढवा",
        "btn_delete_salon": "सलून हटवा (Delete)",
        "btn_save_changes": "बदल जतन करा",
        "btn_cancel": "रद्द करा / मागे जा",
        "celebration_modal_title": "सर्वोत्कृष्ट ३ कर्मचाऱ्यांचा गौरव",
        "celebration_sub": "कष्ट, ग्राहकांचे समाधान आणि अप्रतिम विक्री कामगिरीचा गौरव.",
        "champ_1st": "🥇 प्रथम क्रमांक विजेता",
        "star_2nd": "🥈 द्वितीय क्रमांक स्टार",
        "achiever_3rd": "🥉 तृतीय क्रमांक अचिव्हर",
        "sales_delivered": "दिलेली एकूण विक्री",
        "clients_attended": "सेवा दिलेले ग्राहक",
        "btn_close": "खिडकी बंद करा"
    }
}

# ----------------- SESSION STATE -----------------
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "store_info" not in st.session_state:
    st.session_state.store_info = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "admin_editing_store_id" not in st.session_state:
    st.session_state.admin_editing_store_id = None
if "show_request_form" not in st.session_state:
    st.session_state.show_request_form = False
if "req_view_filter" not in st.session_state:
    st.session_state.req_view_filter = "pending"
if "pos_form_run_count" not in st.session_state:
    st.session_state.pos_form_run_count = 0

T = TRANSLATIONS[st.session_state.lang]

def render_language_bar():
    c_space, c_lang = st.columns([5.5, 2.5])
    with c_lang:
        lang_choice = st.selectbox(
            "🌐 भाषा / Language",
            options=["English", "हिन्दी (Hindi)", "मराठी (Marathi)"],
            index=["English", "हिन्दी (Hindi)", "मराठी (Marathi)"].index(st.session_state.lang),
            key="lang_select_box"
        )
        if lang_choice != st.session_state.lang:
            st.session_state.lang = lang_choice
            st.rerun()

# ----------------- MODAL DIALOGS -----------------
@st.dialog("🧾 Salon Bill Receipt & Confirmation")
def confirm_receipt_modal(bill_data):
    st.markdown("""
    <div style="text-align: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 12px;">
        <h3 style="margin: 0; color: #B45309;">✨ LUXE SALON RECEIPT ✨</h3>
        <p style="margin: 2px 0 0 0; color: #64748B; font-size: 0.85rem;">Official Customer Service Invoice</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Customer:** {bill_data['customer_name']}")
        st.write(f"**Stylist / Staff:** {bill_data['worker_name']}")
    with c2:
        st.write(f"**Date:** {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
        st.write(f"**Payment:** {bill_data['payment_mode']}")

    st.write("---")
    st.markdown("##### ✂️ Services Rendered")
    
    # Table of services and amounts
    service_items = bill_data["services_breakdown"]
    df_receipt = pd.DataFrame(service_items)
    df_receipt.columns = ["Service Item", "Rate (₹)"]
    st.dataframe(df_receipt, use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div style="text-align: right; background: #F8FAFC; padding: 12px 16px; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 8px;">
        <span style="font-size: 1.1rem; color: #64748B;">Total Amount Payable:</span> 
        <span style="font-size: 1.5rem; font-weight: 800; color: #0F172A; margin-left: 10px;">₹ {bill_data['amount']:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    c_save, c_cancel = st.columns(2)
    with c_save:
        if st.button("✅ Confirm & Save Sale", type="primary", use_container_width=True):
            try:
                supabase.table("transactions").insert({
                    "txn_id": f"TXN-{uuid.uuid4().hex[:6].upper()}",
                    "store_id": bill_data["store_id"],
                    "logged_by_user": bill_data["logged_by_user"],
                    "worker_name": bill_data["worker_name"],
                    "customer_name": bill_data["customer_name"],
                    "service": bill_data["service_str"],
                    "amount": bill_data["amount"],
                    "payment_mode": bill_data["payment_mode"]
                }).execute()

                st.session_state.pos_form_run_count += 1
                st.toast("✅ Transaction confirmed and saved to database!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to record transaction: {e}")

    with c_cancel:
        if st.button("❌ Edit / Go Back", use_container_width=True):
            st.rerun()

@st.dialog("✏️ Edit Service & Pricing")
def edit_service_modal(srv):
    st.markdown(f"### Update Service: **{srv['service_name']}**")
    with st.form("edit_service_dialog_form"):
        new_name = st.text_input("Service Name *", value=srv["service_name"]).strip()
        new_price = st.number_input("Standard Rate (₹) *", min_value=0.0, value=float(srv.get("price", 0.0)), step=20.0)
        c_up, c_can = st.columns(2)
        with c_up:
            up_btn = st.form_submit_button("💾 Update Service", use_container_width=True)
        with c_can:
            can_btn = st.form_submit_button("Cancel", use_container_width=True)

    if can_btn:
        st.rerun()

    if up_btn:
        if not new_name or new_price <= 0:
            st.error("Please enter a valid service name and price.")
        else:
            supabase.table("services").update({
                "service_name": new_name,
                "price": new_price
            }).eq("service_id", srv["service_id"]).execute()
            st.toast("Service updated successfully!")
            st.rerun()

@st.dialog("✅ Provision & Activate Client Salon")
def accept_request_modal(req):
    st.markdown(f"### Activating: **{req['shop_name']}**")
    st.markdown(f"**Owner:** {req['owner_name']} | **Phone:** +91 {req['owner_phone']}")
    with st.form(f"provision_req_form_{req['request_id']}"):
        col_u, col_p = st.columns(2)
        with col_u:
            prov_user = st.text_input("Owner Login Username *", value=req.get("preferred_username", req['shop_name'].lower().replace(" ", "_"))).strip()
        with col_p:
            prov_pass = st.text_input("Initial Secret Password *", value="Salon@1234")

        plan_sel = st.selectbox("Assign Subscription Plan", [
            "Basic - ₹300 / Month",
            "Quarterly - 90 Days",
            "Annual - 365 Days",
            "Free Trial - 30 Days"
        ], index=0)

        c_submit, c_cancel = st.columns(2)
        with c_submit:
            confirm_btn = st.form_submit_button("🚀 Activate & Create Salon", use_container_width=True)
        with c_cancel:
            cancel_btn = st.form_submit_button("Cancel", use_container_width=True)

    if cancel_btn:
        st.rerun()

    if confirm_btn:
        if not prov_user or not prov_pass:
            st.error("Please provide both username and password.")
        else:
            chk = supabase.table("users").select("username").eq("username", prov_user).execute().data
            if chk:
                st.error(f"Username '{prov_user}' is already taken.")
            else:
                try:
                    new_store_id = f"STORE-{uuid.uuid4().hex[:6].upper()}"
                    new_user_id = f"U{uuid.uuid4().hex[:5].upper()}"
                    days = 30 if ("30" in plan_sel or "300" in plan_sel) else (90 if "90" in plan_sel else 365)
                    tstart = date.today()
                    tend = tstart + timedelta(days=days)

                    supabase.table("stores").insert({
                        "store_id": new_store_id,
                        "store_name": req["shop_name"],
                        "salon_type": req["salon_type"],
                        "owner_name": req["owner_name"],
                        "owner_phone": req["owner_phone"],
                        "trial_start": tstart.isoformat(),
                        "trial_end": tend.isoformat(),
                        "status": "active",
                        "plan_name": plan_sel
                    }).execute()

                    supabase.table("users").insert({
                        "user_id": new_user_id,
                        "username": prov_user,
                        "password_hash": hash_password(prov_pass),
                        "role": "client",
                        "store_id": new_store_id,
                        "name": req["owner_name"],
                        "status": "active"
                    }).execute()

                    if "Women" in req["salon_type"]:
                        starter = [
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Haircut & Blowdry", "price": 400},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Fruit / Gold Facial", "price": 850},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Full Arms Waxing", "price": 300},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Threading & Eyebrows", "price": 80}
                        ]
                    elif "Men" in req["salon_type"]:
                        starter = [
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Haircut & Styling", "price": 200},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Beard Grooming & Shape", "price": 120},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Facial Clean-up", "price": 500},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Head Massage & Wash", "price": 250}
                        ]
                    else:
                        starter = [
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Men Haircut & Style", "price": 200},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Women Haircut & Blowdry", "price": 450},
                            {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": new_store_id, "service_name": "Facial & Glow Treatment", "price": 800}
                        ]
                    supabase.table("services").insert(starter).execute()

                    supabase.table("access_requests").update({"status": "accepted"}).eq("request_id", req["request_id"]).execute()
                    st.success(f"🎉 Salon '{req['shop_name']}' successfully activated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to activate salon: {e}")

@st.dialog("📋 Confirm New Salon Registration")
def confirm_new_salon_modal(p):
    st.markdown("### Please verify the salon account details:")
    summary = {
        "Salon / Shop Name": p["salon_name"],
        "Category": p["salon_type"],
        "Owner Full Name": p["owner_name"],
        "10-Digit Mobile": f"+91 {p['owner_phone']}",
        "Owner Username": p["username"],
        "Initial Password": "•" * len(p["password"]),
        "Plan Option": p["plan_opt"],
        "Validity Ends": str(p["trial_end"])
    }
    st.dataframe(pd.DataFrame(list(summary.items()), columns=["Field", "Details"]), use_container_width=True, hide_index=True)
    st.write("---")
    
    c_yes, c_no = st.columns(2)
    with c_yes:
        if st.button("✅ Confirm & Create Salon", type="primary", use_container_width=True):
            try:
                supabase.table("stores").insert({
                    "store_id": p["store_id"],
                    "store_name": p["salon_name"],
                    "salon_type": p["salon_type"],
                    "owner_name": p["owner_name"],
                    "owner_phone": p["owner_phone"],
                    "trial_start": p["trial_start"].isoformat(),
                    "trial_end": p["trial_end"].isoformat(),
                    "status": "active",
                    "plan_name": p["plan_opt"]
                }).execute()

                supabase.table("users").insert({
                    "user_id": p["user_id"],
                    "username": p["username"],
                    "password_hash": hash_password(p["password"]),
                    "role": "client",
                    "store_id": p["store_id"],
                    "name": p["owner_name"],
                    "status": "active"
                }).execute()

                if "Women" in p["salon_type"]:
                    starter = [
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Haircut & Blowdry", "price": 400},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Fruit / Gold Facial", "price": 850},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Full Arms Waxing", "price": 300},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Threading & Eyebrows", "price": 80}
                    ]
                elif "Men" in p["salon_type"]:
                    starter = [
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Haircut & Styling", "price": 200},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Beard Grooming & Shape", "price": 120},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Facial Clean-up", "price": 500},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Head Massage & Wash", "price": 250}
                    ]
                else:
                    starter = [
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Men Haircut & Style", "price": 200},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Women Haircut & Blowdry", "price": 450},
                        {"service_id": f"S{uuid.uuid4().hex[:4].upper()}", "store_id": p["store_id"], "service_name": "Facial & Glow Treatment", "price": 800}
                    ]
                supabase.table("services").insert(starter).execute()

                st.success(f"🎉 Salon '{p['salon_name']}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating salon: {e}")

    with c_no:
        if st.button("❌ Cancel / Edit", use_container_width=True):
            st.rerun()

@st.dialog("👤 Confirm New Staff Account")
def confirm_new_staff_modal(p):
    st.markdown("### Please review the staff member details:")
    summary = {
        "Staff Full Name": p["name"],
        "Staff Login Username": p["username"],
        "Role": "Stylist / Staff Worker",
        "Status": "Active"
    }
    st.dataframe(pd.DataFrame(list(summary.items()), columns=["Field", "Details"]), use_container_width=True, hide_index=True)
    st.write("---")

    c_yes, c_no = st.columns(2)
    with c_yes:
        if st.button("✅ Confirm & Create Staff", type="primary", use_container_width=True):
            try:
                supabase.table("users").insert({
                    "user_id": p["user_id"],
                    "username": p["username"],
                    "password_hash": hash_password(p["password"]),
                    "role": "worker",
                    "store_id": p["store_id"],
                    "name": p["name"],
                    "status": "active"
                }).execute()
                st.success(f"🎉 Staff account created for {p['name']}!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create staff account: {e}")

    with c_no:
        if st.button("❌ Cancel", use_container_width=True):
            st.rerun()

@st.dialog(f"💐 🏆 {T['celebration_modal_title']} 🏆 💐")
def show_top_performers_modal(txns_df):
    st.balloons()
    if txns_df.empty:
        st.info("No transaction data available yet.")
        return

    emp_rank = txns_df.groupby("worker_name").agg(
        Total_Sales=("amount", "sum"),
        Clients_Served=("customer_name", "count")
    ).reset_index().sort_values(by="Total_Sales", ascending=False)

    top_3 = emp_rank.head(3)
    medals = [T["champ_1st"], T["star_2nd"], T["achiever_3rd"]]
    flower_garlands = ["🌸 🌺 💐 🌷 🌻", "🌸 💐 🌷 🌺", "💐 🌷 🌸"]
    cheers_map = {
        "English": [
            "Extraordinary excellence and dedication! Your outstanding craftsmanship sets the gold standard for our studio. Keep shining! ✨",
            "Remarkable work and warm hospitality! Your commitment to customer delight makes our salon proud. Keep rocking! 🌟",
            "Superb effort and consistent service! Your talent and passion are truly appreciated by every customer. Keep climbing high! 🚀"
        ],
        "हिन्दी (Hindi)": [
            "असाधारण उत्कृष्टता और अटूट निष्ठा! आपकी शानदार कारीगरी हमारे स्टूडियो के लिए मिसाल है। ऐसे ही चमकते रहें! ✨",
            "उत्कृष्ट कार्य और मधुर आतिथ्य! ग्राहकों को खुश रखने का आपका समर्पण हमारे सैलून का गौरव बढ़ाता है। 🌟",
            "शानदार प्रयास और निरंतर बेहतरीन सेवा! आपकी प्रतिभा और लगन की हर ग्राहक दिल से सराहना करता है। 🚀"
        ],
        "मराठी (Marathi)": [
            "असामान्य कौशल्य आणि अतुलनीय समर्पण! तुमची कला आपल्या सलूनची शान वाढवते. असेच प्रगती करत राहा! ✨",
            "उत्कृष्ट काम आणि ग्राहकांशी आपुलकीचे नाते! तुमचे योगदान आपल्या सलूनचा अभिमान आहे. 🌟",
            "अथक परिश्रम आणि सातत्यपूर्ण दर्जेदार सेवा! प्रत्येक ग्राहक तुमच्या कौशल्याचे कौतुक करतो. 🚀"
        ]
    }
    cheers = cheers_map[st.session_state.lang]

    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 14px;'>
        <h3 style='margin:0; color:#B45309;'>🎉 {T['celebration_modal_title']} 🎉</h3>
        <p style='color:#64748B; font-size:0.92rem;'>{T['celebration_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    for idx, (_, row) in enumerate(top_3.iterrows()):
        medal_title = medals[idx] if idx < len(medals) else f"🌟 Rank {idx+1}"
        garland = flower_garlands[idx] if idx < len(flower_garlands) else "💐 🌸 💐"
        quote = cheers[idx] if idx < len(cheers) else "Great work!"

        st.markdown(f"""
        <div class="performer-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#0F172A;">{medal_title}: <span style="color:#B45309;">{row['worker_name']}</span></h4>
                <span style="font-size:1.15rem;">{garland}</span>
            </div>
            <p style="margin:6px 0 8px 0; font-size:0.95rem; color:#1E293B;">
                <b>{T['sales_delivered']}:</b> <span style="color:#059669; font-weight:800;">₹ {row['Total_Sales']:,.2f}</span> &nbsp;|&nbsp; 
                <b>{T['clients_attended']}:</b> <span style="font-weight:700;">{row['Clients_Served']}</span>
            </p>
            <p style="margin:0; font-size:0.87rem; font-style:italic; color:#475569; background:#F8FAFC; padding:8px 12px; border-radius:8px; border-left:4px solid #D4A338;">
                “{quote}”
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    if st.button(T["btn_close"], use_container_width=True):
        st.rerun()

# ----------------- PUBLIC REQUEST ACCESS PAGE -----------------
def render_request_access_page():
    render_language_bar()
    c_pad1, col_req, c_pad2 = st.columns([1, 2, 1])
    with col_req:
        if st.button("⬅️ Back to Sign In Screen"):
            st.session_state.show_request_form = False
            st.rerun()

        st.markdown("<div style='text-align: center; margin: 15px 0 10px 0;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size: 2.8rem;'>💎 ✂️ 💄</span>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #0F172A; margin-bottom: 4px; font-weight:800;'>Get LuxeSalon OS For Your Business</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 0.98rem;'>Affordable, modern digital POS and billing management for Salons & Beauty Parlours.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="pricing-card">
            <span style="background:#FEF3C7; color:#B45309; padding:5px 14px; border-radius:20px; font-size:0.85rem; font-weight:800; text-transform:uppercase;">
                🌟 Most Popular Starter Plan
            </span>
            <h1 style="color:#0F172A; margin:12px 0 0 0; font-size:2.4rem; font-weight:800;">₹ 300 <span style="font-size:1.1rem; color:#64748B; font-weight:500;">/ Month</span></h1>
            <p style="color:#475569; margin:6px 0 14px 0; font-size:0.95rem;">Full access to Men's Salon & Women's Beauty Parlour Suite</p>
            <div style="display:flex; justify-content:space-around; text-align:left; font-size:0.88rem; color:#1E293B; margin-top:10px;">
                <div>
                    <div>✅ Quick Multi-Service Billing POS</div>
                    <div>✅ Daily & Monthly Sales Analytics</div>
                    <div>✅ 7-Day Performance Trend Chart</div>
                </div>
                <div>
                    <div>✅ Employee Sales & Top 3 Stars</div>
                    <div>✅ Expense Tracking & Monthly PnL</div>
                    <div>✅ Multilingual (English / हिंदी / मराठी)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📝 Fill Your Salon & Contact Details")
        st.caption("Submit your information below. Your request will be directly queued in the Super Admin console for immediate contact and account activation:")

        with st.form("public_request_access_form", clear_on_submit=True):
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                req_shop_name = st.text_input("Salon / Shop / Parlour Name *", placeholder="e.g. Royal Hair Studio")
                req_cat = st.selectbox("Salon Category *", [
                    "Men's Salon & Grooming", 
                    "Women's Beauty Parlour", 
                    "Unisex Studio & Spa"
                ])
                req_owner_name = st.text_input("Owner Full Name *", placeholder="e.g. Ramesh Kumar")
                req_phone = st.text_input("Mobile Number (10 Digits) *", placeholder="e.g. 9876543210")
            
            with r_col2:
                req_staff = st.number_input("Number of Stylists / Staff *", min_value=1, max_value=50, value=2, step=1)
                req_plan = st.selectbox("Selected Subscription Plan", [
                    "Basic - ₹300 / Month",
                    "Quarterly - ₹850 / 3 Months (Save ₹50)",
                    "Annual - ₹3,000 / Year (Save ₹600)"
                ])
                req_user = st.text_input("Desired Login Username (Optional)", placeholder="e.g. royal_pune").strip()
                req_notes = st.text_input("Special Requirements / Questions", placeholder="e.g. Need help configuring our rate list")

            req_address = st.text_area("Complete Shop Address & City *", placeholder="e.g. Shop No. 4, MG Road, Camp, Pune, Maharashtra - 411001", height=80)
            submit_request = st.form_submit_button("🚀 Submit Request & Get Started", use_container_width=True)

        if submit_request:
            clean_p = clean_phone_number(req_phone)
            if not req_shop_name or not req_owner_name or not req_address or len(clean_p) != 10:
                st.error("❌ Please provide all mandatory fields (*) and a valid 10-digit mobile number.")
            else:
                lead_data = {
                    "request_id": f"REQ-{uuid.uuid4().hex[:6].upper()}",
                    "shop_name": req_shop_name.strip(),
                    "salon_type": req_cat,
                    "address": req_address.strip(),
                    "owner_name": req_owner_name.strip(),
                    "owner_phone": clean_p,
                    "num_staff": int(req_staff),
                    "selected_plan": req_plan,
                    "preferred_username": req_user if req_user else req_shop_name.lower().replace(" ", "_"),
                    "notes": req_notes.strip() if req_notes else "None",
                    "status": "pending"
                }

                try:
                    supabase.table("access_requests").insert(lead_data).execute()
                    st.success("🎉 Thank you! Your request has been queued successfully in the Admin Console.")
                    st.info("📞 Our administration team will contact you shortly on your registered mobile number to activate your portal login.")
                except Exception as e:
                    st.error(f"Could not submit request. Please try again: {e}")

# ----------------- LOGIN SCREEN -----------------
def login_screen():
    if st.session_state.show_request_form:
        render_request_access_page()
        return

    render_language_bar()
    c_pad1, col_login, c_pad2 = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size: 3rem;'>✨ ✂️ 💄 ✨</span>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color: #0F172A; font-size: 2.1rem; margin-bottom: 4px;'>{T['welcome_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748B; font-size: 1rem; margin-bottom: 20px;'>{T['welcome_subtitle']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            st.markdown(f"<h4 style='color: #0F172A; margin-bottom: 12px;'>{T['portal_signin']}</h4>", unsafe_allow_html=True)
            chosen_category = st.selectbox(T["select_salon_type"], [
                "Men's Salon & Grooming", 
                "Women's Beauty Parlour", 
                "Unisex Studio & Spa"
            ])
            username = st.text_input(T["username"]).strip()
            password = st.text_input(T["password"], type="password")
            btn = st.form_submit_button(T["btn_signin"], use_container_width=True)

            if btn:
                if not username or not password:
                    st.error("Please enter both username and password.")
                    return

                hashed = hash_password(password)
                resp = supabase.table("users").select("*").eq("username", username).eq("password_hash", hashed).execute()
                
                if resp.data:
                    user_data = resp.data[0]
                    store_obj = None

                    if user_data["role"] != "admin":
                        store_res = supabase.table("stores").select("*").eq("store_id", user_data["store_id"]).execute()
                        if not store_res.data:
                            st.error("Salon record not found.")
                            return
                        store_obj = store_res.data[0]
                        actual_cat = store_obj.get("salon_type", "Men's Salon & Grooming")

                        def norm_cat(c):
                            if "Women" in c: return "Women"
                            if "Men" in c: return "Men"
                            return "Unisex"

                        if norm_cat(chosen_category) != norm_cat(actual_cat):
                            st.error(f"⛔ Category Mismatch! This user account belongs to '{actual_cat}'. Please select the correct salon category above.")
                            return

                        if store_obj.get("status") != "active":
                            st.error("⛔ This salon store has been deactivated. Please contact administration.")
                            return
                        
                        trial_end = datetime.strptime(store_obj["trial_end"], "%Y-%m-%d").date()
                        if date.today() > trial_end:
                            st.error(f"⛔ Subscription expired on {trial_end}. Please renew.")
                            return

                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.store_info = store_obj
                    st.session_state.current_page = "admin_home" if user_data["role"] == "admin" else "home"
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        st.write("")
        if st.button(T["btn_request_access"], use_container_width=True):
            st.session_state.show_request_form = True
            st.rerun()

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
current_store = st.session_state.store_info
salon_cat = current_store.get("salon_type", "Men's Salon & Grooming") if current_store else "Men's Salon & Grooming"

def perform_logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.store_info = None
    st.session_state.current_page = "home"
    st.session_state.admin_editing_store_id = None
    st.session_state.show_request_form = False
    st.rerun()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown(f"### 👤 {user['name']}")
    st.markdown(f"**{T['username']}:** `{user['username']}`")
    st.markdown(f"**Role:** `{role.upper()}`")
    if current_store:
        st.markdown(f"**Store:** {current_store.get('store_name')}")
        st.caption(f"Category: {salon_cat}")
    st.caption("Engineered by **Global Wealth International**")
    st.write("---")
    if st.button(f"🚪 {T['log_off']}", key="sidebar_logout_btn", use_container_width=True):
        perform_logout()

# ----------------- TOP BAR: LANGUAGE SELECTOR & NAVIGATION -----------------
render_language_bar()

if role != "admin" and current_store:
    owner_label = "Owner" if role == "client" else "Stylist / Staff"
    st.markdown(f"""
    <div class="user-profile-header">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <h3 style="margin:0; color:#0F172A; font-weight:800; font-size:1.35rem;">
                    💈 {current_store.get('store_name')} 
                    <span style="font-size:0.85rem; background:#FEF3C7; color:#B45309; padding:4px 10px; border-radius:6px; font-weight:700; margin-left:8px;">{salon_cat}</span>
                </h3>
                <p style="margin:4px 0 0 0; color:#475569; font-size:0.92rem;">
                    👤 <b>User:</b> {user['name']} ({owner_label}) &nbsp;|&nbsp; 
                    🔑 <b>Username:</b> <code style="background:#F1F5F9; padding:2px 6px; border-radius:4px;">{user['username']}</code> &nbsp;|&nbsp; 
                    🆔 <b>User ID:</b> <code style="background:#F1F5F9; padding:2px 6px; border-radius:4px;">{user['user_id']}</code>
                </p>
            </div>
            <div style="text-align:right;">
                <span style="font-size:0.82rem; font-weight:700; color:#16A34A; background:#DCFCE7; padding:4px 10px; border-radius:6px;">🟢 ACTIVE SUBSCRIPTION</span>
                <p style="margin:4px 0 0 0; color:#64748B; font-size:0.85rem;">
                    Plan: <b>{current_store.get('plan_name', 'Custom Plan')}</b> | Expires: <b>{current_store.get('trial_end')}</b>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if role == "admin":
    nav1, nav2, nav3, nav4 = st.columns([4, 2.5, 2, 1.5])
    with nav1:
        st.markdown(f"<h3 style='margin:0; font-weight:800;'>✂️ Studio Central Console | {user['name']}</h3>", unsafe_allow_html=True)
    with nav2:
        if st.button(f"🧾 {T['nav_admin_txns']}", use_container_width=True):
            st.session_state.current_page = "admin_home"
            st.session_state.admin_editing_store_id = None
            st.rerun()
    with nav3:
        if st.button(f"🏢 {T['nav_admin_salons']}", use_container_width=True):
            st.session_state.current_page = "admin_salons"
            st.rerun()
    with nav4:
        if st.button(f"🚪 {T['log_off']}", key="top_admin_logout", use_container_width=True):
            perform_logout()

else:  # Salon Owner / Worker
    nav1, nav2, nav3, nav4, nav5 = st.columns([3, 2.5, 2, 2, 1.5])
    with nav1:
        if st.button(f"🏠 {T['nav_pos']}", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    with nav2:
        if role == "client":
            if st.button(f"📊 {T['nav_pnl']}", use_container_width=True):
                st.session_state.current_page = "pnl"
                st.rerun()
        else:
            st.empty()
    with nav3:
        if role == "client":
            if st.button(f"💸 {T['nav_expenses']}", use_container_width=True):
                st.session_state.current_page = "expenses"
                st.rerun()
        else:
            st.empty()
    with nav4:
        if role == "client":
            if st.button(f"⚙️ {T['nav_config']}", use_container_width=True):
                st.session_state.current_page = "settings"
                st.rerun()
        else:
            if st.button(f"🚪 {T['log_off']}", key="top_worker_logout", use_container_width=True):
                perform_logout()
    with nav5:
        if role == "client":
            if st.button(f"🚪 {T['log_off']}", key="top_user_logout", use_container_width=True):
                perform_logout()

st.write("---")

# =========================================================
# ADMIN: TRANSACTIONS & CENTRAL VIEW
# =========================================================
if role == "admin" and st.session_state.current_page == "admin_home":
    st.markdown(f"<h2 style='font-weight:700;'>🧾 {T['admin_txns_title']}</h2>", unsafe_allow_html=True)
    st.caption(T["admin_txns_sub"])

    stores_data = supabase.table("stores").select("store_id, store_name, salon_type").execute().data
    store_map = {s["store_id"]: f"{s['store_name']} ({s.get('salon_type', 'Men Salon')})" for s in stores_data} if stores_data else {}

    col_flt1, col_flt2 = st.columns([2, 2])
    with col_flt1:
        selected_store_filter = st.selectbox("Filter by Salon / Parlour", ["All Salons & Parlours"] + list(store_map.values()))

    query = supabase.table("transactions").select("*").order("timestamp", desc=True)
    if selected_store_filter != "All Salons & Parlours":
        inv_map = {v: k for k, v in store_map.items()}
        target_id = inv_map.get(selected_store_filter)
        if target_id:
            query = query.eq("store_id", target_id)

    tx_res = query.execute().data
    tx_df = pd.DataFrame(tx_res)

    today_str = date.today().isoformat()
    if not tx_df.empty:
        tx_df["amount"] = pd.to_numeric(tx_df["amount"], errors="coerce").fillna(0.0)
        tx_df["date"] = pd.to_datetime(tx_df["timestamp"]).dt.strftime("%Y-%m-%d")

        t_today = tx_df[tx_df["date"] == today_str]["amount"].sum()
        t_all = tx_df["amount"].sum()
        t_count = len(tx_df)

        m1, m2, m3 = st.columns(3)
        m1.metric(T["metric_today_sales"], f"₹ {t_today:,.2f}")
        m2.metric("Total Overall Transactions", t_count)
        m3.metric("Lifetime Volume", f"₹ {t_all:,.2f}")

        st.write("---")
        for _, tr in tx_df.iterrows():
            s_label = store_map.get(tr.get("store_id"), tr.get("store_id", "N/A"))
            with st.container():
                c1, c2, c3, c4 = st.columns([2.5, 3, 2, 1.5])
                with c1:
                    st.markdown(f"**{s_label}**")
                    st.caption(f"Time: {str(tr.get('timestamp'))[:19]}")
                with c2:
                    st.write(f"**Customer:** {tr.get('customer_name')} | **Stylist:** {tr.get('worker_name')}")
                    st.caption(f"Services: {tr.get('service')}")
                with c3:
                    st.markdown(f"### ₹ {tr.get('amount', 0):,.2f}")
                    st.caption(f"Payment: {tr.get('payment_mode')}")
                with c4:
                    if st.button("🗑️ Delete", key=f"del_tx_{tr['txn_id']}", use_container_width=True):
                        supabase.table("transactions").delete().eq("txn_id", tr["txn_id"]).execute()
                        st.toast(f"Removed transaction {tr['txn_id']}")
                        st.rerun()
                st.write("")
    else:
        st.info("No transactions logged yet.")

# =========================================================
# ADMIN: SALONS, PARLOURS, REQUEST PIPELINE (ACCEPT/REJECT)
# =========================================================
elif role == "admin" and st.session_state.current_page == "admin_salons":
    if st.session_state.admin_editing_store_id:
        edit_sid = st.session_state.admin_editing_store_id
        store_match = supabase.table("stores").select("*").eq("store_id", edit_sid).execute().data
        
        if not store_match:
            st.error("Salon record not found.")
            st.session_state.admin_editing_store_id = None
            st.rerun()

        curr_s = store_match[0]
        user_match = supabase.table("users").select("*").eq("store_id", edit_sid).eq("role", "client").execute().data
        curr_u = user_match[0] if user_match else {}

        st.subheader(f"✏️ {T['btn_edit_info']}: {curr_s.get('store_name')}")

        with st.form("admin_full_edit_form"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                cat_choices = ["Men's Salon & Grooming", "Women's Beauty Parlour", "Unisex Studio & Spa"]
                existing_cat = curr_s.get("salon_type", "Men's Salon & Grooming")
                cat_idx = cat_choices.index(existing_cat) if existing_cat in cat_choices else 0
                edit_cat = st.selectbox(T["select_salon_type"], cat_choices, index=cat_idx)
                edit_sname = st.text_input("Salon / Parlour Name *", value=curr_s.get("store_name", "")).strip()
                edit_oname = st.text_input("Owner Full Name *", value=curr_s.get("owner_name", "")).strip()
                edit_phone = st.text_input("Owner 10-Digit Mobile *", value=curr_s.get("owner_phone", "")).strip()

            with col_e2:
                edit_username = st.text_input(f"Owner {T['username']} *", value=curr_u.get("username", "")).strip()
                edit_password = st.text_input(f"Set New {T['password']} (leave blank to keep unchanged)", type="password")
                
                plan_choices = ["Free Trial - 30 Days", "Basic - ₹300 / Month", "Quarterly - 90 Days", "Annual - 365 Days", "Custom Plan"]
                existing_plan = curr_s.get("plan_name", "Free Trial - 30 Days")
                plan_idx = plan_choices.index(existing_plan) if existing_plan in plan_choices else 0
                edit_plan = st.selectbox("Subscription Plan", plan_choices, index=plan_idx)
                
                try:
                    exp_date = datetime.strptime(curr_s.get("trial_end", ""), "%Y-%m-%d").date()
                except Exception:
                    exp_date = date.today() + timedelta(days=30)
                edit_expiry = st.date_input("Plan Expiry Date", value=exp_date)

            c_save, c_cancel = st.columns(2)
            with c_save:
                btn_save_changes = st.form_submit_button(f"💾 {T['btn_save_changes']}", use_container_width=True)
            with c_cancel:
                btn_cancel_edit = st.form_submit_button(f"❌ {T['btn_cancel']}", use_container_width=True)

        if btn_cancel_edit:
            st.session_state.admin_editing_store_id = None
            st.rerun()

        if btn_save_changes:
            clean_p = clean_phone_number(edit_phone)
            if not edit_sname or not edit_oname or len(clean_p) != 10 or not edit_username:
                st.error("Please fill in valid required details.")
            elif edit_password and len(edit_password) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                supabase.table("stores").update({
                    "store_name": edit_sname,
                    "salon_type": edit_cat,
                    "owner_name": edit_oname,
                    "owner_phone": clean_p,
                    "plan_name": edit_plan,
                    "trial_end": edit_expiry.isoformat()
                }).eq("store_id", edit_sid).execute()

                user_updates = {
                    "name": edit_oname,
                    "username": edit_username
                }
                if edit_password:
                    user_updates["password_hash"] = hash_password(edit_password)

                if curr_u:
                    supabase.table("users").update(user_updates).eq("user_id", curr_u["user_id"]).execute()
                else:
                    supabase.table("users").update(user_updates).eq("store_id", edit_sid).eq("role", "client").execute()

                st.success("✅ Information updated successfully!")
                st.session_state.admin_editing_store_id = None
                st.rerun()

    else:
        st.markdown(f"<h2 style='font-weight:700;'>🏢 {T['admin_salons_title']}</h2>", unsafe_allow_html=True)
        tab_list, tab_requests, tab_create = st.tabs([
            "📋 Registered Stores", 
            "📩 Inbound Access Requests", 
            f"➕ {T['onboard_salon']}"
        ])

        with tab_list:
            stores = supabase.table("stores").select("*").order("trial_end", desc=False).execute().data
            if stores:
                for s in stores:
                    s_id = s["store_id"]
                    is_active = (s.get("status") == "active")
                    badge = "🟢 ACTIVE" if is_active else "🔴 INACTIVE"
                    border = "#D4A338" if is_active else "#EF4444"

                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left: 6px solid {border}; padding:14px 18px; border-radius:10px; margin-bottom:10px;">
                        <h4 style="margin:0; color:#0F172A;">{s['store_name']} <span style="font-size:0.85rem; color:#B45309;">[{s.get('salon_type', 'Men Salon')}]</span> - {badge}</h4>
                        <p style="margin:2px 0 0 0; color:#64748B; font-size:0.88rem;">
                            <b>Owner:</b> {s.get('owner_name')} | <b>Phone:</b> {s.get('owner_phone')} | <b>Plan:</b> {s.get('plan_name')} | <b>Expires:</b> {s.get('trial_end')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    c1, c2, c3, c4 = st.columns([2.5, 2, 2, 1.8])
                    with c1:
                        if st.button(f"✏️ {T['btn_edit_info']}", key=f"edit_info_{s_id}", use_container_width=True):
                            st.session_state.admin_editing_store_id = s_id
                            st.rerun()
                    with c2:
                        toggle_lbl = "⛔ Deactivate" if is_active else "✅ Activate"
                        new_st = "inactive" if is_active else "active"
                        if st.button(toggle_lbl, key=f"tog_{s_id}", use_container_width=True):
                            supabase.table("stores").update({"status": new_st}).eq("store_id", s_id).execute()
                            st.rerun()
                    with c3:
                        if st.button(f"➕ {T['btn_extend_30']}", key=f"ext_{s_id}", use_container_width=True):
                            curr_e = datetime.strptime(s["trial_end"], "%Y-%m-%d").date()
                            new_e = max(curr_e, date.today()) + timedelta(days=30)
                            supabase.table("stores").update({"trial_end": new_e.isoformat()}).eq("store_id", s_id).execute()
                            st.toast("Plan extended 30 days!")
                            st.rerun()
                    with c4:
                        if st.button(f"🗑️ {T['btn_delete_salon']}", key=f"del_store_{s_id}", use_container_width=True):
                            supabase.table("stores").delete().eq("store_id", s_id).execute()
                            st.toast(f"Deleted {s['store_name']}")
                            st.rerun()
                    st.write("")
            else:
                st.info("No salon stores registered yet.")

        # TAB 2: INBOUND ACCESS REQUESTS
        with tab_requests:
            st.subheader("📩 Inbound Access Requests")
            st.caption("Review incoming salon leads, call to verify, and activate or reject their registration:")

            col_sw1, col_sw2, _ = st.columns([2.2, 2.5, 4])
            with col_sw1:
                if st.button("⏳ View Pending Requests", use_container_width=True):
                    st.session_state.req_view_filter = "pending"
                    st.rerun()
            with col_sw2:
                if st.button("📋 View Accepted / Rejected History", use_container_width=True):
                    st.session_state.req_view_filter = "history"
                    st.rerun()

            try:
                if st.session_state.req_view_filter == "pending":
                    st.markdown("##### ⏳ Pending Approval Pipeline")
                    reqs = supabase.table("access_requests").select("*").eq("status", "pending").order("created_at", desc=True).execute().data
                    if reqs:
                        for rq in reqs:
                            rid = rq["request_id"]
                            st.markdown(f"""
                            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left: 6px solid #D4A338; padding:16px 20px; border-radius:10px; margin-bottom:10px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <h3 style="margin:0; font-size:1.25rem; color:#0F172A;">
                                        {rq.get('shop_name')} 
                                        <span style="font-size:0.85rem; color:#B45309; margin-left:8px;">[{rq.get('salon_type')}]</span>
                                    </h3>
                                    <span style="background:#FEF3C7; color:#B45309; padding:4px 10px; border-radius:6px; font-weight:700; font-size:0.82rem;">
                                        Plan: {rq.get('selected_plan')}
                                    </span>
                                </div>
                                <p style="margin:6px 0 0 0; color:#1E293B; font-size:0.92rem;">
                                    👤 <b>Owner:</b> {rq.get('owner_name')} &nbsp;|&nbsp; 
                                    📞 <b>Phone:</b> <a href="tel:{rq.get('owner_phone')}" style="color:#2563EB; font-weight:700;">+91 {rq.get('owner_phone')}</a> &nbsp;|&nbsp; 
                                    👥 <b>Staff:</b> {rq.get('num_staff')}
                                </p>
                                <p style="margin:4px 0 0 0; color:#64748B; font-size:0.88rem;">
                                    📍 <b>Address:</b> {rq.get('address')}
                                </p>
                                <p style="margin:2px 0 0 0; color:#64748B; font-size:0.85rem;">
                                    💬 <b>Remarks / Notes:</b> {rq.get('notes')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            c_acc, c_rej, c_trash = st.columns([2, 2, 4])
                            with c_acc:
                                if st.button(f"✅ Accept & Provision", key=f"acc_{rid}", use_container_width=True):
                                    accept_request_modal(rq)
                            with c_rej:
                                if st.button(f"❌ Reject Request", key=f"rej_{rid}", use_container_width=True):
                                    supabase.table("access_requests").update({"status": "rejected"}).eq("request_id", rid).execute()
                                    st.toast(f"Request for {rq['shop_name']} marked as rejected.")
                                    st.rerun()
                            with c_trash:
                                if st.button("🗑️ Delete Record", key=f"del_rq_{rid}"):
                                    supabase.table("access_requests").delete().eq("request_id", rid).execute()
                                    st.toast("Record deleted.")
                                    st.rerun()
                            st.write("")
                    else:
                        st.info("No pending requests right now. All requests are cleared!")

                else:
                    st.markdown("##### 📋 Accepted & Rejected History")
                    history_reqs = supabase.table("access_requests").select("*").neq("status", "pending").order("created_at", desc=True).execute().data
                    if history_reqs:
                        for hq in history_reqs:
                            h_status = hq.get("status", "unknown").upper()
                            badge_color = "#16A34A" if h_status == "ACCEPTED" else "#EF4444"
                            st.markdown(f"""
                            <div style="background:#FFFFFF; border:1px solid #E2E8F0; padding:12px 18px; border-radius:8px; margin-bottom:8px;">
                                <div style="display:flex; justify-content:space-between;">
                                    <b>{hq.get('shop_name')}</b> ({hq.get('salon_type')}) - Owner: {hq.get('owner_name')} (+91 {hq.get('owner_phone')})
                                    <span style="color:{badge_color}; font-weight:800; font-size:0.85rem;">{h_status}</span>
                                </div>
                                <div style="font-size:0.83rem; color:#64748B; margin-top:3px;">
                                    Plan: {hq.get('selected_plan')} | Address: {hq.get('address')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No history records found.")
            except Exception as e:
                st.error(f"Error accessing requests: {e}")

        # TAB 3: ONBOARD NEW SALON DIRECTLY
        with tab_create:
            with st.form("admin_create_salon_form", clear_on_submit=True):
                st.subheader(T["onboard_salon"])
                c1, c2 = st.columns(2)
                with c1:
                    s_type = st.selectbox(T["select_salon_type"], [
                        "Men's Salon & Grooming", 
                        "Women's Beauty Parlour", 
                        "Unisex Studio & Spa"
                    ])
                    s_name = st.text_input("Salon / Parlour Name *", placeholder="e.g. Blossom Ladies Parlour")
                    o_name = st.text_input("Owner Full Name *", placeholder="e.g. Sunita Sharma")
                    o_phone = st.text_input("Owner 10-digit Phone *", placeholder="e.g. 9876543210")
                with c2:
                    u_name = st.text_input(f"Owner {T['username']} *", placeholder="e.g. blossom_parlour").strip()
                    p_word = st.text_input(f"Owner {T['password']} *", type="password")
                    plan_opt = st.selectbox("Subscription Plan", ["Basic - ₹300 / Month", "Free Trial - 30 Days", "Quarterly - 90 Days", "Annual - 365 Days"])

                submit_salon_btn = st.form_submit_button(f"🚀 {T['onboard_salon']}", use_container_width=True)

            if submit_salon_btn:
                clean_p = clean_phone_number(o_phone)
                if not s_name or not o_name or len(clean_p) != 10 or not u_name or not p_word:
                    st.error("Please fill in all mandatory details with a valid 10-digit phone number.")
                else:
                    dup = supabase.table("users").select("username").eq("username", u_name).execute().data
                    if dup:
                        st.error(f"Username '{u_name}' is already taken. Please choose another.")
                    else:
                        ns_id = f"STORE-{uuid.uuid4().hex[:6].upper()}"
                        nu_id = f"U{uuid.uuid4().hex[:5].upper()}"
                        days = 30 if ("30" in plan_opt or "300" in plan_opt) else (90 if "90" in plan_opt else 365)
                        tstart = date.today()
                        tend = tstart + timedelta(days=days)

                        payload = {
                            "store_id": ns_id,
                            "user_id": nu_id,
                            "salon_name": s_name,
                            "salon_type": s_type,
                            "owner_name": o_name,
                            "owner_phone": clean_p,
                            "username": u_name,
                            "password": p_word,
                            "plan_opt": plan_opt,
                            "trial_start": tstart,
                            "trial_end": tend
                        }
                        confirm_new_salon_modal(payload)

# =========================================================
# SALON OWNER / WORKER: BILLING POS & TRANSACTIONS
# =========================================================
elif st.session_state.current_page == "home":
    today_str = date.today().isoformat()
    first_of_month = date.today().replace(day=1).isoformat()

    txns_data = supabase.table("transactions").select("*").eq("store_id", store_id).execute().data
    txns_df = pd.DataFrame(txns_data)

    if not txns_df.empty:
        txns_df["amount"] = pd.to_numeric(txns_df["amount"], errors="coerce").fillna(0.0)
        txns_df["date"] = pd.to_datetime(txns_df["timestamp"]).dt.strftime("%Y-%m-%d")

    # Metrics calculation (differentiated for Owner vs. Worker)
    if role == "worker":
        my_txns = txns_df[txns_df["worker_name"] == user["name"]] if not txns_df.empty else pd.DataFrame()
        my_today = my_txns[my_txns["date"] == today_str] if not my_txns.empty else pd.DataFrame()
        my_today_sales = my_today["amount"].sum() if not my_today.empty else 0.0
        my_today_cust = len(my_today)
        my_month_sales = my_txns[my_txns["date"] >= first_of_month]["amount"].sum() if not my_txns.empty else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric(T["metric_my_today_cust"], my_today_cust)
        m1.caption("Only your attended clients")
        m2.metric(T["metric_my_today_sales"], f"₹ {my_today_sales:,.2f}")
        m3.metric("My Current Month Sales", f"₹ {my_month_sales:,.2f}")

    else:  # Owner (Client)
        today_records = txns_df[txns_df["date"] == today_str] if not txns_df.empty else pd.DataFrame()
        today_sales = today_records["amount"].sum() if not today_records.empty else 0.0
        today_entries = len(today_records)
        month_sales = txns_df[txns_df["date"] >= first_of_month]["amount"].sum() if not txns_df.empty else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric(T["metric_today_cust"], today_entries)
        m2.metric(T["metric_today_sales"], f"₹ {today_sales:,.2f}")
        m3.metric(T["metric_month_sales"], f"₹ {month_sales:,.2f}")

        # ---------------- 7-DAY EARNINGS TREND BAR CHART (FOR OWNER ONLY) ----------------
        st.write("---")
        st.subheader(f"📈 {T['trend_7days']}")
        
        past_7_dates = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        past_7_df = pd.DataFrame({
            "Date": [d.strftime("%Y-%m-%d") for d in past_7_dates],
            "Day_Label": [d.strftime("%a (%d %b)") for d in past_7_dates],
            "Earnings": 0.0
        })

        if not txns_df.empty:
            daily_sums = txns_df.groupby("date")["amount"].sum().to_dict()
            past_7_df["Earnings"] = past_7_df["Date"].map(daily_sums).fillna(0.0)

        past_7_df["Label"] = past_7_df["Earnings"].apply(lambda v: f"₹{int(v)}" if v > 0 else "₹0")

        bars = alt.Chart(past_7_df).mark_bar(
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6,
            color="#D4A338"
        ).encode(
            x=alt.X("Day_Label:N", title="Day", sort=None, axis=alt.Axis(labelAngle=0, labelFontWeight="bold")),
            y=alt.Y("Earnings:Q", title="Earnings (₹)", scale=alt.Scale(domain=[0, max(past_7_df["Earnings"].max() * 1.25, 1000)]))
        )

        text_labels = bars.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            fontSize=12,
            fontWeight='bold',
            color='#0F172A'
        ).encode(text='Label:N')

        chart = (bars + text_labels).properties(height=260).configure_view(strokeWidth=0)
        st.altair_chart(chart, use_container_width=True)

        # ---------------- RECOGNITION (OWNER ONLY) ----------------
        st.write("---")
        c_p_title, c_p_btn = st.columns([3, 2.5])
        with c_p_title:
            st.subheader(f"👥 {T['emp_recognition']}")
        with c_p_btn:
            if st.button(T["btn_reveal_top3"], use_container_width=True):
                show_top_performers_modal(txns_df)

        if not txns_df.empty:
            today_tx = txns_df[txns_df["date"] == today_str]
            if not today_tx.empty:
                emp_summary = today_tx.groupby("worker_name").agg(
                    Customers_Served=("customer_name", "count"),
                    Total_Sales_INR=("amount", "sum")
                ).reset_index()
                emp_summary.columns = [T["staff_stylist"], T["metric_today_cust"], T["metric_today_sales"]]
                st.dataframe(emp_summary, use_container_width=True, hide_index=True)

    # ---------------- QUICK BILLING POS (STARTS EMPTY + AUTO-SUM + RECEIPT CONFIRMATION) ----------------
    st.write("---")
    col_entry, col_view = st.columns([1.1, 1.4])

    services_res = supabase.table("services").select("service_id, service_name, price").eq("store_id", store_id).order("service_name").execute().data
    services_dict = {item["service_name"]: float(item["price"]) for item in services_res} if services_res else {"Standard Service": 150.0}
    service_names = list(services_dict.keys())

    run_key = st.session_state.pos_form_run_count

    with col_entry:
        st.subheader(T["quick_pos"])

        # 1. Stylist: locked for staff, selectable for owner
        if role == "worker":
            st.text_input("Stylist / Staff (Locked to your account)", value=user["name"], disabled=True, key=f"pos_worker_locked_{run_key}")
            worker_selected = user["name"]
        else:
            staff_res = supabase.table("users").select("name").eq("store_id", store_id).execute().data
            staff_options = [s["name"] for s in staff_res] if staff_res else [user["name"]]
            default_staff_idx = staff_options.index(user["name"]) if user["name"] in staff_options else 0
            worker_selected = st.selectbox(T["staff_stylist"], staff_options, index=default_staff_idx, key=f"pos_worker_sel_{run_key}")

        # 2. Customer Name
        customer = st.text_input(T["cust_name_mobile"], placeholder="e.g. Priya Sharma", key=f"pos_cust_name_{run_key}")

        # 3. Services Rendered: ALWAYS STARTS EMPTY
        selected_services = st.multiselect(
            T["services_rendered"],
            options=service_names,
            default=[],
            placeholder="Select services provided...",
            key=f"pos_srv_select_{run_key}"
        )

        # 4. Computed Subtotal
        computed_subtotal = sum(services_dict.get(s, 0.0) for s in selected_services)

        # If services are chosen, show itemized breakdown
        if selected_services:
            st.caption("Selected Services Breakdown:")
            for s in selected_services:
                st.markdown(f"- **{s}**: ₹ {services_dict.get(s, 0.0):,.2f}")

        c_amt, c_pay = st.columns(2)
        with c_amt:
            # Dynamically auto-picked sum from selected services, but editable for discounts
            final_bill_amount = st.number_input(
                T["total_bill"],
                min_value=0.0,
                value=float(computed_subtotal),
                step=50.0,
                key=f"pos_amt_inp_{run_key}_{len(selected_services)}_{int(computed_subtotal)}"
            )
        with c_pay:
            payment = st.selectbox(T["payment_mode"], ["UPI", "Cash", "Card"], key=f"pos_pay_mode_{run_key}")

        # 5. Bill Confirmation Trigger
        if st.button(T["btn_save_sale"], use_container_width=True):
            if not customer.strip() or not selected_services or final_bill_amount <= 0:
                st.error("Please enter customer name and choose at least one service with bill > ₹0.")
            else:
                receipt_payload = {
                    "store_id": store_id,
                    "logged_by_user": user["username"],
                    "worker_name": worker_selected,
                    "customer_name": customer.strip(),
                    "services_breakdown": [{"Service": s, "Rate": services_dict.get(s, 0.0)} for s in selected_services],
                    "service_str": ", ".join(selected_services),
                    "amount": final_bill_amount,
                    "payment_mode": payment
                }
                confirm_receipt_modal(receipt_payload)

    with col_view:
        st.subheader(T["today_entries"])
        if not txns_df.empty:
            today_view = txns_df[txns_df["date"] == today_str]
            if role == "worker":
                today_view = today_view[today_view["worker_name"] == user["name"]]
            if not today_view.empty:
                st.dataframe(today_view[["timestamp", "customer_name", "service", "worker_name", "amount", "payment_mode"]], use_container_width=True, hide_index=True)
            else:
                st.info(T["no_bills_today"])
        else:
            st.info(T["no_bills_today"])

# =========================================================
# OWNER: CURRENT MONTH ONLY PROFIT & LOSS (EARNINGS VS EXPENSES)
# =========================================================
elif st.session_state.current_page == "pnl" and role == "client":
    curr_month_name = date.today().strftime("%B %Y")
    first_of_month = date.today().replace(day=1).isoformat()

    st.markdown(f"<h2>📊 {T['pnl_title']} ({curr_month_name})</h2>", unsafe_allow_html=True)
    st.caption(f"Financial summary calculated strictly for {curr_month_name} (from {first_of_month} to today).")

    txns = supabase.table("transactions").select("*").eq("store_id", store_id).execute().data
    exps = supabase.table("expenses").select("*").eq("store_id", store_id).execute().data
    
    tx_df = pd.DataFrame(txns)
    exp_df = pd.DataFrame(exps)

    # 1. Filter Transactions to Current Month Only
    if not tx_df.empty:
        tx_df["amount"] = pd.to_numeric(tx_df["amount"], errors="coerce").fillna(0.0)
        tx_df["date"] = pd.to_datetime(tx_df["timestamp"]).dt.strftime("%Y-%m-%d")
        month_tx_df = tx_df[tx_df["date"] >= first_of_month]
    else:
        month_tx_df = pd.DataFrame()

    # 2. Filter Expenses to Current Month Only
    if not exp_df.empty:
        exp_df["amount"] = pd.to_numeric(exp_df["amount"], errors="coerce").fillna(0.0)
        month_exp_df = exp_df[exp_df["expense_date"] >= first_of_month]
    else:
        month_exp_df = pd.DataFrame()

    total_income = month_tx_df["amount"].sum() if not month_tx_df.empty else 0.0
    total_expense = month_exp_df["amount"].sum() if not month_exp_df.empty else 0.0
    net_profit = total_income - total_expense

    p1, p2, p3 = st.columns(3)
    p1.metric(T["total_rev"], f"₹ {total_income:,.2f}")
    p2.metric(T["total_exp"], f"₹ {total_expense:,.2f}")
    p3.metric(T["net_profit"], f"₹ {net_profit:,.2f}")

    st.write("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader(T["rev_by_mode"])
        if not month_tx_df.empty:
            pay_dist = month_tx_df.groupby("payment_mode", as_index=False)["amount"].sum()
            pay_dist.columns = [T["payment_mode"], T["total_bill"]]
            st.dataframe(pay_dist, use_container_width=True, hide_index=True)
        else:
            st.info("No revenue recorded in this current month yet.")

    with c_right:
        st.subheader(T["exp_by_cat"])
        if not month_exp_df.empty:
            cat_dist = month_exp_df.groupby("category", as_index=False)["amount"].sum()
            cat_dist.columns = [T["exp_cat"], T["exp_amount"]]
            st.dataframe(cat_dist, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded in this current month yet.")

# =========================================================
# OWNER / ADMIN: EXPENSES WITH AUTO-CLEAN FORM & DELETION
# =========================================================
elif st.session_state.current_page == "expenses" and role in ["admin", "client"]:
    st.markdown(f"<h2>💸 {T['expenses_title']}</h2>", unsafe_allow_html=True)
    col_exp_form, col_exp_list = st.columns([1, 1.4])

    with col_exp_form:
        st.subheader(T["log_expense"])
        with st.form("add_expense_form", clear_on_submit=True):
            category = st.selectbox(T["exp_cat"], ["Salon/Beauty Products", "Rent", "Staff Salary", "Utilities", "Maintenance", "Tea/Coffee", "Other"])
            desc = st.text_input(T["exp_desc"], placeholder="e.g. L'Oreal shampoo stock, Tea expenses")
            exp_amount = st.number_input(T["exp_amount"], min_value=0.0, step=100.0)
            exp_date = st.date_input(T["exp_date"], value=date.today())
            submit_exp = st.form_submit_button(T["btn_save_exp"], use_container_width=True)

        if submit_exp:
            if exp_amount > 0:
                supabase.table("expenses").insert({
                    "expense_id": f"EXP-{uuid.uuid4().hex[:6].upper()}",
                    "store_id": store_id,
                    "category": category,
                    "description": desc,
                    "amount": exp_amount,
                    "expense_date": exp_date.isoformat(),
                    "logged_by": user["username"]
                }).execute()
                st.toast("Saved expense!")
                st.rerun()
            else:
                st.error("Please enter a valid expense amount.")

    with col_exp_list:
        st.subheader(T["exp_history"])
        exp_res = supabase.table("expenses").select("*").eq("store_id", store_id).order("expense_date", desc=True).execute().data
        if exp_res:
            for ex in exp_res:
                c_e1, c_e2, c_e3 = st.columns([4, 2, 1.5])
                with c_e1:
                    st.write(f"**{ex.get('category')}** - {ex.get('description', '')}")
                    st.caption(f"Date: {ex.get('expense_date')} | Logged by: {ex.get('logged_by')}")
                with c_e2:
                    st.markdown(f"**₹ {float(ex.get('amount', 0)):,.2f}**")
                with c_e3:
                    if st.button("🗑️ Delete", key=f"del_exp_{ex['expense_id']}"):
                        supabase.table("expenses").delete().eq("expense_id", ex["expense_id"]).execute()
                        st.toast("Expense deleted!")
                        st.rerun()
                st.write("")
        else:
            st.info("No expenses recorded yet.")

# =========================================================
# STORE CONFIG: SERVICES (EDIT + DELETE) & EMPLOYEES
# =========================================================
elif st.session_state.current_page == "settings" and role in ["admin", "client"]:
    st.markdown(f"<h2>⚙️ {T['store_config_title']}</h2>", unsafe_allow_html=True)
    tab_serv, tab_emp = st.tabs([f"💅 {T['tab_services']}", f"👥 {T['tab_employees']}"])

    # 1. SERVICES WITH EDIT AND DELETE
    with tab_serv:
        st.subheader(T["tab_services"])
        services_db = supabase.table("services").select("*").eq("store_id", store_id).order("service_name").execute().data
        
        if services_db:
            for srv in services_db:
                c_s1, c_s2, c_s3, c_s4 = st.columns([3.5, 2, 1.2, 1.2])
                with c_s1:
                    st.write(f"✂️ **{srv.get('service_name')}**")
                with c_s2:
                    st.write(f"₹ {float(srv.get('price', 0)):,.2f}")
                with c_s3:
                    if st.button("✏️ Edit", key=f"edit_srv_{srv.get('service_id')}", use_container_width=True):
                        edit_service_modal(srv)
                with c_s4:
                    if st.button("🗑️ Delete", key=f"del_srv_{srv.get('service_id')}", use_container_width=True):
                        supabase.table("services").delete().eq("service_id", srv["service_id"]).execute()
                        st.toast(f"Deleted {srv['service_name']}!")
                        st.rerun()
                st.write("")
        else:
            st.info("No services added yet.")

        st.write("---")
        st.subheader(f"➕ {T['add_new_service']}")
        with st.form("add_new_service_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                placeholder_text = "e.g. Fruit Facial, Waxing" if "Women" in salon_cat else "e.g. Beard Shape, Fade Cut"
                ns = st.text_input(T["service_name"], placeholder=placeholder_text)
            with c2:
                np = st.number_input(T["standard_rate"], min_value=0.0, step=50.0)
            submit_srv = st.form_submit_button(T["btn_save_service"])

        if submit_srv:
            if ns and np > 0:
                supabase.table("services").insert({
                    "service_id": f"SRV-{uuid.uuid4().hex[:5].upper()}",
                    "store_id": store_id,
                    "service_name": ns.strip(),
                    "price": np
                }).execute()
                st.toast("Service added successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid service name and rate.")

    # 2. EMPLOYEES CONFIGURATION
    with tab_emp:
        st.subheader(T["tab_employees"])
        staff_records = supabase.table("users").select("user_id, username, name, role, status").eq("store_id", store_id).execute().data
        
        if staff_records:
            for stf in staff_records:
                c_u1, c_u2, c_u3, c_u4 = st.columns([3, 2, 2, 1.5])
                with c_u1:
                    st.write(f"👤 **{stf.get('name')}**")
                    st.caption(f"Role: {stf.get('role').upper()}")
                with c_u2:
                    st.write(f"{T['username']}: `{stf.get('username')}`")
                with c_u3:
                    st.write(f"Status: **{stf.get('status', 'active').upper()}**")
                with c_u4:
                    if stf.get("role") == "worker":
                        if st.button("🗑️ Delete", key=f"del_user_{stf.get('user_id')}"):
                            supabase.table("users").delete().eq("user_id", stf["user_id"]).execute()
                            st.toast(f"Removed employee {stf.get('name')}!")
                            st.rerun()
                st.write("")
        else:
            st.info("No staff accounts added yet.")
        
        st.write("---")
        with st.expander(f"➕ {T['add_new_staff']}"):
            with st.form("create_staff_form", clear_on_submit=True):
                en = st.text_input(T["staff_full_name"], placeholder="e.g. Rahul Verma")
                eu = st.text_input(T["staff_username"], placeholder="e.g. rahul_stylist").strip()
                ep = st.text_input(T["staff_password"], type="password")
                submit_staff = st.form_submit_button(T["btn_save_staff"])

            if submit_staff:
                if not en or not eu or not ep:
                    st.error("Please fill in all staff details.")
                elif len(ep) < 6:
                    st.error("Staff password must be at least 6 characters.")
                else:
                    chk_u = supabase.table("users").select("username").eq("username", eu).execute().data
                    if chk_u:
                        st.error(f"Username '{eu}' is already in use. Please select a different username.")
                    else:
                        staff_payload = {
                            "user_id": f"U{uuid.uuid4().hex[:5].upper()}",
                            "store_id": store_id,
                            "name": en.strip(),
                            "username": eu,
                            "password": ep
                        }
                        confirm_new_staff_modal(staff_payload)

# ----------------- GLOBAL FOOTER -----------------
st.markdown("""
<div class="brand-footer">
    Developed & Engineered by <span class="brand-highlight">Global Wealth International</span> • All Rights Reserved
</div>
""", unsafe_allow_html=True)