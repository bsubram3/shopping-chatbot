import streamlit as st
import prompts
import re
from openai import OpenAI
from model_utils import call_chat_model
import os

#client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

#my_key=''
#client = OpenAI(api_key=my_key)
st.set_page_config(layout="wide")

# Header
title = "XYZ Shopping"
logo_path = "logo1.png"

col1, col2 = st.columns([1, 10])

with col1:
    st.image(logo_path, width=100)

# Display the title in the second column
with col2:
    st.title(title)

# Initialize internal and external chat history
if "internal_messages" not in st.session_state:
    st.session_state.internal_messages = [{
        "role": "system",
        "content": prompts.system_prompt
    }]

if "external_messages" not in st.session_state:
    st.session_state.external_messages = []

# Initialize trackers
if "support_ticket_tracker" not in st.session_state:
    st.session_state.support_ticket_tracker = ""


# Function to extract tracker tags from response
def parse_messages(text):
    message_pattern = r"<message>(.*?)</message>"
    support_ticket_pattern = r"<support_ticket_details>(.*?)</support_ticket_details>"

    message = re.findall(message_pattern, text, re.DOTALL)
    support_ticket = re.findall(support_ticket_pattern, text, re.DOTALL)

    return message[0] if message else "", support_ticket[0] if support_ticket else ""


# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Chat with Support Agent")

    # Create a container for chat messages
    chat_container = st.container(height=400)

    # Create a container for the input box
    input_container = st.container()

    # Display chat messages from history on app rerun
    with chat_container:
        for message in st.session_state.external_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input
    with input_container:
        #upload_col1, upload_col2 = st.columns([4, 1])

        if prompt := st.chat_input("Enter text..."):
            # Add user message to chat history
            st.session_state.internal_messages.append({
                "role": "user",
                "content": prompt
            })
            st.session_state.external_messages.append({
                "role": "user",
                "content": prompt
            })

            with chat_container:
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(prompt)

            # with chat_container:
                with st.chat_message("assistant"):
                    messages = [{
                        "role": m["role"],
                        "content": m["content"]
                    } for m in st.session_state.internal_messages]

                    # call the chat model to generate a completion
                    completion = call_chat_model(client, messages)

                    response = completion.choices[0].message.content

                    print('***RAW OUTPUTS***')
                    print(response)

                    # add raw message to internal messages
                    st.session_state.internal_messages.append({
                        "role":
                        "assistant",
                        "content":
                        response
                    })

                    message, support_ticket_tracker = parse_messages(
                        response)

                    # add parsed message to external messages
                    st.session_state.external_messages.append({
                        "role":
                        "assistant",
                        "content":
                        message
                    })

                    # Update session state trackers
                    if support_ticket_tracker:
                        st.session_state.support_ticket_tracker = support_ticket_tracker
                    st.rerun()

with col2:
    st.header("Support Ticket Details")
    ticket_log_container = st.container(height=260)
    with ticket_log_container:
        if len(st.session_state.support_ticket_tracker) > 0:
            print(st.session_state.support_ticket_tracker)
            st.write(st.session_state.support_ticket_tracker)
