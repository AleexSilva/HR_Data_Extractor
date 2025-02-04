import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

# Workable API details
API_KEY = st.secrets["API_KEY"]
SUBDOMAIN = st.secrets["SUBDOMAIN"]
BASE_URL = f'https://{SUBDOMAIN}.workable.com/spi/v3/candidates'


# Headers for authentication
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Jobs mapping
jobs_map = {'React Native Engineer': '9F423CF31C',
 'Recruiter for Latin America': '20962EBA53',
 'Inside Sales Representative': '16101648B9',
 'Data Engineer': '605700F3F7', 
 'Java Engineer': '3E9DDCE12D', 
 'Fullstack JavaScript Developer': '77D039A996',
 'Software Sales Executive': 'CEC0ED4BE5',
 'QA Automation Engineer': '643969844B',
 'Account Solutions Manager': '860CF32BB0',
 'Sales Analyst': '45237D7C70',
 'Golang Backend Engineer': '99EC2490DC',
 'Sales Development Rep Manager': '2050EF2401',
 'BA/PM': '635C0EC084', 
 'UX/UI Designer': 'F584A7354D',
 'Fullstack .Net Developer': '7A1291A379',
 'Cloud DevOps Engineer': '878233D828',
 'Python Engineer': 'B71932FDCC',
 'Ruby on Rails Engineer': '370C1B53C9', 
 'Frontend Engineer': 'F21BAC1F76',
 'Technical Leader (Python)': '669B1AB086', 
 'Software Architect': 'C431D2E2F2',
 'Unity Developer': 'BB40E45E98', 
 'Unreal Engine': 'D5418CE609',
 'Talent Management Senior Analyst': '8ADD7CB5C3', 
 'Marketing Coordinator': 'B2D2CA7C56', 
 '01': 'A8343B88C8', 
 'NodeJs Developer': 'C6EE6D91DA', 
 'QA Manual Engineer': '63033CEE6D', 
 'CTO (Chief Technology Officer)': 'BAEAF6704F', 
 'Data Analyst': 'F4EB0C6635', 
 'PHP Developer': '3F4CE8CFAC', 
 'DBA': 'A4E7E5A34F', 
 'iOS Developer': 'FD517A39A1', 
 'Data Scientist': '20F590E233', 
 'Business Development Representative (US Market)': '2F991DA396', 
 'SRE': 'F3D67B1765', 
 'Android Developer': '4E31CEDF71',
 'Oracle CPQ': '70DC7F1B41', 
 'Corporative Graphic Designer': '66A6717DF4', 
 'Software Architect Javascript': '1013EB9BCA', 
 'Video Game Producer': '1EF8EC60DC'}


# Set a secure password for access
CORRECT_PASSWORD = st.secrets["PASSWORD"]
# Logo URL
LOGO_URL = st.secrets["LOGO_URL"]

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# **Login Page with Logo**
if not st.session_state.authenticated:
    st.image(LOGO_URL, width=150)  # Display logo at the top
    st.title("🔐 Secure Access")
    
    password = st.text_input("Enter Password:", type="password")

    if st.button("Login"):
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True  # Set session state to logged in
            st.empty()  # Forces UI refresh
            st.rerun()  # Refresh the page
        else:
            st.error("❌ Incorrect password. Please try again.")

else:
    # **Main App with Logo**
    col1, col2 = st.columns([0.2, 0.8])  # Create layout for logo + title
    with col1:
        st.image(LOGO_URL, width=100)  # Display logo in top-left corner
    with col2:
        st.title("📊 Workable Candidates Explorer")

    # User input for date filter
    created_after = st.date_input("📅 Select 'Created After' Date:", datetime.today()).strftime('%Y-%m-%d')

    # User input for job selection
    selected_jobs = st.multiselect("🔽 Select Jobs:", list(jobs_map.keys()))

    # Initialize session state for candidates data
    if "candidates_df" not in st.session_state:
        st.session_state.candidates_df = None

    # **Fetch candidates button**
    if st.button("🚀 Fetch Candidates"):
        if not selected_jobs:
            st.warning("⚠️ Please select at least one job.")
        else:
            with st.spinner("Fetching candidates..."):
                # API Call
                all_candidates = []
                for job in selected_jobs:
                    shortcode = jobs_map.get(job)
                    url = f"{BASE_URL}?shortcode={shortcode}&limit=10000&created_after={created_after}"
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get('candidates', [])
                        all_candidates.extend(candidates)
                    else:
                        st.error(f"❌ Failed to fetch data for {job} (Status: {response.status_code})")

                if all_candidates:
                    # Convert to DataFrame
                    def convert_datetime(timestamp):
                        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") if timestamp else None

                    df = pd.DataFrame([
                        {
                            "ID": c.get("id"),
                            "Name": c.get("name"),
                            "Job Title": c.get("job", {}).get("title", "").split(" - ")[0],
                            "Job Shortcode": c.get("job", {}).get("shortcode", ""),
                            "Stage": c.get("stage"),
                            "Disqualified": c.get("disqualified"),
                            "Disqualification Reason": c.get("disqualification_reason"),
                            "Hired At": c.get("hired_at"),
                            "Profile URL": c.get("profile_url"),
                            "Phone": c.get("phone"),
                            "Email": c.get("email"),
                            "Created At": convert_datetime(c.get("created_at")),
                            "Updated At": convert_datetime(c.get("updated_at"))
                        }
                        for c in all_candidates
                    ])

                    # Apply Default Filtering: Remove Disqualified = True
                    df = df[df["Disqualified"] == False]

                    # Hide Default Columns
                    hidden_columns = ["Job Shortcode", "Disqualified", "Disqualification Reason", "Hired At"]
                    df_visible = df.drop(columns=hidden_columns)

                    # Store in session state
                    st.session_state.candidates_df = df_visible

    # **Show data only if candidates exist in session state**
    if st.session_state.candidates_df is not None:
        df_visible = st.session_state.candidates_df.copy()  # Work with a copy to avoid modifying session data

        # **Row Selection Dropdown**
        row_options = [50, 100, 200, 300]
        num_rows = st.selectbox("📊 Number of records to display:", row_options, index=1, help="Changing this may take a few seconds to process.")

        # **Filters Section (Stays Visible)**
        st.write("### 🛠️ Apply Additional Filters")

        job_filter = st.multiselect("Filter by Job Title:", df_visible["Job Title"].unique(), default=df_visible["Job Title"].unique())
        stage_filter = st.multiselect("Filter by Stage:", df_visible["Stage"].unique(), default=df_visible["Stage"].unique())
        name_search = st.text_input("🔍 Search by Name:")

        if st.button("🔄 Apply Filters"):
            df_visible = df_visible[
                df_visible["Job Title"].isin(job_filter) &
                df_visible["Stage"].isin(stage_filter)
            ]

            if name_search:
                df_visible = df_visible[df_visible["Name"].str.contains(name_search, case=False, na=False)]

        # **Show the filtered Data**
        st.write(f"### Showing {len(df_visible)} candidates")
        st.dataframe(df_visible.head(num_rows))  # Show only selected number of rows

        # **Show total count at bottom right**
        st.markdown(f"**Total Candidates: {len(df_visible)}**", unsafe_allow_html=True)

        # **Download button**
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        st.download_button(
            label="📥 Download Filtered Data",
            data=to_excel(df_visible),
            file_name=f"candidates_{created_after}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )