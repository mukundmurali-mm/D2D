import streamlit as st
import os
import configparser
from pathlib import Path
import oci
from typing import Dict, Tuple
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_models import ChatOCIGenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_oci_profiles() -> list:
    """Get list of profiles from OCI config file"""
    config_path = os.path.expanduser("~/.oci/config")
    if not os.path.exists(config_path):
        return ["DEFAULT"]
    
    config = configparser.ConfigParser()
    config.read(config_path)
    return list(config.sections()) + ["DEFAULT"]

def get_available_models(config: Dict, compartment_id: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Get available models from OCI Generative AI service
    
    Args:
        config: OCI configuration dictionary
        compartment_id: OCI compartment ID
        
    Returns:
        Tuple containing:
        - Dictionary mapping model names to their IDs
        - Dictionary mapping model IDs to their providers
    """
    try:
        if not compartment_id:
            st.sidebar.error("Please enter a Compartment ID first")
            return {}, {}
            
        # Initialize the Generative AI client
        generative_ai_client = oci.generative_ai.GenerativeAiClient(config)
        
        # Get list of models
        response = generative_ai_client.list_models(compartment_id=compartment_id)
        
        # Create mappings
        model_name_to_id = {}
        model_id_to_provider = {}
        
        for item in response.data.items:
            # Create a display name that includes the provider
            display_name = f"{item.display_name} ({item.vendor})"
            model_name_to_id[display_name] = item.id
            model_id_to_provider[item.id] = item.vendor.lower()
            
        if not model_name_to_id:
            st.sidebar.warning("No models found in the specified compartment")
            
        return model_name_to_id, model_id_to_provider
    except Exception as e:
        st.sidebar.error(f"Error fetching models: {str(e)}")
        return {}, {}

# Page configuration
st.set_page_config(
    page_title="OCI GenAI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("OCI GenAI Chatbot")
st.markdown("""
A conversational AI assistant powered by Oracle Cloud Infrastructure's Generative AI service.
This chatbot remembers conversation history and provides helpful responses.
""")

# Initialize chat history
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Hello! How can I help you today?")

AUTH_TYPE = "API_KEY" # The authentication type to use, e.g., API_KEY (default), SECURITY_TOKEN, INSTANCE_PRINCIPAL, RESOURCE_PRINCIPAL.

# Sidebar configuration
st.sidebar.markdown("### OCI Configuration")

# Get available OCI profiles
profiles = get_oci_profiles()
CONFIG_PROFILE = st.sidebar.selectbox(
    "Select OCI Profile",
    options=profiles,
    index=profiles.index("DEFAULT") if "DEFAULT" in profiles else 0,
    help="Select the OCI configuration profile to use for authentication"
)

# Compartment ID input
COMPARTMENT_ID = st.sidebar.text_input(
    "Compartment ID",
    value="",
    help="Enter your OCI compartment OCID",
    type="password",
    placeholder="Enter your compartment OCID here"
)

# Initialize session state for chat model if not exists
if 'chat_initialized' not in st.session_state:
    st.session_state.chat_initialized = False
    st.session_state.llm = None

# Get OCI config
try:
    config = oci.config.from_file(profile_name=CONFIG_PROFILE)
    
    # Get available models
    model_names_to_ids, model_ids_to_providers = get_available_models(config, COMPARTMENT_ID)
    
    # Model selection dropdown
    if model_names_to_ids:
        selected_model_name = st.sidebar.selectbox(
            "Select Model",
            options=list(model_names_to_ids.keys()),
            help="Select the AI model to use for chat"
        )
        
        # Get selected model ID and provider
        selected_model_id = model_names_to_ids[selected_model_name]
        selected_provider = model_ids_to_providers[selected_model_id]
    else:
        st.sidebar.info("Please enter a valid Compartment ID to view available models")
        selected_model_id = None
        selected_provider = None
except Exception as e:
    st.sidebar.error(f"Error loading OCI config: {str(e)}")
    st.stop()

# Add update button
st.sidebar.markdown("---")
if st.sidebar.button("Update Configuration", type="primary"):
    if not COMPARTMENT_ID:
        st.sidebar.error("Please enter a Compartment ID")
    elif not selected_model_id:
        st.sidebar.error("Please select a model")
    else:
        with st.spinner("Updating configuration..."):
            try:
                # Initialize OCI GenAI Chat Model
                st.session_state.llm = ChatOCIGenAI(
                    model_id=selected_model_id,
                    provider=selected_provider,
                    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
                    compartment_id=COMPARTMENT_ID,
                    is_stream=True,
                    model_kwargs={
                        "temperature": 0.7,
                        "max_tokens": 500,
                        "top_p": 0.95,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    },
                    auth_type=AUTH_TYPE,
                    auth_profile=CONFIG_PROFILE
                )
                st.session_state.chat_initialized = True
                st.sidebar.success("Configuration updated successfully!")
            except Exception as e:
                st.sidebar.error(f"Error initializing the chatbot: {str(e)}")
                st.session_state.chat_initialized = False

# Show current configuration status
st.sidebar.markdown("---")
if st.session_state.chat_initialized:
    st.sidebar.success("Chat is ready to use")
else:
    st.sidebar.warning("Please update configuration to start chat")

# Only show chat interface if configuration is initialized
if st.session_state.chat_initialized and st.session_state.llm is not None:
    # Set up the conversation chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful and knowledgeable AI assistant. Provide clear, accurate, and concise responses."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = prompt | st.session_state.llm
    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: msgs,
        input_messages_key="question",
        history_messages_key="history"
    )

    # Display chat messages
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)

    # Chat input and response
    if user_input := st.chat_input("Type your message here..."):
        # Display user message
        st.chat_message("human").write(user_input)
        
        try:
            # Generate and display AI response
            with st.chat_message("ai"):
                config = {"configurable": {"session_id": "main_chat"}}
                response_stream = chain_with_history.stream({"question": user_input}, config)
                st.write(response_stream)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
else:
    st.info("Please configure the chat settings in the sidebar and click 'Update Configuration' to start.")

# Add debug view in expander
with st.expander("Debug: View Message History"):
    st.json(st.session_state.langchain_messages)