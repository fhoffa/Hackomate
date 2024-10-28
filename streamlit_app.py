import pandas as pd
import streamlit as st
import google.generativeai as ggi

conn = st.connection("neon", type="sql")
# df = conn.query('SELECT * FROM participants;', ttl="1m")
# for row in df.itertuples():
#     st.write(
#         f"{row.name} skills are :{row.skills}:, and interested in {row.interested_in}. Find them on {row.url}")


st.image(
    "https://i.imgur.com/8Db5CpT.png",
    width=200,  # Manually Adjust the width of the image as per requirement
)

# Initialize session state variables
if 'show_sponsor_form' not in st.session_state:
    st.session_state.show_sponsor_form = False
if 'show_participant_form' not in st.session_state:
    st.session_state.show_participant_form = False
if 'show_project_form' not in st.session_state:
    st.session_state.show_project_form = False
if 'show_requests_modal' not in st.session_state:
    st.session_state.show_requests_modal = False
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None

# Initialize join_requests dynamically
if 'join_requests' not in st.session_state:
    st.session_state.join_requests = {}

if 'current_user' not in st.session_state:
    st.session_state.current_user = None


st.title("Hackomate")

# Sponsors Data
# db_sponsors = [
#     ['Sponsor Name', 'Website URL', 'Features'],
#     ['Stori', 'https://www.stori.com', 'Stori leverages AI to provide personalized financial solutions, empowering users to take control of their finances with tailored insights and tools.'],
#     ['Neon', 'https://neon.tech', 'Neon is a cutting-edge AI platform that enhances productivity by automating workflows and enabling intelligent collaboration across teams.'],
#     ['Defi', 'https://defi.com', 'Defi utilizes AI to revolutionize decentralized finance, offering secure and innovative solutions for users to manage their digital assets effectively.'],
#     ['Edge', 'https://edge.ai', 'Edge harnesses AI technology to deliver real-time insights and analytics, optimizing decision-making for businesses in various sectors.'],
#     ['Weaviate', 'https://weaviate.io', 'Weaviate is an open-source vector search engine that utilizes AI to enable efficient and intelligent data retrieval, facilitating seamless information access.'],
#     ['Toolhouse', 'https://toolhouse.ai',
#         'Toolhouse combines AI-driven tools with a collaborative environment to streamline project management and enhance team productivity.'],
#     ['Restack', 'https://restack.io', 'Restack employs AI to simplify and optimize cloud infrastructure management, ensuring efficient resource allocation and scalability for enterprises.'],
# ]

st.header("Sponsors")

# Get sponsors data from database
sponsors_df = conn.query('SELECT name,features FROM sponsors;', ttl="1m")

# Rename columns for display
sponsors_df = sponsors_df.rename(columns={
    'name': 'Sponsor Name',
    # 'url': 'Website URL',
    'features': 'Features'
})

st.dataframe(sponsors_df)

if st.button('Add Sponsor'):
    st.session_state.show_sponsor_form = not st.session_state.show_sponsor_form

if st.session_state.show_sponsor_form:
    with st.form("sponsor_form"):
        sponsor_name = st.text_input("Sponsor Name")
        # website_url = st.text_input("Website URL")
        features = st.text_area("Features")
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Add to database
            conn.execute(f"""
                INSERT INTO sponsors (name, url, features) 
                VALUES ('{sponsor_name}', '{features}');
            """)
            st.success("Sponsor added successfully!")
            st.session_state.show_sponsor_form = False
            st.rerun()

# project_df = pd.DataFrame(db_sponsors[1:], columns=db_sponsors[0])
# st.dataframe(project_df)

# if st.button('Add Sponsor'):
#     st.session_state.show_sponsor_form = not st.session_state.show_sponsor_form

# if st.session_state.show_sponsor_form:
#     with st.form("sponsor_form"):
#         sponsor_name = st.text_input("Sponsor Name")
#         website_url = st.text_input("Website URL")
#         features = st.text_area("Features")
#         submitted = st.form_submit_button("Submit")
#         if submitted:
#             # Add logic to save sponsor data
#             st.success("Sponsor added successfully!")
#             st.session_state.show_sponsor_form = False


# Participants Data
# db_participants = [
#     ['Participant Name', 'LinkedIn URL', 'Skills'],
#     ['Felipe Hoffa', 'https://linkedin.com/in/hoffa', ['Data', 'Python']],
#     ['Asako', 'https://www.linkedin.com/in/asako-hayase-924508ba/', ['Marketing', 'UX']],
#     ['Aninda', 'https://www.linkedin.com/in/aninda-sengupta/', ['Java', 'Python']],
#     ['Gulsher', 'https://www.linkedin.com/in/gulsher-kooner/', ['Data', 'Spark']],
# ]

st.header("Participants")
# Get participants data from database
participants_df = conn.query(
    'SELECT name, url, interested_in, skills FROM participants;', ttl="1m")

# Rename columns to match the expected format
participants_df = participants_df.rename(columns={
    'name': 'Name',
    'url': 'LinkedIn URL',
    'interested_in': 'Interests',
    'skills': 'Skills'
})

st.dataframe(participants_df)

if st.button('Add Participant'):
    st.session_state.show_participant_form = not st.session_state.show_participant_form

if st.session_state.show_participant_form:
    with st.form("participant_form"):
        participant_name = st.text_input("Participant Name")
        linkedin_url = st.text_input("LinkedIn URL")
        skills = st.text_input("Skills (comma-separated)")
        interested_in = st.text_area("Interested in")
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Add to database
            conn.execute(f"""
                INSERT INTO participants (name, url, skills, interested_in) 
                VALUES ('{participant_name}', '{linkedin_url}', '{skills}', '{interested_in}');
            """)
            st.success("Participant added successfully!")
            st.session_state.show_participant_form = False
            st.rerun()

# project_df = pd.DataFrame(db_participants[1:], columns=db_participants[0])
# st.dataframe(project_df)

# if st.button('Add Participant'):
#     st.session_state.show_participant_form = not st.session_state.show_participant_form

# if st.session_state.show_participant_form:
#     with st.form("participant_form"):
#         participant_name = st.text_input("Participant Name")
#         linkedin_url = st.text_input("LinkedIn URL")
#         skills = st.text_input("Skills (comma-separated)")
#         submitted = st.form_submit_button("Submit")
#         if submitted:
#             # Add logic to save participant data
#             st.success("Participant added successfully!")
#             st.session_state.show_participant_form = False


# Projects Data
db_projects = [
    ['Project Title', 'Idea', 'Leader', 'Members', 'Skills'],
    [
        'Smart Health Tracker',
        'An AI-powered wearable device that monitors health metrics in real-time and provides personalized health insights.',
        'Alice Johnson',
        ['Alice Johnson', 'Michael Lee', 'Sarah Patel'],
        ['AI Development', 'Wearable Technology', 'Health Data Analysis']
    ],
    [
        'Eco-Friendly Packaging',
        'A sustainable packaging solution that uses biodegradable materials and minimizes environmental impact.',
        'David Kim',
        ['David Kim', 'Emma Chen', 'Lucas Martinez'],
        ['Product Design', 'Sustainability Engineering', 'Material Science']
    ],
    [
        'Virtual Learning Assistant',
        'An AI-driven platform that personalizes online learning experiences based on individual student needs and progress.',
        'Nina Garcia',
        ['Nina Garcia', 'James Smith', 'Olivia Brown'],
        ['Machine Learning', 'Education Technology', 'User Experience Design']
    ],
    [
        'Smart Home Energy Management',
        'A system that optimizes energy usage in homes by learning user patterns and suggesting efficient energy-saving practices.',
        'John Doe',
        ['John Doe', 'Rachel Green', 'Ethan White'],
        ['IoT Development', 'Energy Management', 'Data Analytics']
    ],
    [
        'Community Engagement App',
        'A mobile app that connects local communities, facilitating event organization and communication among residents.',
        'Sophia Turner',
        ['Sophia Turner', 'Daniel Harris', 'Mia Wilson'],
        ['App Development', 'Community Building', 'Social Media Marketing']
    ],
]

st.header("Project Ideas")
project_df = conn.query(
    'SELECT title, idea,skills_needed FROM ideas;', ttl="1m")


project_df = project_df.rename(columns={
    'title': 'Title',
    'idea': 'Idea',
    'skills_needed': 'Required Skills'
})


# Display projects with cards and join request functionality
# Display projects with cards
for index, row in project_df.iterrows():
    with st.container():
        # Custom CSS with black text in tags
        st.markdown("""
            <style>
            .project-card {
                background-color: white;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .project-title {
                color: #0569a0;
                font-size: 1.5rem;
                margin-bottom: 1rem;
            }
            .project-detail {
                color: #333;
                margin: 0.5rem 0;
            }
            .skills-tag {
                background-color: #f0f2f6;
                color: black;
                padding: 0.2rem 0.5rem;
                border-radius: 15px;
                margin-right: 0.5rem;
                display: inline-block;
                margin-bottom: 0.3rem;
            }
            </style>
        """, unsafe_allow_html=True)

        # Project Card
        skills_list = row['Required Skills'].split(
            ',') if isinstance(row['Required Skills'], str) else []

        st.markdown(f"""
            <div class="project-card">
                <div class="project-title">{row['Title']}</div>
                <div class="project-detail"><strong>Idea:</strong> {row['Idea']}</div>
                <div class="project-detail"><strong>Skills needed:</strong></div>
                <div>
                    {''.join([f'<span class="skills-tag">{skill.strip()}</span>' for skill in skills_list])}
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        # Initialize join requests for this project if not exists
        project_title = row['Title']
        if project_title not in st.session_state.join_requests:
            st.session_state.join_requests[project_title] = []

        pending_count = len(st.session_state.join_requests[project_title])

        # Action buttons
        with col2:
            # Show join button if not a member
            if st.session_state.current_user not in st.session_state.join_requests[project_title]:
                if st.button("Join Team", key=f"join_team_{index}"):
                    st.session_state.join_requests[project_title].append(
                        st.session_state.current_user)
                    st.success(f"Sent join request for {project_title}")
                    st.rerun()
            else:
                st.warning("Request pending")

            # Show manage requests button if there are any requests
            if pending_count > 0:
                if st.button(f"Manage Requests ({pending_count})", key=f"manage_requests_{index}"):
                    st.session_state.selected_project = project_title
                    st.session_state.show_requests_modal = True


# Simplified Manage Requests Modal
# if st.session_state.show_requests_modal:
#     st.markdown("""
#         <style>
#         .request-list {
#             margin: 10px 0;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     project = st.session_state.selected_project
#     st.subheader(f"Manage Requests - {project}")

#     requests = st.session_state.join_requests[project]
#     if requests:
#         for idx, requester in enumerate(requests):
#             cols = st.columns([3, 1, 1])
#             with cols[0]:
#                 st.write(f"**{requester}**")
#             with cols[1]:
#                 if st.button("Accept", key=f"accept_{requester}_{idx}"):
#                     st.session_state.join_requests[project].remove(requester)
#                     st.success(f"Accepted {requester}")
#                     st.rerun()
#             with cols[2]:
#                 if st.button("Reject", key=f"reject_{requester}_{idx}"):
#                     st.session_state.join_requests[project].remove(requester)
#                     st.error(f"Rejected {requester}")
#                     st.rerun()
#     else:
#         st.info("No pending requests")

#     if st.button("Close", key="close_modal"):
#         st.session_state.show_requests_modal = False
#         st.rerun()

if st.button('Add Project'):
    st.session_state.show_project_form = not st.session_state.show_project_form

if st.session_state.show_project_form:
    with st.form("project_form"):
        project_title = st.text_input("Project Title")
        project_idea = st.text_area("Project Idea")
        team_members = st.text_input("Team Members (comma-separated)")
        project_skills = st.text_input("Required Skills (comma-separated)")
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Add logic to save project data
            st.success("Project added successfully!")
            st.session_state.show_project_form = False


st.write(
    "Step 1 is collecting people and their LinkedIn resumes, also collecting hackathon sponsors and their description"
)


st.write(
    "Step 2: Once a participan is logged in, they can suggest projects. The LLM will suggest other ideas, and suggest what tools from the sponsors can be used."
)

st.write(
    "Step 3: People can ask to participate in projects, and the project owner can choose who they want in their team based on their skills."
)


# experminenting with Gemini

ggi.configure(api_key=st.secrets["GEMINI_KEY"])
model = ggi.GenerativeModel("gemini-1.5-flash-8b")
chat = model.start_chat()


def LLM_Response(question):
    response = chat.send_message(question, stream=True)
    return response


st.title("Chat Application using Gemini Pro")
user_quest = st.text_input("Ask a question:")
btn = st.button("Ask")
if btn and user_quest:
    result = LLM_Response(user_quest)
    st.subheader("Response : ")
    for word in result:
        st.text(word.text)
