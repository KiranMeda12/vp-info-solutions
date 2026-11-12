"""
VP Info Solutions Pvt Ltd - Lead Management System
Streamlit Frontend Application — Premium Enterprise Edition
Tally Certified Partner
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from frontend.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="VP Info Solutions Pvt Ltd | Enterprise Sales Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra-Premium Enterprise Corporate Theme
st.markdown("""
<style>
    /* Global Typography & Palette */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0F172A;
    }
    
    /* Top Accent Line */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Brand Header Bar */
    .brand-header {
        background: linear-gradient(135deg, #0A192F 0%, #0F2A4A 60%, #1A365D 100%);
        border-bottom: 3px solid #F59E0B;
        color: #FFFFFF;
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(10, 25, 47, 0.2), 0 8px 10px -6px rgba(10, 25, 47, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    .brand-header::after {
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 140px;
        height: 140px;
        background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .brand-title {
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin: 4px 0 0 0;
        font-weight: 500;
        letter-spacing: 0.2px;
    }
    .tally-badge {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #0F172A;
        font-weight: 800;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.3);
        display: inline-block;
    }
    
    /* Executive Metric KPI Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 12px;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.08), 0 6px 8px -3px rgba(0, 0, 0, 0.04);
        border-color: #CBD5E1;
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #CBD5E1;
    }
    .metric-card.card-blue::before { background: linear-gradient(90deg, #2563EB, #3B82F6); }
    .metric-card.card-amber::before { background: linear-gradient(90deg, #D97706, #F59E0B); }
    .metric-card.card-green::before { background: linear-gradient(90deg, #059669, #10B981); }
    .metric-card.card-purple::before { background: linear-gradient(90deg, #7C3AED, #8B5CF6); }
    .metric-card.card-gold::before { background: linear-gradient(90deg, #B45309, #F59E0B); }
    
    .metric-label {
        font-size: 11px;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #0A192F;
        margin-top: 6px;
        letter-spacing: -0.5px;
    }
    .metric-sub {
        font-size: 11.5px;
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Modern Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 13.5px;
        color: #475569;
        background-color: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    
    /* Section Containers */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    
    /* Login Box Container */
    .login-container {
        max-width: 480px;
        margin: 30px auto;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(10, 25, 47, 0.1), 0 10px 10px -5px rgba(10, 25, 47, 0.04);
        overflow: hidden;
    }
    .login-header {
        background: linear-gradient(135deg, #0A192F 0%, #1A365D 100%);
        border-bottom: 3px solid #F59E0B;
        padding: 32px 28px;
        color: white;
        text-align: center;
    }
    .login-body {
        padding: 28px;
    }
    
    /* Status Badges */
    .badge {
        font-weight: 700;
        font-size: 11.5px;
        padding: 3px 10px;
        border-radius: 9999px;
        display: inline-block;
        letter-spacing: 0.3px;
    }
    .badge-won { background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .badge-new { background-color: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
    .badge-negotiation { background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .badge-demo { background-color: #FAF5FF; color: #6B21A8; border: 1px solid #E9D5FF; }
    .badge-lost { background-color: #FFF1F2; color: #9F1239; border: 1px solid #FECDD3; }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0A192F !important;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not([style*="color"]),
    section[data-testid="stSidebar"] div:not([style*="color"]),
    section[data-testid="stSidebar"] label {
        color: #E2E8F0;
    }
    section[data-testid="stSidebar"] code {
        background-color: #1E293B !important;
        color: #F59E0B !important;
        border: 1px solid #334155 !important;
        padding: 3px 8px !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #1E293B;
        border: 1px solid #334155;
        color: #F8FAFC !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #F59E0B;
        color: #0F172A !important;
        border-color: #F59E0B;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

api = APIClient(st.session_state.token)

STATUS_OPTIONS = ["New", "Contacted", "Demo Scheduled", "Negotiation", "Won", "Lost"]
PRODUCT_OPTIONS = [
    "TallyPrime Silver/Gold",
    "Tally.ERP 9 Upgrade to Prime",
    "Tally Customization (TDL)",
    "Annual Maintenance Contract (AMC)",
    "Tally on Cloud",
    "Tally Server 9",
    "Tally API & ERP Integration",
]
INDUSTRY_OPTIONS = [
    "Manufacturing",
    "Retail & Apparel",
    "Textiles & Garments",
    "Healthcare & Pharma",
    "Logistics & Warehousing",
    "Construction & Real Estate",
    "FMCG / Agro",
    "IT & Software Services",
    "Industrial Hardware",
    "Import & Export",
    "Professional Services",
]


# =============================================================================
# AUTHENTICATION / LOGIN VIEW (PREMIUM EXECUTIVE BRANDING)
# =============================================================================
def render_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <div style="font-size: 28px; font-weight: 900; letter-spacing: -0.5px; color: #FFFFFF;">
                VP INFO SOLUTIONS
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #F59E0B; margin-top: 6px; letter-spacing: 0.8px; text-transform: uppercase;">
                ★ Tally Certified Partner ★
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 6px;">
                Enterprise Lead Tracking & Sales Governance System
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        with st.form("login_form"):
            default_user = st.session_state.get("login_user", "")
            default_pass = st.session_state.get("login_pass", "")
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 4px;'>Corporate Identity</div>", unsafe_allow_html=True)
            username = st.text_input("Username", value=default_user, placeholder="Enter username", label_visibility="collapsed")
            
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; margin-top: 10px; margin-bottom: 4px;'>Access Key</div>", unsafe_allow_html=True)
            password = st.text_input("Password", value=default_pass, type="password", placeholder="Enter password", label_visibility="collapsed")
            
            st.write("")
            submit_btn = st.form_submit_button("Secure Sign In →", use_container_width=True, type="primary")

            if submit_btn:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Verifying credentials..."):
                        res = api.login(username, password)
                        if res["success"]:
                            data = res["data"]
                            st.session_state.authenticated = True
                            st.session_state.token = data["access_token"]
                            st.session_state.user_info = data
                            st.rerun()
                        else:
                            st.error(f"Authentication failed: {res.get('error', 'Invalid credentials')}")


def logout():
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user_info = None
    st.rerun()


# =============================================================================
# TOP HEADER BAR
# =============================================================================
def render_header():
    user = st.session_state.user_info
    role = user["role"]
    role_color = {
        "Admin": "background: linear-gradient(135deg, #7C3AED, #8B5CF6);",
        "RM": "background: linear-gradient(135deg, #0284C7, #0EA5E9);",
        "Sales Consultant": "background: linear-gradient(135deg, #059669, #10B981);",
        "Sales Person": "background: linear-gradient(135deg, #059669, #10B981);"
    }.get(role, "background: #64748B;")

    rm_info = f" &bull; RM: <strong>{user.get('rm_name')}</strong>" if user.get("rm_name") else ""

    st.markdown(f"""
    <div class="brand-header">
        <div>
            <h1 class="brand-title">
                VP INFO SOLUTIONS PVT LTD
                <span class="tally-badge">Tally Certified Partner</span>
            </h1>
            <p class="brand-subtitle">Premier Enterprise Lead Tracking & Performance Intelligence</p>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 700; font-size: 15px; color: #FFFFFF; display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
                <span>{user['full_name']}</span>
                <span style="{role_color} color: white; padding: 3px 10px; border-radius: 9999px; font-size: 11px; font-weight: 800; letter-spacing: 0.5px;">
                    {role.upper()}
                </span>
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                {user['email']} {rm_info}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# 1. ADMIN DASHBOARD
# =============================================================================
def render_admin_dashboard():
    # Top Timeframe Filter Toolbar
    st.markdown("##### 📅 Performance Timeframe")
    tf_c1, tf_c2, tf_c3, tf_c4 = st.columns([1.3, 1.5, 1.5, 3])
    current_year = datetime.now().year
    # Include current year, next 10 years, and previous years
    year_options = ["All Years"] + list(range(current_year, current_year + 11)) + [current_year - 1, current_year - 2]
    with tf_c1:
        year_sel = st.selectbox("Year", year_options, label_visibility="collapsed")
    with tf_c2:
        quarter_options = ["All Quarters", "Q1 (Jan - Mar)", "Q2 (Apr - Jun)", "Q3 (Jul - Sep)", "Q4 (Oct - Dec)"]
        quarter_sel = st.selectbox("Quarter", quarter_options, label_visibility="collapsed")
    with tf_c3:
        month_names = ["All Months", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_sel = st.selectbox("Month", month_names, label_visibility="collapsed")
    with tf_c4:
        st.caption(f"Filtering metrics for: **{year_sel}** &bull; **{quarter_sel}** &bull; **{month_sel}**")

    year_val = None if year_sel == "All Years" else int(year_sel)
    month_val = None if month_sel == "All Months" else month_names.index(month_sel)

    # Ingest leads & users
    all_leads = api.get_leads(year=year_val, month=month_val)
    all_users = api.get_users()
    rms = [u for u in all_users if u["role"] == "RM"]
    scs = [u for u in all_users if u["role"] in ["Sales Consultant", "Sales Person"]]

    tab_overall, tab_rm_dash, tab_sc_dash, tab_quarterly, tab_assign, tab_user_mgmt, tab_powerbi = st.tabs([
        "🌐 Overall Executive Dashboard",
        "👔 Relationship Managers (RM) Dashboard",
        "🎯 Sales Consultants (SC) Dashboard",
        "📊 Quarterly Reports & Trends",
        "📥 RM Leads Pending Assignment",
        "⚙️ Team Governance & User Accounts",
        "📊 Power BI Reporting Hub"
    ])

    # --- TAB 1: OVERALL EXECUTIVE DASHBOARD ---
    with tab_overall:
        total_leads = len(all_leads)
        won_leads = sum(1 for l in all_leads if l["status"] == "Won")
        lost_leads = sum(1 for l in all_leads if l["status"] == "Lost")
        open_deals = total_leads - won_leads - lost_leads
        total_val = sum(l["estimated_value"] for l in all_leads)
        won_val = sum(l["estimated_value"] for l in all_leads if l["status"] == "Won")
        conv_rate = round((won_leads / total_leads * 100), 1) if total_leads > 0 else 0.0

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"""
            <div class="metric-card card-blue">
                <div class="metric-label">Company Total Leads</div>
                <div class="metric-value">{total_leads}</div>
                <div class="metric-sub" style="color: #2563EB;">All Active Branches</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card card-amber">
                <div class="metric-label">Active Open Deals</div>
                <div class="metric-value">{open_deals}</div>
                <div class="metric-sub" style="color: #D97706;">In Active Stages</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card card-green">
                <div class="metric-label">Closed Won Deals</div>
                <div class="metric-value">{won_leads}</div>
                <div class="metric-sub" style="color: #059669;">Finalized Contracts</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card card-purple">
                <div class="metric-label">Conversion Rate</div>
                <div class="metric-value">{conv_rate}%</div>
                <div class="metric-sub" style="color: #7C3AED;">Company-wide Win Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div class="metric-card card-gold">
                <div class="metric-label">Closed Revenue (INR)</div>
                <div class="metric-value" style="font-size: 21px;">₹{won_val:,.0f}</div>
                <div class="metric-sub" style="color: #B45309;">Gross: ₹{total_val:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Visual breakdown
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            if all_leads:
                df_all = pd.DataFrame(all_leads)
                prod_counts = df_all["interested_product"].value_counts().reset_index()
                prod_counts.columns = ["Product", "Count"]
                fig_prod = px.pie(
                    prod_counts,
                    names="Product",
                    values="Count",
                    title="<b>Leads by Tally Product Portfolio</b>",
                    hole=0.45,
                    color_discrete_sequence=["#1E3A8A", "#2563EB", "#0284C7", "#059669", "#F59E0B", "#7C3AED", "#64748B"]
                )
                fig_prod.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_prod, use_container_width=True)
        with c_ch2:
            if all_leads:
                st_counts = df_all["status"].value_counts().reset_index()
                st_counts.columns = ["Stage", "Count"]
                fig_st = px.bar(
                    st_counts,
                    x="Count",
                    y="Stage",
                    orientation="h",
                    title="<b>Pipeline Deal Stages Funnel</b>",
                    color="Count",
                    color_continuous_scale="Blues"
                )
                fig_st.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_st, use_container_width=True)

        st.markdown("#### 📋 Master Company Pipeline")
        if not all_leads:
            st.info("No leads recorded for current selection.")
        else:
            df_m = pd.DataFrame(all_leads)
            cols = ["lead_number", "business_name", "lead_name", "phone", "interested_product", "status", "estimated_value", "sales_person_name", "rm_name", "created_by_name"]
            st.dataframe(
                df_m[cols].rename(columns={
                    "lead_number": "Lead No.",
                    "business_name": "Company Name",
                    "lead_name": "Person to Meet",
                    "phone": "Phone",
                    "interested_product": "Tally Product",
                    "status": "Stage",
                    "estimated_value": "Value (₹)",
                    "sales_person_name": "Sales Consultant",
                    "rm_name": "Relationship Manager",
                    "created_by_name": "Logged By"
                }),
                use_container_width=True,
                height=320
            )

    # --- TAB 2: RM DASHBOARD ---
    with tab_rm_dash:
        st.markdown("### 👔 Relationship Managers (RM) Command Center")
        rm_leaderboard = api.get_rm_leaderboard()

        if rm_leaderboard:
            df_rm_lb = pd.DataFrame(rm_leaderboard)
            r_c1, r_c2 = st.columns([1.6, 1.4])
            with r_c1:
                st.markdown("**Relationship Manager Performance Matrix:**")
                st.dataframe(
                    df_rm_lb[["rm_name", "leads_raised", "team_reps_count", "team_total_leads", "team_closed_won", "team_conversion_rate", "team_pipeline_value"]].rename(columns={
                        "rm_name": "Relationship Manager",
                        "leads_raised": "Leads Raised",
                        "team_reps_count": "Team Size",
                        "team_total_leads": "Total Leads",
                        "team_closed_won": "Closed Won",
                        "team_conversion_rate": "Win Rate %",
                        "team_pipeline_value": "Pipeline (₹)"
                    }),
                    use_container_width=True,
                    height=240
                )
            with r_c2:
                fig_rm_ch = px.bar(
                    df_rm_lb,
                    x="rm_name",
                    y="team_pipeline_value",
                    title="<b>Team Pipeline Value by Relationship Manager</b>",
                    text_auto=".2s",
                    color="team_closed_won",
                    color_continuous_scale="Viridis"
                )
                fig_rm_ch.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Pipeline (INR)")
                st.plotly_chart(fig_rm_ch, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Filter by Relationship Manager")
        rm_options = {r["full_name"]: r["id"] for r in rms}
        chosen_rm_filter = st.selectbox("Select Relationship Manager:", ["All Relationship Managers"] + list(rm_options.keys()))
        selected_rm_id = rm_options.get(chosen_rm_filter) if chosen_rm_filter != "All Relationship Managers" else None

        rm_filtered_leads = api.get_leads(rm_id=selected_rm_id, year=year_val, month=month_val)
        if rm_filtered_leads:
            df_rml = pd.DataFrame(rm_filtered_leads)
            st.dataframe(
                df_rml[["lead_number", "business_name", "lead_name", "phone", "interested_product", "status", "estimated_value", "sales_person_name", "rm_name"]].rename(columns={
                    "lead_number": "Lead #",
                    "business_name": "Company",
                    "lead_name": "Contact Person",
                    "phone": "Phone",
                    "interested_product": "Tally Product",
                    "status": "Stage",
                    "estimated_value": "Value (₹)",
                    "sales_person_name": "Consultant",
                    "rm_name": "RM"
                }),
                use_container_width=True,
                height=260
            )

    # --- TAB 3: SALES CONSULTANT DASHBOARD ---
    with tab_sc_dash:
        st.markdown("### 🎯 Sales Consultants (SC) Command Center")
        sc_leaderboard = api.get_sc_leaderboard()

        if sc_leaderboard:
            df_sc_lb = pd.DataFrame(sc_leaderboard)
            sc_c1, sc_c2 = st.columns([1.6, 1.4])
            with sc_c1:
                st.markdown("**Sales Consultant Standings:**")
                st.dataframe(
                    df_sc_lb[["sc_name", "total_assigned", "won", "not_interested", "win_rate", "price_on_win"]].rename(columns={
                        "sc_name": "Sales Consultant",
                        "total_assigned": "Total Assigned",
                        "won": "Won",
                        "not_interested": "Not Interested",
                        "win_rate": "Win Rate (%)",
                        "price_on_win": "Price on Win (₹)"
                    }),
                    use_container_width=True,
                    height=260
                )
            with sc_c2:
                fig_sc_ch = px.bar(
                    df_sc_lb,
                    x="sc_name",
                    y=["won", "open_deals", "not_interested"],
                    title="<b>Consultant Deal Trajectory (Won vs Open vs Not Interested)</b>",
                    barmode="stack",
                    color_discrete_map={"won": "#10B981", "open_deals": "#F59E0B", "not_interested": "#EF4444"}
                )
                fig_sc_ch.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Number of Deals")
                st.plotly_chart(fig_sc_ch, use_container_width=True)

        st.markdown("---")
        sc_options = {s["full_name"]: s["id"] for s in scs}
        chosen_sc_filter = st.selectbox("Select Consultant:", ["All Sales Consultants"] + list(sc_options.keys()))
        selected_sc_id = sc_options.get(chosen_sc_filter) if chosen_sc_filter != "All Sales Consultants" else None

        sc_filtered_leads = api.get_leads(sales_rep_id=selected_sc_id, year=year_val, month=month_val)
        if sc_filtered_leads:
            df_scl = pd.DataFrame(sc_filtered_leads)
            st.dataframe(
                df_scl[["lead_number", "business_name", "lead_name", "phone", "interested_product", "status", "estimated_value", "sales_person_name", "rm_name"]].rename(columns={
                    "lead_number": "Lead #",
                    "business_name": "Company",
                    "lead_name": "Person to Meet",
                    "phone": "Phone",
                    "interested_product": "Product",
                    "status": "Stage",
                    "estimated_value": "Value (₹)",
                    "sales_person_name": "Consultant",
                    "rm_name": "RM"
                }),
                use_container_width=True,
                height=260
            )

            st.markdown("#### 📋 Assigned Leads Dossier & Complete Details:")
            for l in sc_filtered_leads:
                with st.expander(f"🏢 {l.get('business_name', 'Lead')} (#{l.get('lead_number', '')}) — Stage: {l.get('status', '')}", expanded=(len(sc_filtered_leads) == 1)):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**👤 Person to Meet:** {l.get('lead_name', 'N/A')}")
                        st.markdown(f"**💼 Designation:** {l.get('designation', 'N/A')}")
                        st.markdown(f"**📞 Phone:** {l.get('phone', 'N/A')}")
                        st.markdown(f"**✉️ Email:** {l.get('email', 'N/A')}")
                    with c2:
                        st.markdown(f"**📅 Meeting Date:** {l.get('meeting_date', 'N/A')}")
                        st.markdown(f"**⏰ Meeting Time:** {l.get('meeting_time', 'N/A')}")
                        st.markdown(f"**📦 Product:** {l.get('interested_product', 'N/A')}")
                        st.markdown(f"**💰 Value:** ₹{float(l.get('estimated_value') or 0):,.2f}")
                    with c3:
                        st.markdown(f"**👔 Generated by RM:** {l.get('rm_name', 'Direct')}")
                        st.markdown(f"**🧑‍💼 Assigned Consultant:** {l.get('sales_person_name', 'Unassigned')}")
                    st.markdown(f"**📍 Company & Meeting Address:** {l.get('address', 'N/A')}")
                    st.markdown(f"**📝 Requirement Notes & RM Remarks:** {l.get('notes', 'N/A')}")

    # --- TAB: QUARTERLY REPORTS ---
    with tab_quarterly:
        st.markdown("### 📊 Enterprise Quarterly Performance & Revenue Reports")
        st.caption(f"Comparative Quarter-by-Quarter Breakdown for **{year_sel}**")

        q_defs = [
            {"id": "Q1", "name": "Q1 (Jan - Mar)", "m": [1, 2, 3]},
            {"id": "Q2", "name": "Q2 (Apr - Jun)", "m": [4, 5, 6]},
            {"id": "Q3", "name": "Q3 (Jul - Sep)", "m": [7, 8, 9]},
            {"id": "Q4", "name": "Q4 (Oct - Dec)", "m": [10, 11, 12]},
        ]

        qc1, qc2, qc3, qc4 = st.columns(4)
        cols = [qc1, qc2, qc3, qc4]
        matrix_rows = []

        for idx, q in enumerate(q_defs):
            q_leads = [l for l in (all_leads or []) if l.get("meeting_date") and int(l["meeting_date"].split("-")[1]) in q["m"]]
            q_won = [l for l in q_leads if l.get("status") == "Won"]
            q_lost = [l for l in q_leads if l.get("status") == "Lost"]
            q_open = len(q_leads) - len(q_won) - len(q_lost)
            q_rev = sum(float(l.get("estimated_value") or 0) for l in q_won)
            q_rate = round(len(q_won) / len(q_leads) * 100, 1) if q_leads else 0.0

            with cols[idx]:
                st.metric(label=q["name"], value=f"₹{q_rev:,.0f}", delta=f"{len(q_won)} Won / {len(q_leads)} Leads")
                st.caption(f"Win Rate: **{q_rate}%** | Open: **{q_open}**")

            matrix_rows.append({
                "Quarter": q["name"],
                "Total Leads": len(q_leads),
                "Won Deals": len(q_won),
                "Not Interested": len(q_lost),
                "Open Deals": q_open,
                "Win Rate (%)": f"{q_rate}%",
                "Total Revenue (₹)": f"₹{q_rev:,.2f}"
            })

        st.markdown("#### 📈 Quarterly Comparative Matrix")
        st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📥 Download Enterprise Reports (Excel / CSV)")
        st.caption("📌 **Rule Applied:** Leads in reports are sorted with **Won** first, followed by **Not Interested**, then remaining pipeline stages.")

        def sort_leads_for_export(leads):
            prio = {"Won": 1, "Lost": 2, "Negotiation": 3, "Demo Scheduled": 4, "Contacted": 5, "New": 6}
            return sorted(leads, key=lambda l: (prio.get(l.get("status"), 99), l.get("meeting_date") or ""))

        if all_leads:
            sorted_leads = sort_leads_for_export(all_leads)
            df_exp = pd.DataFrame(sorted_leads)
            if "status" in df_exp.columns:
                df_exp["status_label"] = df_exp["status"].apply(lambda s: "Not Interested" if s == "Lost" else s)
            csv_data = df_exp.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📗 Download Report in Excel (.csv) — Won First, Then Not Interested",
                data=csv_data,
                file_name=f"VP_Info_Report_{year_sel}_{quarter_sel}_{month_sel}.csv",
                mime="text/csv"
            )

    # --- TAB 4: RM LEADS PENDING ASSIGNMENT ---
    with tab_assign:
        st.markdown("### 📥 RM Raised Leads — Pending Admin Assignment")
        st.info("💡 **Policy:** Leads raised by Relationship Managers are assigned to Sales Consultants by **Admin Only**.")

        unassigned_leads = api.get_leads(unassigned_only=True)
        if not unassigned_leads:
            st.success("🎉 All RM-raised leads are currently assigned! Queue is clean.")
        else:
            st.warning(f"⚠️ You have **{len(unassigned_leads)}** leads awaiting consultant allocation.")
            
            df_un = pd.DataFrame(unassigned_leads)
            st.dataframe(
                df_un[["lead_number", "business_name", "lead_name", "designation", "phone", "meeting_date", "meeting_time", "interested_product", "created_by_name"]].rename(columns={
                    "lead_number": "Lead Number",
                    "business_name": "Company",
                    "lead_name": "Person to Meet",
                    "designation": "Designation",
                    "phone": "Phone",
                    "meeting_date": "Meeting Date",
                    "meeting_time": "Meeting Timings",
                    "interested_product": "Product",
                    "created_by_name": "Raised by RM"
                }),
                use_container_width=True,
                height=220
            )

            st.markdown("#### 🚀 Lead Allocation Desk")
            un_choices = {f"{l['lead_number']} - {l['business_name']} ({l['lead_name']} | Raised by {l['created_by_name']})": l['id'] for l in unassigned_leads}
            sc_target_opts = {f"{s['full_name']} (RM: {s.get('rm_name') or 'Direct'})": s['id'] for s in scs}

            if not sc_target_opts:
                st.warning("No active Sales Consultants found to allocate leads to. Please register consultants in Team Governance.")
            else:
                with st.form("admin_assign_form"):
                    col_as1, col_as2 = st.columns(2)
                    with col_as1:
                        sel_un_label = st.selectbox("Select Pending Lead *", list(un_choices.keys()))
                    with col_as2:
                        sel_sc_label = st.selectbox("Assign to Sales Consultant *", list(sc_target_opts.keys()))

                    assign_notes = st.text_input("Special Instructions / Meeting Notes for Consultant", placeholder="e.g., Client requested on-site visit for multi-user TallyPrime demo...")
                    submit_assign = st.form_submit_button("Allocate Lead to Consultant →", type="primary", use_container_width=True)

                    if submit_assign:
                        sel_un_id = un_choices.get(sel_un_label)
                        sel_sc_id = sc_target_opts.get(sel_sc_label)
                        if not sel_un_id or not sel_sc_id:
                            st.error("Please select a valid lead and sales consultant.")
                        else:
                            res = api.assign_lead(sel_un_id, sel_sc_id, assign_notes)
                            if res["success"]:
                                st.success(f"Lead assigned successfully to {sel_sc_label}!")
                                st.rerun()
                            else:
                                st.error(f"Assignment failed: {res.get('error')}")

    # --- TAB 5: USER MANAGEMENT ---
    with tab_user_mgmt:
        st.markdown("### ⚙️ Team Governance & User Management (Admin Only)")
        st.caption("Admin can add new Relationship Managers and Sales Consultants, manage reporting hierarchies, or remove accounts.")

        col_u1, col_u2 = st.columns([1.7, 1.3])

        with col_u1:
            st.markdown("#### Active Team Directory")
            df_users = pd.DataFrame(all_users)
            st.dataframe(
                df_users[["id", "full_name", "username", "role", "email", "phone", "rm_name"]].rename(columns={
                    "id": "ID",
                    "full_name": "Full Name",
                    "username": "Username",
                    "role": "Role",
                    "email": "Email",
                    "phone": "Phone",
                    "rm_name": "Assigned RM"
                }),
                use_container_width=True,
                height=260
            )

            st.markdown("#### 🗑️ Remove User Account (RM or SC)")
            removable_users = {f"#{u['id']} - {u['full_name']} ({u['role']} - {u['username']})": u['id'] for u in all_users if u['role'] != 'Admin'}
            if removable_users:
                sel_del_label = st.selectbox("Select Account to Remove:", list(removable_users.keys()))
                if st.button("Permanently Remove Selected User", type="secondary"):
                    del_user_id = removable_users.get(sel_del_label)
                    if del_user_id:
                        res = api.delete_user(del_user_id)
                        if res["success"]:
                            st.success("User account removed successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to remove user: {res.get('error')}")

        with col_u2:
            st.markdown("#### ➕ Register New Team Member")
            add_tab_rm, add_tab_sc = st.tabs(["👔 Add Relationship Manager (RM)", "🎯 Add Sales Consultant (SC)"])

            with add_tab_rm:
                with st.form("create_rm_form", clear_on_submit=True):
                    rm_name = st.text_input("RM Full Name *", placeholder="e.g. Vikram Malhotra")
                    rm_uname = st.text_input("RM Username *", placeholder="e.g. rm_vikram")
                    rm_pass = st.text_input("RM Password *", type="password", placeholder="Enter password")
                    rm_email = st.text_input("RM Email Address *", placeholder="e.g. vikram.m@vpinfosolutions.com")
                    rm_phone = st.text_input("RM Phone Number", placeholder="e.g. +91 98111 22334")
                    
                    submit_rm = st.form_submit_button("Create Relationship Manager Account →", type="primary", use_container_width=True)
                    if submit_rm:
                        if not rm_name or not rm_uname or not rm_pass or not rm_email:
                            st.error("Please fill in all mandatory fields: Name, Username, Password, and Email.")
                        else:
                            payload = {
                                "full_name": rm_name,
                                "username": rm_uname,
                                "password": rm_pass,
                                "email": rm_email,
                                "phone": rm_phone,
                                "role": "RM",
                                "rm_id": None,
                                "is_active": True
                            }
                            res = api.create_user(payload)
                            if res["success"]:
                                st.success(f"Relationship Manager '{rm_name}' created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to create RM: {res.get('error')}")

            with add_tab_sc:
                with st.form("create_sc_form", clear_on_submit=True):
                    sc_name = st.text_input("SC Full Name *", placeholder="e.g. Amit Verma")
                    sc_uname = st.text_input("SC Username *", placeholder="e.g. sales_amit")
                    sc_pass = st.text_input("SC Password *", type="password", placeholder="Enter password")
                    sc_email = st.text_input("SC Email Address *", placeholder="e.g. amit.v@vpinfosolutions.com")
                    sc_phone = st.text_input("SC Phone Number", placeholder="e.g. +91 98765 43210")

                    rm_options_map = {"Direct / No RM Assigned": None}
                    for r in rms:
                        rm_options_map[f"{r['full_name']} ({r['username']})"] = r["id"]

                    sel_sc_rm = st.selectbox("Assign to Relationship Manager (RM):", list(rm_options_map.keys()))
                    
                    submit_sc = st.form_submit_button("Create Sales Consultant Account →", type="primary", use_container_width=True)
                    if submit_sc:
                        if not sc_name or not sc_uname or not sc_pass or not sc_email:
                            st.error("Please fill in all mandatory fields: Name, Username, Password, and Email.")
                        else:
                            assigned_rm_val = rm_options_map.get(sel_sc_rm)
                            payload = {
                                "full_name": sc_name,
                                "username": sc_uname,
                                "password": sc_pass,
                                "email": sc_email,
                                "phone": sc_phone,
                                "role": "Sales Consultant",
                                "rm_id": assigned_rm_val,
                                "is_active": True
                            }
                            res = api.create_user(payload)
                            if res["success"]:
                                st.success(f"Sales Consultant '{sc_name}' created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to create Sales Consultant: {res.get('error')}")

    # --- TAB 6: POWER BI ---
    with tab_powerbi:
        st.markdown("### 📊 Power BI Integration Hub")
        st.markdown("Direct tabular exports and live Web API feed for Microsoft Power BI Desktop dashboards.")
        
        p1, p2 = st.columns(2)
        with p1:
            try:
                import requests
                csv_bytes = requests.get("http://127.0.0.1:8000/api/export/powerbi?format=csv", timeout=10).content
            except Exception:
                csv_bytes = b""
            st.download_button(
                "📥 Download Ready CSV Dataset",
                data=csv_bytes,
                file_name=f"vp_info_powerbi_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        with p2:
            st.code("http://127.0.0.1:8000/api/export/powerbi?format=json", language="text")
            st.caption("Paste into Power BI &rarr; Get Data &rarr; Web")


# =============================================================================
# 2. RM DASHBOARD
# =============================================================================
def render_rm_dashboard():
    st.subheader("👔 Relationship Manager Command Center")

    tab_generate, tab_dash, tab_leadboard = st.tabs([
        "➕ Generate Prospect Lead (RM Intake)",
        "📊 RM Performance & Team Pipeline",
        "🏆 Relationship Manager Leaderboard"
    ])

    with tab_generate:
        st.markdown("### 📝 Log Prospect Meeting")
        st.info("ℹ️ **Process Note:** Leads raised by Relationship Managers are assigned to Sales Consultants by **Admin**.")

        existing_leads = api.get_leads()
        next_lead_no = f"VP-{datetime.now().year}-{len(existing_leads)+1:04d}"

        with st.form("rm_lead_form", clear_on_submit=True):
            st.markdown(f"**Lead Number:** `{next_lead_no}` *(Auto-generated)*")
            
            c1, c2 = st.columns(2)
            with c1:
                company_name = st.text_input("Name of Company *", placeholder="e.g. Mahavir Engineering Works")
                person_name = st.text_input("Name of the Person to Meet *", placeholder="e.g. Suresh Jain")
                designation = st.text_input("Their Designation *", placeholder="e.g. Managing Director / CFO")
                phone = st.text_input("Contact Number *", placeholder="e.g. +91 98220 12345")
                email = st.text_input("Email Address", placeholder="e.g. contact@mahavirengg.com")

            with c2:
                product = st.selectbox("Which Product They Are Interested *", PRODUCT_OPTIONS)
                meeting_date = st.date_input("Meeting Date *", min_value=datetime.today())
                meeting_time = st.text_input("Meeting Timings *", placeholder="e.g. 11:30 AM")
                address = st.text_area("Company / Meeting Address *", placeholder="e.g. Plot 18, Phase 1, Hinjewadi IT Park, Pune")

            notes = st.text_area("Requirement Details / Notes", placeholder="Customer wants on-premise multi-user setup with customized invoice printing...")
            submit_rm_lead = st.form_submit_button("Submit Lead for Admin Assignment →", type="primary", use_container_width=True)

            if submit_rm_lead:
                if not company_name or not person_name or not phone or not address:
                    st.error("Please fill in all mandatory fields: Company, Person to Meet, Phone, and Address.")
                else:
                    payload = {
                        "business_name": company_name,
                        "lead_name": person_name,
                        "designation": designation,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "meeting_date": str(meeting_date),
                        "meeting_time": meeting_time,
                        "industry": "Corporate",
                        "interested_product": product,
                        "status": "New",
                        "estimated_value": 0.0,
                        "notes": notes
                    }
                    res = api.create_lead(payload)
                    if res["success"]:
                        st.success(f"Lead `{res['data']['lead_number']}` for '{company_name}' raised successfully! Routed to Admin for allocation.")
                        st.rerun()
                    else:
                        st.error(f"Failed to submit lead: {res.get('error')}")

    with tab_dash:
        st.markdown("### 📊 Regional Performance Overview")
        my_user = st.session_state.user_info
        user_id = my_user.get("id") or my_user.get("user_id")
        
        rm_leads = api.get_leads(rm_id=user_id)
        raised_by_me = [l for l in rm_leads if l.get("created_by_id") == user_id]
        won_deals = [l for l in rm_leads if l.get("status") == "Won"]
        open_deals = [l for l in rm_leads if l.get("status") not in ["Won", "Lost"]]
        pipe_val = sum(l.get("estimated_value", 0) for l in rm_leads)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card card-blue">
                <div class="metric-label">Leads Raised By Me</div>
                <div class="metric-value">{len(raised_by_me)}</div>
                <div class="metric-sub" style="color: #2563EB;">Prospects Sourced</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card card-amber">
                <div class="metric-label">Team Active Pipeline</div>
                <div class="metric-value">{len(open_deals)}</div>
                <div class="metric-sub" style="color: #D97706;">In Progress Deals</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card card-green">
                <div class="metric-label">Closed Won Deals</div>
                <div class="metric-value">{len(won_deals)}</div>
                <div class="metric-sub" style="color: #059669;">Finalized Contracts</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card card-gold">
                <div class="metric-label">Team Gross Pipeline</div>
                <div class="metric-value" style="font-size: 21px;">₹{pipe_val:,.0f}</div>
                <div class="metric-sub" style="color: #B45309;">Estimated Value</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Regional Pipeline Roster")
        if not rm_leads:
            st.info("No leads currently registered under your regional team.")
        else:
            df_rm_view = pd.DataFrame(rm_leads)
            st.dataframe(
                df_rm_view[["lead_number", "business_name", "lead_name", "phone", "interested_product", "status", "sales_person_name", "meeting_date", "meeting_time"]].rename(columns={
                    "lead_number": "Lead Number",
                    "business_name": "Company Name",
                    "lead_name": "Person to Meet",
                    "phone": "Phone",
                    "interested_product": "Product",
                    "status": "Stage",
                    "sales_person_name": "Assigned SC",
                    "meeting_date": "Meeting Date",
                    "meeting_time": "Meeting Timings"
                }),
                use_container_width=True,
                height=300
            )

    with tab_leadboard:
        st.markdown("### 🏆 Relationship Manager Leaderboard")
        rm_lb = api.get_rm_leaderboard()
        if rm_lb:
            df_rmlb = pd.DataFrame(rm_lb)
            st.dataframe(
                df_rmlb[["rm_name", "leads_raised", "team_reps_count", "team_total_leads", "team_closed_won", "team_conversion_rate", "team_pipeline_value"]].rename(columns={
                    "rm_name": "Relationship Manager",
                    "leads_raised": "Leads Raised",
                    "team_reps_count": "Assigned SCs",
                    "team_total_leads": "Total Team Leads",
                    "team_closed_won": "Closed Won Deals",
                    "team_conversion_rate": "Conversion Rate %",
                    "team_pipeline_value": "Pipeline Value (₹)"
                }),
                use_container_width=True,
                height=240
            )


# =============================================================================
# 3. SALES CONSULTANT DASHBOARD
# =============================================================================
def render_sales_consultant_dashboard():
    st.subheader("🎯 Sales Consultant Workspace")

    tab_pipeline, tab_direct_lead, tab_sc_dash, tab_sc_lb = st.tabs([
        "📋 My Assigned Pipeline & Stage Updates",
        "➕ Log Direct Lead",
        "📊 Personal Performance",
        "🏆 Sales Consultant Leaderboard"
    ])

    my_leads = api.get_leads()

    with tab_pipeline:
        st.markdown("### 📋 Active Pipeline & Stage Progression")
        st.caption("Update stage progression with interaction audit notes.")

        if not my_leads:
            st.info("No leads currently assigned to you.")
        else:
            df_my = pd.DataFrame(my_leads)
            cols = [
                "lead_number", "business_name", "lead_name", "designation",
                "phone", "email", "address", "meeting_date", "meeting_time",
                "interested_product", "status", "created_by_name", "notes"
            ]
            for col in cols:
                if col not in df_my.columns:
                    df_my[col] = "—"

            st.dataframe(
                df_my[cols].rename(columns={
                    "lead_number": "Lead #",
                    "business_name": "Company Name",
                    "lead_name": "Person to Meet",
                    "designation": "Designation",
                    "phone": "Phone Number",
                    "email": "Email Address",
                    "address": "Meeting Address",
                    "meeting_date": "Meeting Date",
                    "meeting_time": "Meeting Timings",
                    "interested_product": "Interested Product",
                    "status": "Current Stage",
                    "created_by_name": "Generated by RM",
                    "notes": "Requirement Details (RM)"
                }),
                use_container_width=True,
                height=280
            )

            st.markdown("#### ⚡ Quick Stage Progression & RM Prospect Dossier")
            lead_select_map = {f"{l['lead_number']} - {l['business_name']} ({l['lead_name']}) [Stage: {l['status']}]": l['id'] for l in my_leads}
            
            chosen_lead_label = st.selectbox("Select Lead to View Details & Update Stage:", list(lead_select_map.keys()))
            chosen_lead_id = lead_select_map.get(chosen_lead_label)
            target_lead_obj = next((l for l in my_leads if l["id"] == chosen_lead_id), None)

            if target_lead_obj:
                rm_author = target_lead_obj.get("created_by_name") or target_lead_obj.get("rm_name") or "Direct Submission"
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 5px solid #2563EB; border-radius: 12px; padding: 20px 24px; margin-top: 15px; margin-bottom: 22px; box-shadow: 0 4px 8px -2px rgba(0,0,0,0.06);">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 14px;">
                        <div>
                            <span style="font-size: 19px; font-weight: 800; color: #0F172A;">🏢 {target_lead_obj.get('business_name')}</span>
                            <span style="background: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; font-size: 12px; font-weight: 800; padding: 3px 10px; border-radius: 6px; margin-left: 10px;">
                                {target_lead_obj.get('lead_number')}
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 12px; color: #64748B; font-weight: 600;">Generated by RM:</span>
                            <span style="font-size: 12px; font-weight: 800; color: #0284C7; background: #E0F2FE; border: 1px solid #BAE6FD; padding: 3px 10px; border-radius: 6px;">
                                👔 {rm_author}
                            </span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; font-size: 13.5px;">
                        <div>
                            <span style="color: #64748B; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">👤 Person to Meet</span>
                            <div style="font-weight: 800; color: #0F172A; margin-top: 4px; font-size: 15px;">{target_lead_obj.get('lead_name')}</div>
                            <div style="font-size: 12px; color: #64748B; margin-top: 2px;">{target_lead_obj.get('designation') or 'Designation not specified'}</div>
                        </div>
                        <div>
                            <span style="color: #64748B; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">📅 Meeting Schedule</span>
                            <div style="font-weight: 800; color: #0F172A; margin-top: 4px; font-size: 15px;">📆 {target_lead_obj.get('meeting_date') or 'To be scheduled'}</div>
                            <div style="font-size: 12px; color: #2563EB; font-weight: 700; margin-top: 2px;">⏰ {target_lead_obj.get('meeting_time') or 'Flexible timings'}</div>
                        </div>
                        <div>
                            <span style="color: #64748B; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">📞 Contact Information</span>
                            <div style="font-weight: 800; color: #0F172A; margin-top: 4px; font-size: 15px;">📱 {target_lead_obj.get('phone')}</div>
                            <div style="font-size: 12px; color: #475569; margin-top: 2px;">✉️ {target_lead_obj.get('email') or 'No email provided'}</div>
                        </div>
                        <div>
                            <span style="color: #64748B; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">📦 Product Interest</span>
                            <div style="font-weight: 800; color: #D97706; margin-top: 4px; font-size: 14px;">★ {target_lead_obj.get('interested_product')}</div>
                            <div style="font-size: 12px; color: #059669; font-weight: 700; margin-top: 2px;">Current Stage: {target_lead_obj.get('status')}</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px; padding-top: 12px; border-top: 1px dashed #CBD5E1; display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <span style="color: #64748B; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">📍 Company / Meeting Address (From RM)</span>
                            <div style="color: #1E293B; margin-top: 4px; font-weight: 500; font-size: 13px; background: #F8FAFC; padding: 8px 12px; border-radius: 8px; border: 1px solid #E2E8F0; line-height: 1.4;">
                                {target_lead_obj.get('address') or 'Address not recorded by RM'}
                            </div>
                        </div>
                        <div>
                            <span style="color: #64748B; font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">📝 Requirement Notes (Entered by RM)</span>
                            <div style="color: #1E293B; margin-top: 4px; font-size: 13px; background: #F8FAFC; padding: 8px 12px; border-radius: 8px; border: 1px solid #E2E8F0; line-height: 1.4; white-space: pre-wrap;">
                                {target_lead_obj.get('notes') or 'No notes entered by RM'}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                u_c1, u_c2, u_c3 = st.columns([1.5, 2.5, 1.2])
                with u_c1:
                    curr_idx = STATUS_OPTIONS.index(target_lead_obj["status"]) if target_lead_obj["status"] in STATUS_OPTIONS else 0
                    new_st = st.selectbox("Progress Stage To:", STATUS_OPTIONS, index=curr_idx)
                with u_c2:
                    update_notes = st.text_input("Interaction Details / Meeting Summary", placeholder="e.g. Conducted product demo for Accounts team...")
                with u_c3:
                    won_val_input = 0.0
                    if new_st == "Won":
                        won_val_input = st.number_input("Final Won Deal Price (₹)", min_value=0.0, value=float(target_lead_obj.get("estimated_value") or 50000.0), step=5000.0)
                    else:
                        st.write("")
                    st.write("")
                    if st.button("Update Stage →", type="primary", use_container_width=True):
                        est_val_to_send = won_val_input if new_st == "Won" else None
                        res = api.update_lead_status(chosen_lead_id, new_st, update_notes, estimated_value=est_val_to_send)
                        if res["success"]:
                            st.success(f"Lead stage progressed to '{new_st}'!")
                            st.rerun()
                        else:
                            st.error(f"Error: {res.get('error')}")

    with tab_direct_lead:
        st.markdown("### ➕ Log Direct Prospect Lead")
        st.caption("Prospects logged here are directly allocated to your own pipeline.")

        all_l = api.get_leads()
        preview_no = f"VP-{datetime.now().year}-{len(all_l)+1:04d}"

        with st.form("sc_direct_lead_form", clear_on_submit=True):
            st.markdown(f"**Lead Number:** `{preview_no}` *(Auto-generated)*")
            
            c1, c2 = st.columns(2)
            with c1:
                d_company = st.text_input("Name of Company *", placeholder="e.g. Sunrise Polyesters")
                d_person = st.text_input("Name of Person to Meet *", placeholder="e.g. Anish Shah")
                d_desig = st.text_input("Designation", placeholder="e.g. Commercial Manager")
                d_phone = st.text_input("Contact Number *", placeholder="e.g. +91 98111 22334")
                d_email = st.text_input("Email", placeholder="e.g. anish@sunrisepoly.com")

            with c2:
                d_product = st.selectbox("Which Product They Are Interested *", PRODUCT_OPTIONS)
                d_date = st.date_input("Meeting Date", min_value=datetime.today())
                d_time = st.text_input("Meeting Timings", placeholder="e.g. 03:00 PM")
                d_address = st.text_area("Address", placeholder="e.g. GIDC Industrial Estate, Sachin, Surat")

            d_notes = st.text_area("Notes", placeholder="Met client at industrial expo. Wants TallyPrime gold upgrade...")
            submit_direct = st.form_submit_button("Save Directly to My Pipeline →", type="primary", use_container_width=True)

            if submit_direct:
                if not d_company or not d_person or not d_phone:
                    st.error("Please fill in Company, Person to Meet, and Phone Number.")
                else:
                    payload = {
                        "business_name": d_company,
                        "lead_name": d_person,
                        "designation": d_desig,
                        "phone": d_phone,
                        "email": d_email,
                        "address": d_address,
                        "meeting_date": str(d_date),
                        "meeting_time": d_time,
                        "industry": "Corporate",
                        "interested_product": d_product,
                        "status": "New",
                        "estimated_value": 0.0,
                        "notes": d_notes
                    }
                    res = api.create_lead(payload)
                    if res["success"]:
                        st.success(f"Lead `{res['data']['lead_number']}` logged directly to your pipeline!")
                        st.rerun()
                    else:
                        st.error(f"Error: {res.get('error')}")

    with tab_sc_dash:
        st.markdown("### 📊 Personal Performance Metrics")
        kpis = api.get_personal_kpis()

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(f"""
            <div class="metric-card card-blue">
                <div class="metric-label">My Total Leads</div>
                <div class="metric-value">{kpis.get('my_total_leads', 0)}</div>
                <div class="metric-sub" style="color: #2563EB;">Assigned + Direct</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card card-amber">
                <div class="metric-label">My Open Deals</div>
                <div class="metric-value">{kpis.get('my_open_deals', 0)}</div>
                <div class="metric-sub" style="color: #D97706;">In Active Stages</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card card-green">
                <div class="metric-label">My Closed Won</div>
                <div class="metric-value">{kpis.get('my_closed_won', 0)}</div>
                <div class="metric-sub" style="color: #059669;">Finalized Contracts</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card card-purple">
                <div class="metric-label">My Win Rate</div>
                <div class="metric-value">{kpis.get('my_win_rate', 0)}%</div>
                <div class="metric-sub" style="color: #7C3AED;">Conversion Ratio</div>
            </div>
            """, unsafe_allow_html=True)
        with c5:
            pipe_v = f"₹{kpis.get('my_total_pipeline_value', 0):,.0f}"
            st.markdown(f"""
            <div class="metric-card card-gold">
                <div class="metric-label">Total Pipeline</div>
                <div class="metric-value" style="font-size: 21px;">{pipe_v}</div>
                <div class="metric-sub" style="color: #B45309;">Estimated Value</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_sc_lb:
        st.markdown("### 🏆 Company Sales Consultant Standings & Leaderboard")
        sc_lb = api.get_sc_leaderboard()
        if sc_lb:
            df_sclb = pd.DataFrame(sc_lb)
            st.dataframe(
                df_sclb[["sc_name", "total_assigned", "won", "not_interested", "win_rate", "price_on_win"]].rename(columns={
                    "sc_name": "Sales Consultant",
                    "total_assigned": "Total Assigned",
                    "won": "Won",
                    "not_interested": "Not Interested",
                    "win_rate": "Win Rate (%)",
                    "price_on_win": "Price on Win (₹)"
                }),
                use_container_width=True,
                height=260
            )


# =============================================================================
# MAIN CONTROLLER & ROUTING
# =============================================================================
def main():
    if not st.session_state.authenticated or not st.session_state.user_info:
        render_login()
        return

    render_header()

    with st.sidebar:
        user = st.session_state.user_info
        role_label = user.get("role", "Unknown")
        role_badge_bg = {
            "Admin": "background: linear-gradient(135deg, #7C3AED, #9333EA);",
            "RM": "background: linear-gradient(135deg, #0284C7, #0369A1);",
            "Sales Consultant": "background: linear-gradient(135deg, #059669, #10B981);",
            "Sales Person": "background: linear-gradient(135deg, #059669, #10B981);"
        }.get(role_label, "background: #475569;")

        st.markdown(f"""
        <div style="background: #0F2342; border: 1px solid #1E3A5F; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);">
            <div style="font-size: 11px; text-transform: uppercase; color: #94A3B8; font-weight: 700; letter-spacing: 0.8px;">
                ACTIVE SESSION
            </div>
            <div style="margin-top: 10px; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 13px; color: #E2E8F0; font-weight: 600;">Logged in:</span>
                <span style="font-size: 13px; color: #F59E0B; font-weight: 800; background: #1E293B; border: 1px solid #334155; padding: 3px 10px; border-radius: 6px; letter-spacing: 0.3px;">
                    {user.get('username')}
                </span>
            </div>
            <div style="margin-top: 10px; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 13px; color: #E2E8F0; font-weight: 600;">Role:</span>
                <span style="{role_badge_bg} color: #FFFFFF !important; font-size: 12px; font-weight: 800; padding: 4px 12px; border-radius: 6px; letter-spacing: 0.4px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                    {role_label}
                </span>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #1E2E4A; font-size: 12px; color: #CBD5E1; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                <span>👤</span>
                <span>{user.get('full_name')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.session_state.user_info["role"] != "Admin":
            if st.button("👑 Switch to Admin View", use_container_width=True):
                res = api.login("VP Info solutions", "vpinfo@123")
                if res["success"]:
                    st.session_state.user_info = res["data"]
                    st.session_state.token = res["data"]["access_token"]
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Sign Out", type="secondary", use_container_width=True):
            logout()

        st.markdown("""
        <div style="font-size: 11px; color: #64748B; margin-top: 40px; text-align: center; border-top: 1px solid #1E293B; padding-top: 15px;">
            <strong style="color: #94A3B8;">VP INFO SOLUTIONS PVT LTD</strong><br>
            Tally Certified Partner<br>
            Enterprise Edition v2.5
        </div>
        """, unsafe_allow_html=True)

    role = st.session_state.user_info["role"]
    if role == "Admin":
        render_admin_dashboard()
    elif role == "RM":
        render_rm_dashboard()
    elif role in ["Sales Consultant", "Sales Person"]:
        render_sales_consultant_dashboard()
    else:
        st.error(f"Unrecognized role '{role}'. Please contact system administrator.")


if __name__ == "__main__":
    main()
