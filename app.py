import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Tamil Nadu Assembly Elections (2021 vs 2026) Dashboard",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Main page style */
        .reportview-container {
            background-color: #0c0f17;
            font-family: 'Outfit', sans-serif;
        }
        
        /* Heading styles */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
            font-weight: 700;
        }
        
        /* Custom card elements */
        .insight-card {
            background: linear-gradient(135deg, #1b2030 0%, #111522 100%);
            border: 1px solid #2b324c;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .insight-card:hover {
            transform: translateY(-5px);
            border-color: #3b4566;
            box-shadow: 0 8px 30px 0 rgba(0, 0, 0, 0.4);
        }
        
        /* Metrics styling */
        .metric-title {
            color: #8f9cae;
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .metric-value {
            color: #ffffff;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .metric-delta-positive {
            color: #00e676;
            font-size: 14px;
            font-weight: 600;
        }
        
        .metric-delta-negative {
            color: #ff1744;
            font-size: 14px;
            font-weight: 600;
        }
        
        /* Highlight labels */
        .highlight-tvk {
            background: linear-gradient(90deg, #7b1fa2, #e040fb);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .highlight-dmk {
            background: linear-gradient(90deg, #d32f2f, #ff5252);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        .highlight-admk {
            background: linear-gradient(90deg, #388e3c, #69f0ae);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #0f131c;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background-color: #1e2538;
            color: #ffffff;
            border: 1px solid #323c58;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #2a344d;
            border-color: #7b1fa2;
            color: #ffffff;
        }
        
        .navigation-header {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 15px;
            border-bottom: 2px solid #7b1fa2;
            padding-bottom: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to load data
@st.cache_data
def load_data():
    df_21 = pd.read_csv("election_results_2021.csv")
    df_26 = pd.read_csv("election_results_2026.csv")
    df_master = pd.read_csv("constituency_master.csv")
    
    # Standardize column values
    df_21['ac_name_clean'] = df_21['ac_name'].str.upper().str.replace(r'\s*\(SC\)\s*', '', regex=True).str.replace(r'\s*\(ST\)\s*', '', regex=True).str.strip()
    df_26['ac_name_clean'] = df_26['ac_name'].str.upper().str.replace(r'\s*\(SC\)\s*', '', regex=True).str.replace(r'\s*\(ST\)\s*', '', regex=True).str.strip()
    
    # Standardize party groups
    df_21['party_group'] = df_21['party_group'].fillna('Others')
    df_26['party_group'] = df_26['party_group'].fillna('Others')
    
    # Group standardisation for simplicity
    valid_groups = ['DMK+', 'ADMK+', 'TVK+', 'NTK', 'MNM', 'NOTA', 'IND']
    df_21['party_group_clean'] = df_21['party_group'].apply(lambda x: x if x in valid_groups else 'Others')
    df_26['party_group_clean'] = df_26['party_group'].apply(lambda x: x if x in valid_groups else 'Others')
    
    # Merge with master data
    df_21 = df_21.merge(df_master, left_on='ac_no', right_on='ac_number', how='left')
    df_26 = df_26.merge(df_master, left_on='ac_no', right_on='ac_number', how='left')
    
    return df_21, df_26

df_2021, df_2026 = load_data()

# Precompute Winners
w_2021 = df_2021[df_2021['rank'] == 1].copy().set_index('ac_no')
w_2026 = df_2026[df_2026['rank'] == 1].copy().set_index('ac_no')

# Precompute Transitions
transitions = w_2021[['ac_name', 'party_group_clean', 'candidate_name', 'total', 'pct_votes', 'region', 'district', 'reserved']].join(
    w_2026[['ac_name', 'party_group_clean', 'candidate_name', 'total', 'pct_votes', 'region', 'district', 'reserved']],
    lsuffix='_2021', rsuffix='_2026'
)

# Global Color Palette Map for political alliances
color_map = {
    'TVK+': '#7A1FA2',
    'DMK+': '#E30613',
    'ADMK+': '#008000',
    'NTK': '#FFEB3B',
    'MNM': '#00BCD4',
    'Others': '#757575',
    'NOTA': '#9E9E9E',
    'IND': '#BDBDBD'
}

# Sidebar View Format Selection
st.sidebar.markdown('<div class="navigation-header">🗺️ Dashboard View Mode</div>', unsafe_allow_html=True)
view_mode = st.sidebar.selectbox(
    "Choose View Layout", 
    ["📽️ Slide Deck Presentation", "📊 PowerBI Unified Dashboard"]
)

if view_mode == "📊 PowerBI Unified Dashboard":
    st.title("📊 PowerBI-Style Unified Election Dashboard")
    st.subheader("Tamil Nadu Assembly Elections: Multi-Year Analysis Dashboard")
    
    st.markdown("### 🎛️ Dashboard Filters")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        dashboard_year = st.selectbox("Select Election Year", ["2026 Election", "2021 Election"])
    
    # Determine raw active dataset first
    df_raw_active = df_2026 if "2026" in dashboard_year else df_2021
    df_w_active = df_2026[df_2026['rank'] == 1].copy() if "2026" in dashboard_year else df_2021[df_2021['rank'] == 1].copy()

    with col_f2:
        regions_list = ["All"] + sorted(list(df_raw_active['region'].dropna().unique()))
        region_filter = st.selectbox("Select Region", regions_list)
        
    with col_f3:
        if region_filter == "All":
            districts_list = ["All"] + sorted(list(df_raw_active['district'].dropna().unique()))
        else:
            districts_list = ["All"] + sorted(list(df_raw_active[df_raw_active['region'] == region_filter]['district'].dropna().unique()))
        district_filter = st.selectbox("Select District", districts_list)
        
    with col_f4:
        category_filter = st.selectbox("Constituency Category", ["All", "GEN", "SC", "ST"])

    # Second row filters
    col_f5, col_f6 = st.columns(2)
    
    with col_f5:
        gender_filter = st.selectbox("Winner Gender Filter", ["All", "MALE", "FEMALE"])
        
    with col_f6:
        min_age = int(df_raw_active['age'].min())
        max_age = int(df_raw_active['age'].max())
        age_range = st.slider("Candidate Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
    
    # Apply category filter
    if category_filter != "All":
        df_w_active = df_w_active[df_w_active['reserved'] == category_filter]
        
    # Apply gender filter
    if gender_filter != "All":
        df_w_active = df_w_active[df_w_active['gender'] == gender_filter]
        
    # Apply region filter
    if region_filter != "All":
        df_w_active = df_w_active[df_w_active['region'] == region_filter]
        
    # Apply district filter
    if district_filter != "All":
        df_w_active = df_w_active[df_w_active['district'] == district_filter]
        
    # Apply age filter
    df_w_active = df_w_active[(df_w_active['age'] >= age_range[0]) & (df_w_active['age'] <= age_range[1])]

    total_constituencies = len(df_w_active)
    
    # Electors and Turnout
    ac_nos = df_w_active['ac_no'].unique()
    df_raw_filtered = df_raw_active[df_raw_active['ac_no'].isin(ac_nos)]
    
    if len(ac_nos) > 0:
        total_electors = df_raw_filtered.groupby('ac_no')['total_electors'].first().sum()
        total_votes = df_raw_filtered.groupby('ac_no')['total'].sum().sum()
        turnout_pct = (total_votes / total_electors * 100) if total_electors > 0 else 0
    else:
        total_electors = 0
        total_votes = 0
        turnout_pct = 0
        
    avg_age = df_w_active['age'].mean() if len(df_w_active) > 0 else 0
    female_winners = len(df_w_active[df_w_active['gender'] == 'FEMALE'])
    
    # Render KPI Cards
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    
    with col_c1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="metric-title">Total Filtered Seats</div>
            <div class="metric-value">{total_constituencies} / 234</div>
            <div style="font-size: 12px; color: #8f9cae;">Selected filter subset</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="metric-title">Voter Turnout</div>
            <div class="metric-value">{turnout_pct:.2f}%</div>
            <div style="font-size: 12px; color: #8f9cae;">Votes polled: {total_votes:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="metric-title">Average Winner Age</div>
            <div class="metric-value">{avg_age:.1f} Yrs</div>
            <div style="font-size: 12px; color: #8f9cae;">Mean age of winning MLAs</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c4:
        st.markdown(f"""
        <div class="insight-card">
            <div class="metric-title">Female Winners</div>
            <div class="metric-value">{female_winners}</div>
            <div style="font-size: 12px; color: #8f9cae;">{female_winners / max(1, total_constituencies) * 100:.1f}% representation</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Render Charts Grid
    col_ch1, col_ch2 = st.columns(2)
    
    seats_breakdown = df_w_active['party_group_clean'].value_counts().reset_index()
    seats_breakdown.columns = ['Party Group', 'Seats']
    
    with col_ch1:
        fig_donut = px.pie(
            seats_breakdown,
            values='Seats',
            names='Party Group',
            color='Party Group',
            color_discrete_map=color_map,
            hole=0.4,
            title=f"Seats Breakdown ({dashboard_year})"
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+value')
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_ch2:
        votes_breakdown = df_raw_filtered.groupby('party_group_clean')['total'].sum().reset_index()
        votes_breakdown['Vote Share %'] = (votes_breakdown['total'] / votes_breakdown['total'].sum() * 100) if votes_breakdown['total'].sum() > 0 else 0
        
        fig_votes_bar = px.bar(
            votes_breakdown,
            x='party_group_clean',
            y='Vote Share %',
            color='party_group_clean',
            color_discrete_map=color_map,
            title=f"Vote Share Breakdown (%) ({dashboard_year})",
            labels={'party_group_clean': 'Party Group'}
        )
        st.plotly_chart(fig_votes_bar, use_container_width=True)

    col_row3_1, col_row3_2 = st.columns(2)
    
    with col_row3_1:
        margins_active = []
        for ac_no_g, group in df_raw_filtered.groupby('ac_no'):
            sorted_g = group.sort_values('rank')
            if len(sorted_g) >= 2:
                winner = sorted_g.iloc[0]
                runner_up = sorted_g.iloc[1]
                margin_votes = winner['total'] - runner_up['total']
                margins_active.append({
                    'Constituency': winner['ac_name'],
                    'Winner': winner['candidate_name'],
                    'Party': winner['party'],
                    'Margin': margin_votes
                })
        
        if len(margins_active) > 0:
            df_margins_active = pd.DataFrame(margins_active).sort_values('Margin', ascending=False)
            fig_margins = px.bar(
                df_margins_active.head(10),
                x='Margin',
                y='Constituency',
                orientation='h',
                color='Party',
                title=f"Top 10 Victory Margins ({dashboard_year})"
            )
            st.plotly_chart(fig_margins, use_container_width=True)
        else:
            st.info("No margin data available for this subset.")
            
    with col_row3_2:
        if len(df_w_active) > 0:
            fig_hist = px.histogram(
                df_w_active,
                x='age',
                nbins=15,
                title=f"MLAs Age Distribution Histogram ({dashboard_year})",
                labels={'age': 'Age (Years)'},
                color_discrete_sequence=['#7A1FA2']
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No age data available.")

    st.markdown("### 📋 Filtered Winners List")
    st.dataframe(
        df_w_active[['ac_no', 'ac_name', 'region', 'district', 'reserved', 'candidate_name', 'gender', 'age', 'party', 'total', 'pct_votes']]
        .rename(columns={
            'ac_no': 'AC No', 'ac_name': 'Constituency', 'region': 'Region', 'district': 'District', 'reserved': 'Category',
            'candidate_name': 'Winner Name', 'gender': 'Gender', 'age': 'Age', 'party': 'Party',
            'total': 'Votes', 'pct_votes': 'Votes %'
        })
        .style.format({'Votes': '{:,}', 'Votes %': '{:.2f}%'}),
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export Selected Data as CSV",
        data=df_w_active.to_csv(index=False).encode('utf-8'),
        file_name=f"election_dashboard_data_{category_filter}_{gender_filter}_{region_filter}_{district_filter}.csv",
        mime='text/csv'
    )
    
    st.stop()

# Sidebar Navigation (Story Presentation Format)
st.sidebar.markdown('<div class="navigation-header">📽️ Presentation Slides</div>', unsafe_allow_html=True)


slide_options = [
    "1. 📊 Executive Summary",
    "2. 🏛️ Seat & Vote Share Swings",
    "3. 🔄 Seat Transitions Matrix",
    "4. 🗺️ Regional & District Performance",
    "5. 📊 Victory Margins & Contests",
    "6. 👥 Demographics (Age & Gender)",
    "7. 🔍 Constituency Explorer"
]

# Session state to track current slide selection
if 'slide_radio' not in st.session_state:
    st.session_state.slide_radio = slide_options[0]

# Sidebar radio selection synced with session state
selected_slide_str = st.sidebar.radio(
    "Select Slide", 
    slide_options, 
    key="slide_radio"
)

# Extract index from selection
slide_index = slide_options.index(selected_slide_str)

# Content based on selected slide
if slide_index == 0:
    # ----------------------------------------------------
    # Slide 1: Executive Summary
    # ----------------------------------------------------
    st.title("🗳️ Tamil Nadu Election Insights: The 2026 Political Disruption")
    st.subheader("Executive Summary & Core Takeaways")
    
    st.markdown("""
    In the **2026 Tamil Nadu Legislative Assembly Election**, the political landscape experienced a historic shift. 
    The newly formed **Tamizhaga Vettri Kazhagam (TVK)**, led by actor-politician **C. Joseph Vijay**, disrupted the traditional 
    duopoly of DMK+ and ADMK+, emerging as the single largest party with **108 seats**.
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="insight-card">
            <div class="metric-title">TVK+ Debut Seats</div>
            <div class="metric-value">108 / 234</div>
            <div class="metric-delta-positive">▲ Debut Winner (Single Largest)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="insight-card">
            <div class="metric-title">Voter Turnout</div>
            <div class="metric-value">85.91%</div>
            <div class="metric-delta-positive">▲ +12.45% (from 73.46%)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="insight-card">
            <div class="metric-title">Average Winner Age</div>
            <div class="metric-value">52.0 Years</div>
            <div class="metric-delta-negative">▼ -3.9 Years (Youth Surge)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="insight-card">
            <div class="metric-title">Female Winners</div>
            <div class="metric-value">23 MLAs</div>
            <div class="metric-delta-positive">▲ +11 (Doubled Representation)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🔑 Key Takeaways")
    st.markdown("""
    - **Dravidian Duopoly Broken**: For the first time in decades, neither DMK+ nor ADMK+ secured a majority. TVK+ won **108 seats** (34.9% vote share), relegating DMK+ to **73 seats** (31.4% vote share) and ADMK+ to **53 seats** (27.2% vote share).
    - **Turnout Surge**: Voter turnout increased by over 12 percentage points, reaching **85.91%**. This shows a high level of voter mobilization and anti-incumbency engagement, heavily favoring the new player.
    - **High-Profile Upsets**: Several veteran politicians lost their seats. Most notably, incumbent DMK Chief Minister **M. K. Stalin** was defeated in his stronghold of *Kolathur* by TVK's **V. S. Babu**.
    - **Younger, Diverse Assembly**: The average age of winning MLAs dropped to 52.0 years (from 55.9), and women’s representation doubled from 12 to 23 MLAs.
    """)

elif slide_index == 1:
    # ----------------------------------------------------
    # Slide 2: Seat & Vote Share Swings
    # ----------------------------------------------------
    st.title("🏛️ Seat & Vote Share Swings (2021 vs 2026)")
    st.subheader("Comparing Assembly Composition and Popular Vote Shares")
    
    col1, col2 = st.columns(2)
    
    # Data aggregation for seats
    seats_21 = w_2021['party_group_clean'].value_counts().reset_index()
    seats_21.columns = ['Party Group', 'Seats 2021']
    
    seats_26 = w_2026['party_group_clean'].value_counts().reset_index()
    seats_26.columns = ['Party Group', 'Seats 2026']
    
    seats_df = pd.merge(seats_21, seats_26, on='Party Group', how='outer').fillna(0)
    
    
    with col1:
        st.markdown("### Seat Distribution Shift")
        
        # Donut Chart for 2021
        fig_seats_21 = px.pie(
            seats_21, 
            values='Seats 2021', 
            names='Party Group',
            color='Party Group',
            color_discrete_map=color_map,
            hole=0.4,
            title="Assembly Composition 2021 (Total: 234)"
        )
        fig_seats_21.update_traces(textposition='inside', textinfo='percent+value')
        st.plotly_chart(fig_seats_21, use_container_width=True)
        
        # Donut Chart for 2026
        fig_seats_26 = px.pie(
            seats_26, 
            values='Seats 2026', 
            names='Party Group',
            color='Party Group',
            color_discrete_map=color_map,
            hole=0.4,
            title="Assembly Composition 2026 (Total: 234)"
        )
        fig_seats_26.update_traces(textposition='inside', textinfo='percent+value')
        st.plotly_chart(fig_seats_26, use_container_width=True)
        
    with col2:
        st.markdown("### Vote Share Collapse & Rise")
        
        # Vote share aggregation
        votes_21 = df_2021.groupby('party_group_clean')['total'].sum().reset_index()
        votes_21['Vote Share %'] = (votes_21['total'] / votes_21['total'].sum()) * 100
        votes_21['Year'] = '2021'
        
        votes_26 = df_2026.groupby('party_group_clean')['total'].sum().reset_index()
        votes_26['Vote Share %'] = (votes_26['total'] / votes_26['total'].sum()) * 100
        votes_26['Year'] = '2026'
        
        vote_share_compare = pd.concat([votes_21, votes_26])
        vote_share_compare = vote_share_compare[vote_share_compare['party_group_clean'].isin(['TVK+', 'DMK+', 'ADMK+', 'NTK', 'Others'])]
        
        fig_votes = px.bar(
            vote_share_compare, 
            x='party_group_clean', 
            y='Vote Share %', 
            color='Year',
            barmode='group',
            color_discrete_sequence=['#ff4b4b', '#7a1fa2'],
            title="Popular Vote Share Comparison (%)",
            labels={'party_group_clean': 'Party Group'}
        )
        st.plotly_chart(fig_votes, use_container_width=True)
        
        st.markdown("""
        **Observations on Vote Shares**:
        - **TVK+** captured a massive **34.92%** of the popular vote in its debut, reflecting a powerful wave of voter enthusiasm.
        - **DMK+** saw its vote share fall by **14.0%** (from 45.38% to 31.39%).
        - **ADMK+** saw its vote share drop by **12.5%** (from 39.72% to 27.22%).
        - **NTK** (Naam Tamilar Katchi) fell from 6.58% to 4.00%, indicating that third-party voters consolidated strongly around TVK.
        """)

elif slide_index == 2:
    # ----------------------------------------------------
    # Slide 3: Seat Transitions
    # ----------------------------------------------------
    st.title("🔄 Seat Transitions Matrix")
    st.subheader("Where did TVK's 108 Seats Come From?")
    
    # Create transition matrix data
    cross_tab = pd.crosstab(
        transitions['party_group_clean_2021'], 
        transitions['party_group_clean_2026']
    )
    
    view_type = st.radio("Select View Type", ["📊 Sankey Flow Diagram", "🎛️ Heatmap Matrix"], horizontal=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        if "Sankey" in view_type:
            # Source nodes: ADMK+ (2021) -> 0, DMK+ (2021) -> 1
            # Target nodes: ADMK+ (2026) -> 2, DMK+ (2026) -> 3, TVK+ (2026) -> 4
            fig_sankey = go.Figure(data=[go.Sankey(
                node = dict(
                  pad = 15,
                  thickness = 20,
                  line = dict(color = "black", width = 0.5),
                  label = ["ADMK+ (2021: 75)", "DMK+ (2021: 159)", "ADMK+ (2026: 53)", "DMK+ (2026: 73)", "TVK+ (2026: 108)"],
                  color = ["#4CAF50", "#F44336", "#2E7D32", "#C62828", "#9C27B0"]
                ),
                link = dict(
                  source = [0, 0, 0, 1, 1, 1],
                  target = [2, 3, 4, 2, 3, 4],
                  value = [25, 20, 30, 28, 53, 78],
                  color = ["rgba(76, 175, 80, 0.4)", "rgba(76, 175, 80, 0.4)", "rgba(76, 175, 80, 0.4)",
                           "rgba(244, 67, 54, 0.4)", "rgba(244, 67, 54, 0.4)", "rgba(244, 67, 54, 0.4)"]
                )
            )])
            fig_sankey.update_layout(title_text="Seat Flows from 2021 to 2026 Alliances", font_size=12)
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            # Plot Heatmap
            fig_heat = px.imshow(
                cross_tab,
                labels=dict(x="2026 Party Group (Winner)", y="2021 Party Group (Incumbent)", color="Seats"),
                x=cross_tab.columns,
                y=cross_tab.index,
                text_auto=True,
                color_continuous_scale="Purples",
                title="Seat Gains and Losses Matrix (2021 vs 2026)"
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        
    with col2:
        st.markdown("### Analysis of Seat Swings")
        st.markdown("""
        The transition matrix shows exactly how the seats shifted between coalitions:
        
        - **TVK's Gains**:
          - Won **78 seats** that were previously held by <span class="highlight-dmk">DMK+</span>.
          - Won **30 seats** that were previously held by <span class="highlight-admk">ADMK+</span>.
          - In total, **72.2%** of TVK's seats came from former DMK+ strongholds, while **27.8%** came from ADMK+.
          
        - **DMK's Deficit**:
          - DMK+ retained only **53** of its 159 seats from 2021.
          - DMK+ won **20** seats from ADMK+.
          - DMK+ lost **78** seats to TVK+ and **28** seats to ADMK+.
          
        - **ADMK's Deficit**:
          - ADMK+ retained only **25** of its 75 seats.
          - ADMK+ won **28** seats from DMK+.
          - ADMK+ lost **30** seats to TVK+ and **20** seats to DMK+.
        """, unsafe_allow_html=True)
        
        # Add a metric highlighting the swing
        st.info("💡 **Key Insight**: TVK disproportionately damaged the ruling DMK+ coalition, capturing nearly half of the seats DMK+ won in 2021.")

elif slide_index == 3:
    # ----------------------------------------------------
    # Slide 4: Regional & District Performance
    # ----------------------------------------------------
    st.title("🗺️ Regional & District Performance")
    st.subheader("Seat Composition, Reservation Swings, and District-Wise Win Distribution")
    
    # Regional Seat counts comparing 2021 vs 2026
    seats_reg_21 = w_2021.groupby(['region', 'party_group_clean']).size().reset_index(name='Seats')
    seats_reg_21['Year'] = '2021'
    seats_reg_26 = w_2026.groupby(['region', 'party_group_clean']).size().reset_index(name='Seats')
    seats_reg_26['Year'] = '2026'
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_reg_21 = px.bar(
            seats_reg_21,
            x='region',
            y='Seats',
            color='party_group_clean',
            barmode='group',
            color_discrete_map=color_map,
            title="Regional Seat Share - 2021 (Total: 234)",
            labels={'party_group_clean': 'Alliance', 'region': 'Region', 'Seats': 'Seats Won'}
        )
        fig_reg_21.update_layout(xaxis_title="Region", yaxis_title="Seats Won", legend_title="Alliance")
        st.plotly_chart(fig_reg_21, use_container_width=True)
        
    with col_chart2:
        fig_reg_26 = px.bar(
            seats_reg_26,
            x='region',
            y='Seats',
            color='party_group_clean',
            barmode='group',
            color_discrete_map=color_map,
            title="Regional Seat Share - 2026 (Total: 234)",
            labels={'party_group_clean': 'Alliance', 'region': 'Region', 'Seats': 'Seats Won'}
        )
        fig_reg_26.update_layout(xaxis_title="Region", yaxis_title="Seats Won", legend_title="Alliance")
        st.plotly_chart(fig_reg_26, use_container_width=True)
        
    col_row2_1, col_row2_2 = st.columns(2)
    
    with col_row2_1:
        # Stacked bar chart showing 2026 seat share by reservation status (GEN, SC, ST)
        seats_res_26 = w_2026.groupby(['reserved', 'party_group_clean']).size().reset_index(name='Seats')
        fig_res_26 = px.bar(
            seats_res_26,
            x='reserved',
            y='Seats',
            color='party_group_clean',
            barmode='stack',
            color_discrete_map=color_map,
            title="2026 Seats won by Reservation Category",
            labels={'party_group_clean': 'Alliance', 'reserved': 'Category', 'Seats': 'Seats Won'}
        )
        fig_res_26.update_layout(xaxis_title="Reservation Status (GEN/SC/ST)", yaxis_title="Seats Won")
        st.plotly_chart(fig_res_26, use_container_width=True)
        
    with col_row2_2:
        st.markdown("### 📊 Regional Swing Analysis")
        st.markdown(f"""
        The integration of constituency master data reveals major regional patterns:
        
        * 🏙️ **Chennai Metro Sweep**: <span class="highlight-tvk">TVK+</span> won **29/32** seats in the Chennai Metro region (a former DMK+ stronghold which they swept 32/32 in 2021). 
        * 🌾 **Kongu Resurgence**: TVK+ won **16/33** seats in the Kongu region, leading DMK+ (9) and ADMK+ (8).
        * ⚖️ **South & North Splits**:
          - In the South, DMK+ retained **27** seats and TVK+ won **26** (a neck-and-neck fight).
          - In the North, ADMK+ led with **16** seats, followed by TVK+ with **15** and DMK+ with **6**.
        * 🛡️ **Reservation Dynamics**: 
          - Of the 44 **SC** seats, TVK+ won **23**, DMK+ won **13**, and ADMK+ won **8**.
          - Of the 2 **ST** seats, TVK+ and ADMK+ won **1** each.
        """, unsafe_allow_html=True)
        
    st.markdown("### 📋 District-wise Seat Breakdown (2021 vs 2026)")
    # Generate district-wise table
    dist_21 = w_2021.groupby(['district', 'party_group_clean']).size().unstack(fill_value=0)
    dist_26 = w_2026.groupby(['district', 'party_group_clean']).size().unstack(fill_value=0)
    
    # Align columns
    for group in ['DMK+', 'ADMK+', 'TVK+']:
        if group not in dist_21.columns:
            dist_21[group] = 0
        if group not in dist_26.columns:
            dist_26[group] = 0
            
    dist_21.columns = [f"{col} (2021)" for col in dist_21.columns]
    dist_26.columns = [f"{col} (2026)" for col in dist_26.columns]
    
    dist_compare = dist_21.join(dist_26, how='outer').fillna(0).astype(int)
    dist_compare['Total Seats'] = dist_compare[[col for col in dist_compare.columns if '(2026)' in col]].sum(axis=1)
    dist_compare = dist_compare.sort_values('Total Seats', ascending=False).reset_index()
    
    # Reorder columns for readability
    cols_order = ['district', 'Total Seats', 'DMK+ (2021)', 'ADMK+ (2021)', 'DMK+ (2026)', 'ADMK+ (2026)', 'TVK+ (2026)']
    cols_order = [c for c in cols_order if c in dist_compare.columns]
    
    st.dataframe(
        dist_compare[cols_order].rename(columns={
            'district': 'District',
            'Total Seats': 'Total Seats'
        }),
        use_container_width=True,
        hide_index=True
    )

elif slide_index == 4:
    # ----------------------------------------------------
    # Slide 5: Victory Margins & Closest Contests
    # ----------------------------------------------------
    st.title("📊 Victory Margins & Contests Analysis")
    st.subheader("Analyzing the Widest and Closest Wins in the 2026 Election")
        
    # Calculate margins for all 2026 seats
    margins_26 = []
    for ac_no, group in df_2026.groupby('ac_no'):
        sorted_g = group.sort_values('rank')
        if len(sorted_g) >= 2:
            winner = sorted_g.iloc[0]
            runner_up = sorted_g.iloc[1]
            margin_votes = winner['total'] - runner_up['total']
            margins_26.append({
                'Constituency No': ac_no,
                'Constituency': winner['ac_name'],
                'Winner': winner['candidate_name'],
                'Winner Party': winner['party'],
                'Runner Up': runner_up['candidate_name'],
                'Runner Party': runner_up['party'],
                'Winner Votes': winner['total'],
                'Runner Votes': runner_up['total'],
                'Margin (Votes)': margin_votes,
                'Margin %': round(winner['pct_votes'] - runner_up['pct_votes'], 2)
            })
            
    margins_df = pd.DataFrame(margins_26).sort_values('Margin (Votes)')

    st.markdown("### 📊 Victory Margins Analysis")
    tab1, tab2 = st.tabs(["🏆 Top 10 Highest Victory Margins", "🎯 Top 10 Closest Contests"])
    
    with tab1:
        top_margins = margins_df.tail(10).copy()
        fig_top = px.bar(
            top_margins,
            x='Margin (Votes)',
            y='Constituency',
            orientation='h',
            text='Margin (Votes)',
            color='Winner Party',
            color_discrete_map={'TVK': '#7A1FA2', 'DMK': '#E30613', 'ADMK': '#008000', 'INC': '#42A5F5'},
            title="Top 10 Highest Victory Margins in 2026"
        )
        fig_top.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig_top, use_container_width=True)
        
    with tab2:
        bottom_margins = margins_df.head(10).copy()
        fig_bottom = px.bar(
            bottom_margins,
            x='Margin (Votes)',
            y='Constituency',
            orientation='h',
            text='Margin (Votes)',
            color='Winner Party',
            color_discrete_map={'TVK': '#7A1FA2', 'DMK': '#E30613', 'ADMK': '#008000', 'INC': '#42A5F5', 'PMK': '#FFD700', 'DMDK': '#00BCD4', 'CPI(M)': '#FF5722'},
            title="Top 10 Closest Contests (Lowest Victory Margins) in 2026"
        )
        fig_bottom.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig_bottom, use_container_width=True)

    st.markdown("### 🔍 Full Margins Table")
    st.dataframe(
        margins_df.style.format({'Winner Votes': '{:,}', 'Runner Votes': '{:,}', 'Margin (Votes)': '{:,}', 'Margin %': '{:.2f}%'}),
        use_container_width=True
    )
    
    st.markdown("---")
    # Enable CSV Export
    st.download_button(
        label="📥 Export Full 2026 Victory Margins CSV",
        data=margins_df.to_csv(index=False).encode('utf-8'),
        file_name='tn_election_margins_2026.csv',
        mime='text/csv',
    )

elif slide_index == 5:
    # ----------------------------------------------------
    # Slide 6: Demographics (Age & Gender)
    # ----------------------------------------------------
    st.title("👥 Demographic Shifts in Assembly Winners")
    st.subheader("Analyzing the Age Profiles and Gender Balance of Winning MLAs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Age Distribution of Winners")
        
        age_view = st.radio("Age Visual Type", ["📊 Histogram Overlay", "📦 Box Plot Comparison"], horizontal=True)
        if "Histogram" in age_view:
            fig_age = go.Figure()
            fig_age.add_trace(go.Histogram(x=w_2021['age'], name='2021 Winners', opacity=0.75, marker_color='#E30613'))
            fig_age.add_trace(go.Histogram(x=w_2026['age'], name='2026 Winners', opacity=0.75, marker_color='#7A1FA2'))
            fig_age.update_layout(
                barmode='overlay',
                title_text="Age Comparison of Winning Candidates",
                xaxis_title_text="Age (Years)",
                yaxis_title_text="Count",
                bargap=0.1
            )
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            age_box_df = pd.concat([
                pd.DataFrame({'Age': w_2021['age'], 'Year': '2021 Winners'}),
                pd.DataFrame({'Age': w_2026['age'], 'Year': '2026 Winners'})
            ])
            fig_box = px.box(
                age_box_df,
                x='Year',
                y='Age',
                color='Year',
                color_discrete_map={'2021 Winners': '#E30613', '2026 Winners': '#7A1FA2'},
                title="Winner Age Spread Comparison"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        st.markdown("""
        **Age Insights**:
        - The **mean age** of winning MLAs dropped significantly from **55.9 years** to **52.0 years**.
        - In 2026, a surge of young winners emerged, with the youngest winners being **28 years old** (e.g. Kamali.s from Avanashi, Sabari Iyngaran G. from Periyakulam).
        - TVK fielded several younger candidates, leading to a rejuvenized legislative assembly.
        """)
        
    with col2:
        st.markdown("### Gender Representation")
        
        gender_21 = w_2021['gender'].value_counts().reset_index()
        gender_21.columns = ['Gender', 'Count']
        gender_21['Year'] = '2021'
        
        gender_26 = w_2026['gender'].value_counts().reset_index()
        gender_26.columns = ['Gender', 'Count']
        gender_26['Year'] = '2026'
        
        gender_df = pd.concat([gender_21, gender_26])
        
        fig_gender = px.bar(
            gender_df,
            x='Year',
            y='Count',
            color='Gender',
            barmode='group',
            color_discrete_sequence=['#42a5f5', '#ec407a'],
            title="Winners by Gender (2021 vs 2026)"
        )
        st.plotly_chart(fig_gender, use_container_width=True)
        
        st.markdown("""
        **Gender Balance Insights**:
        - **Female winners** nearly doubled, rising from **12 MLAs** (5.1% of assembly) in 2021 to **23 MLAs** (9.8% of assembly) in 2026.
        - While male winners still dominate (211 out of 234 in 2026), the rise in female representation marks a progressive shift in the state's legislative history.
        """)

elif slide_index == 6:
    # ----------------------------------------------------
    # Slide 7: Constituency Explorer
    # ----------------------------------------------------
    st.title("🔍 Constituency Explorer")
    st.subheader("Compare 2021 and 2026 Results Side-by-Side")
    
    # Sort constituencies by name
    constituencies = sorted(df_2026['ac_name_clean'].unique())
    selected_ac = st.selectbox("Select a Constituency", constituencies)
    
    # Find AC number based on name
    ac_no = df_2026[df_2026['ac_name_clean'] == selected_ac]['ac_no'].iloc[0]
    
    # Retrieve data for selected AC
    data_21 = df_2021[df_2021['ac_no'] == ac_no].sort_values('rank')
    data_26 = df_2026[df_2026['ac_no'] == ac_no].sort_values('rank')
    
    winner_21 = data_21.iloc[0]
    winner_26 = data_26.iloc[0]
    
    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
    
    with col_meta1:
        st.markdown(f"""
        <div class="insight-card" style="padding: 15px; text-align: center;">
            <div class="metric-title">Constituency No & Name</div>
            <h4 style="margin: 5px 0 0 0; color: white;">#{ac_no} {selected_ac}</h4>
        </div>
        """, unsafe_allow_html=True)
        
    with col_meta2:
        # Swing type
        swing_text = f"{winner_21['party_group_clean']} to {winner_26['party_group_clean']}"
        swing_color = "#00e676" if winner_21['party_group_clean'] != winner_26['party_group_clean'] else "#8f9cae"
        
        st.markdown(f"""
        <div class="insight-card" style="padding: 15px; text-align: center;">
            <div class="metric-title">Swing Type</div>
            <h4 style="margin: 5px 0 0 0; color: {swing_color};">{swing_text}</h4>
        </div>
        """, unsafe_allow_html=True)
        
    with col_meta3:
        # Margin change
        margin_21 = winner_21['total'] - data_21.iloc[1]['total']
        margin_26 = winner_26['total'] - data_26.iloc[1]['total']
        margin_diff = margin_26 - margin_21
        delta_sign = "+" if margin_diff >= 0 else ""
        delta_color = "color:#00e676;" if margin_diff >= 0 else "color:#ff1744;"
        
        st.markdown(f"""
        <div class="insight-card" style="padding: 15px; text-align: center;">
            <div class="metric-title">2026 Margin of Victory</div>
            <h4 style="margin: 5px 0 0 0; color: white;">{margin_26:,} votes <span style="font-size:12px; {delta_color} font-weight:600;">({delta_sign}{margin_diff:,})</span></h4>
        </div>
        """, unsafe_allow_html=True)

    with col_meta4:
        st.markdown(f"""
        <div class="insight-card" style="padding: 15px; text-align: center;">
            <div class="metric-title">Region | District | Category</div>
            <h4 style="margin: 5px 0 0 0; color: white; font-size: 15px;">{winner_26['region']} | {winner_26['district']} | {winner_26['reserved']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 📅 2021 Election Results")
        
        # Turnout Card
        turnout_21_pct = (data_21['total'].sum() / winner_21['total_electors']) * 100
        st.markdown(f"**Total Electors:** {winner_21['total_electors']:,} | **Voter Turnout:** {turnout_21_pct:.2f}%")
        
        st.dataframe(
            data_21[['rank', 'candidate_name', 'party', 'party_group_clean', 'total', 'pct_votes']]
            .rename(columns={'pct_votes': 'Votes %', 'total': 'Votes', 'party_group_clean': 'Alliance'}),
            use_container_width=True,
            hide_index=True
        )
        
    with col_right:
        st.markdown("### 📅 2026 Election Results")
        
        turnout_26_pct = (data_26['total'].sum() / winner_26['total_electors']) * 100
        st.markdown(f"**Total Electors:** {winner_26['total_electors']:,} | **Voter Turnout:** {turnout_26_pct:.2f}%")
        
        st.dataframe(
            data_26[['rank', 'candidate_name', 'party', 'party_group_clean', 'total', 'pct_votes']]
            .rename(columns={'pct_votes': 'Votes %', 'total': 'Votes', 'party_group_clean': 'Alliance'}),
            use_container_width=True,
            hide_index=True
        )

# Slide Pagination at the bottom
st.markdown("---")
col_prev, col_center, col_next = st.columns([1, 4, 1])

def prev_slide(current_idx):
    if current_idx > 0:
        st.session_state.slide_radio = slide_options[current_idx - 1]

def next_slide(current_idx):
    if current_idx < len(slide_options) - 1:
        st.session_state.slide_radio = slide_options[current_idx + 1]

with col_prev:
    st.button("⬅️ Previous Slide", on_click=prev_slide, args=(slide_index,), use_container_width=True)

with col_center:
    st.markdown(f"<div style='text-align: center; color: #8f9cae; padding-top: 5px;'>Slide {slide_index + 1} of {len(slide_options)}</div>", unsafe_allow_html=True)

with col_next:
    st.button("Next Slide ➡️", on_click=next_slide, args=(slide_index,), use_container_width=True)
