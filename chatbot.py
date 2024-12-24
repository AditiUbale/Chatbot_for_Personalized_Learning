import streamlit as st
import google.generativeai as genai
import os
import requests

# Set the page config at the very top of the script
st.set_page_config(page_title="Learning Chatbot", page_icon=":robot:", layout="wide")

# Initialize Gemini API key
def initialize_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("Gemini API key is missing. Please add it to secrets or environment variables.")
            return None
        genai.configure(api_key=api_key)
        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        st.error(f"Failed to initialize Gemini API client: {e}")
        return None

# Function to interact with Gemini LLM (Generative AI)
def chat_with_gemini(model, input_query):
    try:
        # Generate a response using the Gemini model
        response = model.generate_content(input_query)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error during chat response generation: {e}")
        return "I'm sorry, but I'm having trouble processing your request."

# Function to fetch video recommendations from YouTube
def fetch_youtube_videos(query):
    try:
        api_key = st.secrets["YOUTUBE_API_KEY"] if "YOUTUBE_API_KEY" in st.secrets else os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            st.error("YouTube API key is missing. Please add it to secrets or environment variables.")
            return []

        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=5&key={api_key}"
        response = requests.get(url).json()
        videos = [
            {
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            for item in response.get("items", [])
        ]
        return videos
    except Exception as e:
        st.error(f"Failed to fetch YouTube videos: {e}")
        return []

# Function to fetch course recommendations
# (This is a placeholder function, update it with real API integrations)
def fetch_courses(query):
    try:
        # Placeholder for API integration (e.g., Udemy, Coursera, edX, etc.)
        # Here, we return dummy data for demonstration purposes
        courses = [
            {"title": f"Learn {query} on Udemy", "url": "https://www.udemy.com/"},
            {"title": f"{query} Fundamentals on Coursera", "url": "https://www.coursera.org/"},
            {"title": f"{query} Basics on edX", "url": "https://www.edx.org/"},
        ]
        return courses
    except Exception as e:
        st.error(f"Failed to fetch courses: {e}")
        return []

# Streamlit app UI
def main():
    # Sidebar with instructions and API key setup
    st.sidebar.title("Personalized Learning Chatbot")
    st.sidebar.write(
        """
        ### Instructions
        - Type your question or prompt in the input box below.
        - Press Enter or click Submit to send it to the AI.
        - The AI model will generate a response based on your input.
        - Video and course recommendations are provided for additional learning resources.
        """
    )

    # Initialize Gemini model
    model = initialize_gemini()
    if not model:
        return  # Stop app execution if the model fails to initialize

    # Page header with a welcoming message
    st.title("Personalized Learning Chatbot")
    st.write("What would you like to learn today? Ask me anything and I'll do my best to provide an answer.")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history with formatting
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {message['content']}")
        else:
            with st.chat_message("assistant"):
                st.markdown(f"**Assistant:** {message['content']}")

    # Chat input
    prompt = st.text_input("What's on your mind?", key="input", placeholder="Type your message here...")

    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")

        # Generate response from Gemini model
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_gemini(model, prompt)
                st.markdown(f"**Assistant:** {response}")

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Fetch and display video recommendations
        st.subheader("Recommended Videos")
        videos = fetch_youtube_videos(prompt)
        for video in videos:
            st.markdown(f"- [{video['title']}]({video['url']})")

        # Fetch and display course recommendations
        st.subheader("Recommended Courses")
        courses = fetch_courses(prompt)
        for course in courses:
            st.markdown(f"- [{course['title']}]({course['url']})")

    # Footer for the app with credits or information
    st.markdown(
        """
        ---
        Made with ❤️ by [Aditi](https://www.linkedin.com/in/aditinubale) | Powered by Gemini AI
        """
    )

if __name__ == "__main__":
    main()
