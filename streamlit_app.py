import streamlit as st
from sqlalchemy import text

conn = st.connection("neon", type="sql")

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


st.header("Sponsors")

sponsors_df = conn.query('SELECT name,features FROM sponsors;', ttl="1m")
sponsors_df = sponsors_df.rename(columns={
    'name': 'Sponsor Name',
    # 'url': 'Website URL',
    'features': 'Features'
})

st.dataframe(sponsors_df)

if st.button('Add Sponsor',  key="add_sponsors_button"):
    st.session_state.show_sponsor_form = not st.session_state.show_sponsor_form

if st.session_state.show_sponsor_form:
    with st.form("sponsor_form"):
        sponsor_name = st.text_input("Sponsor Name")
        # website_url = st.text_input("Website URL")
        features = st.text_area("Features")
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                with conn.session as s:
                    # Create sequence and insert without assuming column name
                    s.execute(
                        text("""
                            INSERT INTO sponsors (name, features) 
                            VALUES (:name, :features);
                        """),
                        params={
                            'name': sponsor_name,
                            'features': features
                        }
                    )
                    s.commit()
                st.success("Sponsor added successfully!")
                st.session_state.show_sponsor_form = False
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding sponsor: {str(e)}")
                s.rollback()


st.header("Participants")

participants_df = conn.query(
    'SELECT name, url, interested_in, skills FROM participants;', ttl="1m")

participants_df = participants_df.rename(columns={
    'name': 'Name',
    'url': 'LinkedIn URL',
    'interested_in': 'Interests',
    'skills': 'Skills'
})

st.dataframe(participants_df)

if st.button('Add Participant', key="add_participant_button"):
    st.session_state.show_participant_form = not st.session_state.show_participant_form

if st.session_state.show_participant_form:
    with st.form("participant_form"):
        participant_name = st.text_input("Participant Name")
        linkedin_url = st.text_input("LinkedIn URL")
        skills = st.text_input("Skills (comma-separated)")
        interested_in = st.text_area("Interested in")
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                with conn.session as s:
                    # Ensure sequence exists and is synchronized
                    s.execute(text("""
                        CREATE SEQUENCE IF NOT EXISTS participants_id_seq;
                        SELECT setval('participants_id_seq', COALESCE((SELECT MAX(prt_id) FROM participants), 0));
                    """))

                    s.execute(
                        text("""
                            INSERT INTO participants (prt_id, name, url, skills, interested_in) 
                            VALUES (nextval('participants_id_seq'), :name, :url, :skills, :interested_in);
                        """),
                        params={
                            'name': participant_name,
                            'url': linkedin_url,
                            'skills': skills,
                            'interested_in': interested_in
                        }
                    )
                    s.commit()
                st.success("Participant added successfully!")
                st.session_state.show_participant_form = False
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding participant: {str(e)}")
                s.rollback()

# Projects Data

st.header("Project Ideas")

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


def execute_query(query):
    conn.query(query, ttl=0)
    conn.query("SELECT 1;", ttl=0)  # Force cache clearing


# Get projects with team members using JOIN
project_df = conn.query('''
    SELECT
        i.idea_id,
        i.title,
        i.idea,
        i.skills_needed,
        STRING_AGG(
            CASE
                WHEN t.approved = true THEN p.name
                ELSE NULL
            END,
            ', '
        ) as team_members,
        COUNT(CASE WHEN t.approved IS NULL AND t.team_id IS NOT NULL THEN 1 END) as pending_requests
    FROM ideas i
    LEFT JOIN team t ON i.idea_id = t.idea_id
    LEFT JOIN participants p ON t.prt_id = p.prt_id
    GROUP BY i.idea_id, i.title, i.idea, i.skills_needed;
''', ttl="1m")

# Display projects with cards
for index, row in project_df.iterrows():
    with st.container():
        # Project Card
        skills_list = row['skills_needed'].split(
            ',') if isinstance(row['skills_needed'], str) else []
        team_members = row['team_members'].split(
            ', ') if row['team_members'] else []

        st.markdown(f"""
            <div class="project-card">
                <div class="project-title">{row['title']}</div>
                <div class="project-detail"><strong>Idea:</strong> {row['idea']}</div>
                <div class="project-detail"><strong>Skills needed:</strong></div>
                <div>
                    {''.join(
                        [f'<span class="skills-tag">{skill.strip()}</span>' for skill in skills_list])}
                </div>
                <div class="project-detail">
                    <strong>Current Team Members:</strong><br/>
                    {', '.join(team_members)
                               if team_members else "No team members yet"}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Action buttons column
        col1, col2 = st.columns([3, 1])

        with col2:
            # Show join button if not already a member
            if st.session_state.current_user not in team_members:
                # Check if already requested
                already_requested = conn.query(f'''
                    SELECT COUNT(*) as count
                    FROM team t
                    JOIN participants p ON t.prt_id = p.prt_id
                    JOIN ideas i ON t.idea_id = i.idea_id
                    WHERE i.title = '{row['title']}'
                    AND p.name = '{st.session_state.current_user}'
                    AND t.approved IS NULL;
                ''', ttl="1m").iloc[0]['count'] > 0

                if already_requested:
                    st.warning("Request pending")
                else:
                    if st.button("Join Team", key=f"join_team_{index}"):
                        try:
                            execute_query(f'''
                                INSERT INTO team (idea_id, prt_id, approved)
                                SELECT i.idea_id, p.prt_id, NULL
                                FROM ideas i, participants p
                                WHERE i.title = '{row['title']}'
                                AND p.name = '{st.session_state.current_user}';
                            ''')
                            st.success(f"Sent join request for {row['title']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error sending request: {str(e)}")

            # Show pending requests count and manage button
            pending_count = row['pending_requests']
            if pending_count > 0:
                if st.button(f"Manage Requests ({pending_count})", key=f"manage_requests_{index}"):
                    st.session_state.selected_project = row['title']
                    st.session_state.show_requests_modal = True

# Requests Management Modal
if st.session_state.show_requests_modal:
    project = st.session_state.selected_project
    st.subheader(f"Manage Requests - {project}")

    # Get pending requests
    pending_requests = conn.query(f'''
        SELECT
            p.name,
            p.skills,
            t.team_id
        FROM team t
        JOIN ideas i ON t.idea_id = i.idea_id
        JOIN participants p ON t.prt_id = p.prt_id
        WHERE i.title = '{project}'
        AND t.approved IS NULL;
    ''', ttl="1m")

    if not pending_requests.empty:
        for idx, request in pending_requests.iterrows():
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"**{request['name']}**")
                st.write(f"Skills: {request['skills']}")
            with cols[1]:
                if st.button("Accept", key=f"accept_{idx}"):
                    try:
                        execute_query(f"""
                            UPDATE team
                            SET approved = true
                            WHERE team_id = {request['team_id']};
                        """)
                        st.success(f"Accepted {request['name']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error accepting request: {str(e)}")
            with cols[2]:
                if st.button("Reject", key=f"reject_{idx}"):
                    try:
                        execute_query(f"""
                            DELETE FROM team
                            WHERE team_id = {request['team_id']};
                        """)
                        st.error(f"Rejected {request['name']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error rejecting request: {str(e)}")
    else:
        st.info("No pending requests")

    if st.button("Close", key="close_modal"):
        st.session_state.show_requests_modal = False
        st.rerun()

# Add Project Form
if st.button('Add Project', key="add_project_button"):
    st.session_state.show_project_form = not st.session_state.show_project_form

if st.session_state.show_project_form:
    with st.form("project_form"):
        project_title = st.text_input("Project Title")
        project_idea = st.text_area("Project Idea")
        required_skills = st.text_input("Required Skills (comma-separated)")
        submitted = st.form_submit_button("Submit")

        if submitted:
            try:
                with conn.session as s:
                    # First ensure we have a sequence
                    s.execute(text("""
                        CREATE SEQUENCE IF NOT EXISTS ideas_id_seq;
                    """))

                    # Reset the sequence to start after the highest existing id
                    s.execute(text("""
                        SELECT setval('ideas_id_seq', COALESCE((SELECT MAX(idea_id) FROM ideas), 0));
                    """))

                    # Now insert the new record
                    s.execute(
                        text("""
                            INSERT INTO ideas (idea_id, title, idea, skills_needed) 
                            VALUES (nextval('ideas_id_seq'), :title, :idea, :skills_needed);
                        """),
                        params={
                            'title': project_title,
                            'idea': project_idea,
                            'skills_needed': required_skills
                        }
                    )
                    s.commit()
                st.success("Project added successfully!")
                st.session_state.show_project_form = False
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding project: {str(e)}")
                s.rollback()
