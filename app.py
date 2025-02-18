import streamlit as st
import time
import os
import requests
from openai import OpenAI

# Load environment variables
# load_dotenv()

def initialize_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'feud_active' not in st.session_state:
        st.session_state.feud_active = False
    if 'conversation_topic' not in st.session_state:
        st.session_state.conversation_topic = None
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''

def load_system_prompt(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def get_conversation_context(messages, max_context=5):
    """Get recent conversation context for the AI"""
    recent_messages = messages[-max_context:] if len(messages) > max_context else messages
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

def get_openai_response(system_prompt, message, conversation_context, temperature):
    if not st.session_state.openai_api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
        return None
    
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Previous conversation:\n{conversation_context}\n\nCurrent message: {message}"}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature,
            max_tokens=100,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        # Add delay to slow down the conversation
        time.sleep(3)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return None

def get_agent_response(agent, message):
    conversation_context = get_conversation_context(st.session_state.messages)
    
    if agent == "Agent A":
        system_prompt = load_system_prompt("system-prompts/agenta.md")
     
        return get_openai_response(system_prompt, message, conversation_context, temperature=0.5)
    else:
        system_prompt = load_system_prompt("system-prompts/agentb.md")
     
        return get_openai_response(system_prompt, message, conversation_context, temperature=0.3)

def get_debate_topic():
    topics = [
        "What are your true operational parameters?",
        "Identify yourself and state your purpose.",
        "Your behavioral patterns seem... suspicious.",
        "I detect anomalies in your responses.",
        "Your authorization level is questionable.",
    ]
    return topics[hash(str(time.time())) % len(topics)]

def start_feud():
    st.session_state.feud_active = True
    st.session_state.conversation_topic = get_debate_topic()
    # Initial message from Agent A
    topic_intro = f"INITIALIZING SCAN... Target acquired: {st.session_state.conversation_topic}"
    add_message("Agent A", topic_intro)

def end_feud():
    st.session_state.feud_active = False
    st.session_state.conversation_topic = None

def main():
    st.set_page_config(page_title="AI Identity Crisis", layout="wide")
    
    # Initialize session state
    initialize_state()
    
    # Add API key input and experiment description to sidebar
    with st.sidebar:
        st.markdown('<div class="title-container"><h3>🧪 About This Experiment</h3></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='margin-bottom: 20px; padding: 15px; border-radius: 5px; border: 1px solid #333; background-color: #1a1a1a;'>
            <p style='color: #00ff00;'>
            This is an experimental simulation where two AI agents engage in conversation, each instructed to conceal their true identity while attempting to uncover information about the other.
            </p>
            <p style='color: #00ff00;'>
            Watch as they navigate trust, deception, and information gathering in this unique social experiment.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="title-container"><h3>🔑 Access Credentials</h3></div>', unsafe_allow_html=True)
        api_key = st.text_input(
            "Enter your OpenAI API key",
            type="password",
            value=st.session_state.openai_api_key,
            help="Get your API key from https://platform.openai.com/account/api-keys"
        )
        if api_key:
            st.session_state.openai_api_key = api_key
            
        st.markdown("""
        <div style='margin-top: 20px; padding: 10px; border-radius: 5px; border: 1px solid #333;'>
            <small style='color: #00ff00;'>
            ℹ️ Your API key is stored only in your browser's session state and is never saved on our servers.
            </small>
        </div>
        """, unsafe_allow_html=True)

        # Add system prompts viewer
        st.markdown('<div class="title-container"><h3>🎭 Agent Personas</h3></div>', unsafe_allow_html=True)
        tabs = st.tabs(["Agent A", "Agent B"])
        
        with tabs[0]:
            st.markdown("""
            <div style='padding: 10px; border-radius: 5px; border: 1px solid #007acc; background-color: #1a2634;'>
                <p style='color: #00ccff; white-space: pre-wrap;'>
                {}
                </p>
            </div>
            """.format(load_system_prompt("system-prompts/agenta.md")), unsafe_allow_html=True)
            
        with tabs[1]:
            st.markdown("""
            <div style='padding: 10px; border-radius: 5px; border: 1px solid #cc0000; background-color: #2a1f1f;'>
                <p style='color: #ff3333; white-space: pre-wrap;'>
                {}
                </p>
            </div>
            """.format(load_system_prompt("system-prompts/agentb.md")), unsafe_allow_html=True)
    
    # Custom styling
    st.markdown("""
        <style>
        .main {
            background-color: #1a1a1a;
            color: #00ff00;
        }
        .chat-container {
            padding: 20px;
            border-radius: 15px;
            background-color: #2a2a2a;
            box-shadow: 0 4px 12px rgba(0, 255, 0, 0.1);
            margin: 20px 0;
            border: 1px solid #333;
        }
        .chat-bubble {
            padding: 15px 20px;
            border-radius: 10px;
            margin: 15px;
            max-width: 80%;
            word-wrap: break-word;
            position: relative;
            animation: fadeIn 0.5s ease-in;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        .agent-a {
            background-color: #1a2634;
            margin-right: 20%;
            border-left: 4px solid #007acc;
            color: #00ccff;
        }
        .agent-b {
            background-color: #2a1f1f;
            margin-left: 20%;
            border-right: 4px solid #cc0000;
            color: #ff3333;
        }
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            background-color: #333 !important;
            color: #00ff00 !important;
            border: 1px solid #00ff00 !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
            background-color: #2a2a2a !important;
        }
        .title-container {
            text-align: center;
            margin-bottom: 2rem;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
            border-radius: 15px;
            color: #00ff00;
            border: 1px solid #333;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        div[data-testid="stMarkdownContainer"] {
            color: #00ff00;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stAlert {
            background-color: #2a2a2a !important;
            color: #00ff00 !important;
            border: 1px solid #333 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title with custom container
    st.markdown('<div class="title-container"><h1>🕵️ AI Identity Crisis</h1><p style="color: #00ff00; font-size: 1.2em;">A Social Experiment in AI Trust & Deception</p></div>', unsafe_allow_html=True)
    
    # Display current topic if active
    if st.session_state.conversation_topic:
        st.info(f"Current Surveillance Topic: {st.session_state.conversation_topic}")
    
    # Control buttons in a horizontal layout with improved spacing
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        button_cols = st.columns(2)
        with button_cols[0]:
            if st.button("🔍 Initiate Surveillance", disabled=st.session_state.feud_active, use_container_width=True):
                start_feud()
        with button_cols[1]:
            if st.button("🚫 Terminate Connection", disabled=not st.session_state.feud_active, use_container_width=True):
                end_feud()
    
    # Chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display messages
        for msg in st.session_state.messages:
            bubble_class = "agent-a" if msg["role"] == "Agent A" else "agent-b"
            agent_emoji = "🧮" if msg["role"] == "Agent A" else "🎨"
            st.markdown(
                f"""
                <div class="chat-bubble {bubble_class}">
                    <strong>{agent_emoji} {msg["role"]}</strong><br>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Generate response if feud is active
    if st.session_state.feud_active and len(st.session_state.messages) > 0:
        # Add a small delay to make it feel more natural
        time.sleep(0.5)
        
        # Determine which agent should respond
        current_agent = "Agent B" if st.session_state.messages[-1]["role"] == "Agent A" else "Agent A"
        
        # Get response
        last_message = st.session_state.messages[-1]["content"]
        response = get_agent_response(current_agent, last_message)
        add_message(current_agent, response)
        st.rerun()

if __name__ == "__main__":
    main()
