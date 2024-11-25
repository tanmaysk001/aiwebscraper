import streamlit as st
import nest_asyncio
from scrapegraphai.graphs import SmartScraperGraph
import os
os.system("playwright install")


# Apply nest_asyncio to avoid event loop issues with Streamlit
nest_asyncio.apply()

# Streamlit App Title
# Custom title with HTML and CSS for color
st.markdown("<h1 style='color: #4CAF50;'>ScrapeGraphAI Web App</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='color: #4CAF50;'>Complete Insights from any Website</h2>", 
unsafe_allow_html=True)

# Sidebar for API Key Input
with st.sidebar:
    st.header("Enter OpenAI API Key")
    # Initialize session state for the API key
    if "OPENAI_API_KEY" not in st.session_state:
        st.session_state.OPENAI_API_KEY = None

    if not st.session_state.OPENAI_API_KEY:
        api_key = st.text_input("API Key:", type="password", key="api_key_input")
        if st.button("Submit"):
            if api_key.strip():  # Check if the key is non-empty
                st.session_state.OPENAI_API_KEY = api_key.strip()
                st.success("API Key successfully saved! You can now use the app.")
            else:
                st.error("Please enter a valid API key.")
    else:
        st.success("API Key is set!")

# Initialize session state for other variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_processed" not in st.session_state:
    st.session_state.is_processed = False
if "source_url" not in st.session_state:
    st.session_state.source_url = ""

# Step 1: Enter URL and Process it
# st.header("Step 1: Enter URL and Process it")
with st.form("url_form"):
    source_url = st.text_input("Enter a URL:")
    process_button = st.form_submit_button("Process URL")
    
    if process_button:
        if not st.session_state.OPENAI_API_KEY:
            st.warning("Please enter your OpenAI API key in the sidebar before processing a URL.")
        elif source_url:
            try:
                # Create the SmartScraperGraph instance
                smart_scraper_graph = SmartScraperGraph(
                    prompt="Index the data from the URL",
                    source=source_url,
                    config={
                        "llm": {
                            "api_key": st.session_state.OPENAI_API_KEY,  # Use the saved API key
                            "model": "openai/gpt-4o-mini",
                        },
                        "verbose": True,
                        "headless": True,
                    }
                )

                # Run the scraper
                smart_scraper_graph.run()

                # Reset chat history when a new URL is processed
                st.session_state.messages = []  # Clear the chat history
                st.session_state.is_processed = True
                st.session_state.source_url = source_url

                st.success("Success URL Index")
            except Exception as e:
                st.error(f"An error occurred while processing the URL: {e}")
        else:
            st.warning("Please enter a URL.")

# Step 2: Chat Interface for Questions and Answers
if st.session_state.is_processed:
    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about URL:"):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        try:
            smart_scraper_graph = SmartScraperGraph(
                prompt=prompt,
                source=st.session_state.source_url,
                config={
                    "llm": {
                        "api_key": st.session_state.OPENAI_API_KEY,
                        "model": "openai/gpt-4o-mini",
                    },
                    "verbose": True,
                    "headless": True,
                }
            )

            response = smart_scraper_graph.run()

            # Handle response as a dictionary or string
            if isinstance(response, dict):
                # Replace underscores with spaces and format the dictionary
                response_text = "\n".join([f"**{key.replace('_', ' ').capitalize()}:** {value}" 
for key, value in response.items()])
            else:
                response_text = response.strip()

            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)

        except Exception as e:
            with st.chat_message("assistant"):
                error_msg = f"An error occurred: {e}"
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
else:
    st.info("Please process the URL first to start asking questions.")
