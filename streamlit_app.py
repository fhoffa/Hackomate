import streamlit as st

st.title("Hackomate")


st.write(
    "Step 1 is collecting people and their LinkedIn resumes, also collecting hackathon sponsors and their description"
)

db_participants = [
    ['Felipe Hoffa', 'https://linkedin.com/in/hoffa', 'Data and Python'],
    ['Asako', 'https://www.linkedin.com/in/asako-hayase-924508ba/', 'Marketing and UX and ...'],
    ['Aninda', 'https://www.linkedin.com/in/aninda-sengupta/', 'Java and Python and  ...'],
    ['Gulsher', 'https://www.linkedin.com/in/gulsher-kooner/', 'Data and Spark and ...'],
]    


st.dataframe(db_participants)


st.write(
    "Step 2: Once a participan is logged in, they can suggest projects. The LLM will suggest other ideas, and suggest what tools from the sponsors can be used."
)

st.write(
    "Step 3: People can ask to participate in projects, and the project owner can choose who they want in their team based on their skills."
)
