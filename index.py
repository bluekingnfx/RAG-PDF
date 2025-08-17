import typing as tpy
from dotenv import load_dotenv
import streamlit as st
load_dotenv('.env',override=True)

from main_func import UploadClass,ProcessTheQuestion




if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if "processorInstance" not in st.session_state:
    st.session_state.processorInstance = ProcessTheQuestion()
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False

st.title("PDF Query Application")

def processed_state(prompt:str):
    processed = st.session_state.processorInstance.processPrompt(prompt)
    if st.session_state.processorInstance.result == True and processed is not None:
        print(processed)
        st.session_state.chat_history.append((prompt, processed['answer'], [f"- {i.page_content}" for i in processed['source_documents']]))
        st.rerun()
    else:
        st.error(processed.result)

def ChatInterface():
    with st.form('question_form'):
        prompt = st.text_area(label='Ask Your question?',
                            placeholder="What would you like to know about the document?",
                            height=100)
        but = st.form_submit_button(label='✨ Submit')
    if but:
        prompt = prompt.strip()
        with st.spinner():
            processed_state(prompt)


if st.session_state.uploaded == True:
    st.success('Uploaded! Run queries.')
    ChatInterface()
else:
    uploaded_file = st.file_uploader(
        label='Give a pdf',
        help = "Please upload document obtain the info: ",
        type = ['pdf'],
    )
    
    if uploaded_file is not None:
        with st.spinner('In progress'):
            upd = UploadClass(uploaded_file)
            if upd.result == True:
                st.success('File uploaded in vector db')
                st.session_state.uploaded = True
                st.rerun()
            else:
                st.error(f'❌ {upd.result}') #type:ignore

history:tpy.List[tuple[str,str,tpy.List[str]]] = st.session_state.chat_history  # type: ignore

if len(history) > 0:
    for idx, (question, answer,context) in enumerate(reversed(history),1):
        st.subheader('Chat history')
        with st.expander(label=f'{question[:50]} ...'):
            st.markdown("**Question:**")
            st.write(question)
            st.markdown("**Answer:**")
            st.write(answer)
            st.markdown('--')
            st.subheader('Context')
            for point in context:
                st.markdown(point)

with st.sidebar:
    st.markdown('Controls')
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    if st.button("📄 Upload New Document"):
        st.session_state.uploaded  = False
        
        st.success('Upload new document, Previous is saved')
        st.rerun()
    if st.button('📗 Already Uploaded'):
        st.session_state.uploaded = True
        st.success('Ask Pdf ✨')
        st.rerun()


if st.session_state.uploaded == True:
    st.write('The document has been uploaded.')
else:
    st.write('The document has been not uploaded.')