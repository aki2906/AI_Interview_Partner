import streamlit as st
import api_client
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="AI Interview Partner", layout="centered")

st.markdown("""
<style>
    .chat-msg { padding: 10px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'messages' not in st.session_state: st.session_state.messages = []
if 'session_id' not in st.session_state: st.session_state.session_id = None

# --- SHARED RESPONSE HANDLER ---
def handle_response(res):
    if "error" in res:
        st.error(f"Error: {res['error']}")
    else:
        st.session_state.messages.append({"role": "user", "content": res['transcription']})
        eval_text = f"**Score:** {res['score']}/10\n\n**Feedback:** {res['feedback']}"
        st.session_state.messages.append({"role": "system_eval", "content": eval_text})
        
        if res['is_interview_over']:
            st.session_state.page = 'report'
        elif res['next_question']:
            st.session_state.messages.append({"role": "assistant", "content": res['next_question']})
        st.rerun()

# LANDING
if st.session_state.page == 'landing':
    st.title("🎙️ AI Interview Partner")
    st.caption("Powered by Gemini 2.5 Flash")
    
    with st.form("start_form"):
        domain = st.selectbox("Topic", ["Python", "Java", "SQL", "System Design", "HR"])
        difficulty = st.select_slider("Difficulty", ["Junior", "Mid-Level", "Senior"])
        submitted = st.form_submit_button("Start Interview")
        
        if submitted:
            with st.spinner("Preparing interview..."):
                res = api_client.start_interview_session(domain, difficulty)
                if "error" in res:
                    st.error(f"Backend Error: {res['error']}")
                else:
                    st.session_state.session_id = res['session_id']
                    st.session_state.messages = [{"role": "assistant", "content": res['first_question']}]
                    st.session_state.page = 'interview'
                    st.rerun()

# INTERVIEW
elif st.session_state.page == 'interview':
    st.title("💬 Interview Session")
    
    for msg in st.session_state.messages:
        role = msg['role']
        if role == 'assistant':
            with st.chat_message("assistant"): st.write(msg['content'])
        elif role == 'user':
            with st.chat_message("user"): st.write(msg['content'])
        elif role == 'system_eval':
            st.info(msg['content'])

    st.write("---")
    
    tab1, tab2 = st.tabs(["🎤 Voice Recorder", "⌨️ Type Answer"])
    
    with tab1:
        st.write("Click Start, Speak, Click Stop.")
        dynamic_key = f"recorder_{len(st.session_state.messages)}"
        
        audio = mic_recorder(
            start_prompt="🔴 Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=False,
            use_container_width=True,
            format="wav", 
            key=dynamic_key
        )
        if audio:
            st.success("Audio Captured!")
            if st.button("Submit Audio Answer"):
                with st.spinner("Analyzing Audio..."):
                    res = api_client.submit_audio_response(st.session_state.session_id, audio['bytes'])
                    handle_response(res)

    with tab2:
        # REAL TEXT SUBMISSION LOGIC
        text_input = st.text_area("Type your answer here:")
        if st.button("Submit Text Answer"):
            if text_input.strip():
                with st.spinner("Analyzing Text..."):
                    res = api_client.submit_text_response(st.session_state.session_id, text_input)
                    handle_response(res)
            else:
                st.warning("Please type an answer first.")

# REPORT
elif st.session_state.page == 'report':
    st.title("📊 Performance Report")
    
    with st.spinner("Generating Final Summary..."):
        report = api_client.get_final_report(st.session_state.session_id)
    
    st.metric("Final Average Score", f"{report.get('total_score', 0):.1f} / 10")
    st.markdown("### Executive Summary")
    st.write(report.get('summary', 'No summary generated.'))
    
    if st.button("Start New Interview"):
        st.session_state.clear()
        st.rerun()
