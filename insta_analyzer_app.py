import json
import io
import zipfile
import streamlit as st
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
import matplotlib.pyplot as plt

# Funkcije za ucitavanje username-a iz podataka JSON struktura

def load_usernames_following_from_data(data):
    usernames = set()
    for entry in data.get("relationships_following", []):
        if 'string_list_data' in entry and entry['string_list_data']:
            username = entry['string_list_data'][0]['value'].strip().lower()
            usernames.add(username)
    return usernames

def load_usernames_followers_from_data(data):
    usernames = set()
    for entry in data:
        if 'string_list_data' in entry and entry['string_list_data']:
            username = entry['string_list_data'][0]['value'].strip().lower()
            usernames.add(username)
    return usernames

# CSS stil
st.markdown("""
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5);
        min-height: 100vh;
        margin: 0;
        padding: 0 20px 40px 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: white;
    }
    .card {
        background-color: white !important;
        color: black !important;
        border-radius: 15px;
        padding: 15px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgb(0 0 0 / 0.1);
    }
    .header-box {
        background-color: white !important;
        color: black !important;
        border-radius: 15px;
        padding: 12px 18px;
        margin-top: 20px;
        margin-bottom: 15px;
        font-weight: 700;
        font-size: 22px;
        box-shadow: 0 4px 10px rgb(0 0 0 / 0.15);
        text-align: center;
    }
    a {
        color: #4f5bd5;
        font-weight: 600;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    .tutorial {
        background-color: rgba(255, 255, 255, 0.85);
        color: black;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        font-size: 16px;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Instagram Follower Analyzer")

uploaded_zip = st.file_uploader("Upload your Instagram Data ZIP file", type=["zip"])

st.markdown("""
<div class="tutorial">
<h2>How to Download Your Instagram Data for Analysis</h2>
<ol>
<li>Open Instagram and go to <strong>Settings & Activity</strong>.</li>
<li>Navigate to <strong>Accounts Centre</strong>.</li>
<li>Click on <strong>Your Information and Permissions</strong>.</li>
<li>Select <strong>Download or Transfer Your Information</strong>.</li>
<li>Choose to download your data.</li>
<li>Some of your data includes <strong>Followers and Following</strong> lists.</li>
<li>Submit your request and wait for the data to be prepared.</li>
<li>Download the ZIP file from Instagram.</li>
<li>Upload the ZIP file here to analyze your followers and following.</li>
</ol>
</div>
""", unsafe_allow_html=True)
if uploaded_zip is not None:
    try:
        with zipfile.ZipFile(io.BytesIO(uploaded_zip.read())) as z:
            try:
                followers_json = z.read('connections/followers_and_following/followers_1.json').decode('utf-8')
                following_json = z.read('connections/followers_and_following/following.json').decode('utf-8')
            except KeyError:
                st.error("ZIP file does not contain required JSON files in 'connections/followers_and_following/'. Please check your ZIP file.")
                st.stop()

            try:
                followers_data = json.loads(followers_json)
                following_data = json.loads(following_json)
            except json.JSONDecodeError:
                st.error("Error reading JSON files.")
                st.stop()

            followers = set(load_usernames_followers_from_data(followers_data))
            following = set(load_usernames_following_from_data(following_data))

            not_following_you_back = following - followers
            you_dont_follow_back = followers - following
            mutual_follow = followers & following

            st.markdown('<div class="header-box">Users You Follow But Don’t Follow You Back</div>', unsafe_allow_html=True)
            with st.expander(f"Show {len(not_following_you_back)} users"):
                for user in sorted(not_following_you_back):
                    st.markdown(f'<div class="card"><a href="https://instagram.com/{user}" target="_blank">{user}</a></div>', unsafe_allow_html=True)

            st.markdown('<div class="header-box">Users Who Follow You But You Don’t Follow Back</div>', unsafe_allow_html=True)
            with st.expander(f"Show {len(you_dont_follow_back)} users"):
                for user in sorted(you_dont_follow_back):
                    st.markdown(f'<div class="card"><a href="https://instagram.com/{user}" target="_blank">{user}</a></div>', unsafe_allow_html=True)

            st.markdown(f"""
                <div style="margin-top:30px; color:white; font-weight:600; text-align:center;">
                    Total Following: {len(following)}<br>
                    Total Followers: {len(followers)}
                </div>
            """, unsafe_allow_html=True)

            # Pie chart
            st.markdown('<div class="header-box">Follower Relationship Chart</div>', unsafe_allow_html=True)

            labels = ['Not Following You Back', 'You Don\'t Follow Them', 'Mutual Following']
            sizes = [len(not_following_you_back), len(you_dont_follow_back), len(mutual_follow)]
            colors = ['#ff9999','#66b3ff','#99ff99']

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload a ZIP file downloaded from Instagram containing your data.")
