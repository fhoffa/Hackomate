import streamlit as st
import google.generativeai as ggi

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
st.button('add participant')

st.write(
    "Step 2: Once a participan is logged in, they can suggest projects. The LLM will suggest other ideas, and suggest what tools from the sponsors can be used."
)
st.text_input('suggest a project')

st.write(
    "Step 3: People can ask to participate in projects, and the project owner can choose who they want in their team based on their skills."
)



### experminenting with Gemini

st.secrets["GEMINI_KEY"]
model = ggi.GenerativeModel("gemini-flash") 
chat = model.start_chat()

def LLM_Response(question):
    response = chat.send_message(question,stream=True)
    return response

st.title("Chat Application using Gemini Pro")
user_quest = st.text_input("Ask a question:")
btn = st.button("Ask")
if btn and user_quest:
    result = LLM_Response(user_quest)
    st.subheader("Response : ")
    for word in result:
        st.text(word.text)


