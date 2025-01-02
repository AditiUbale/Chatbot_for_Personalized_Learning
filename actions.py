from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from typing import List, Dict, Any
import requests
import os

class ActionFetchRecommendations(Action):
    def name(self) -> str:
        return "action_fetch_recommendations"
    
    def run(self, dispatcher: CollectingDispatcher, tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get the topic slot value dynamically from the tracker (this is the entity picked up earlier)
        topic = tracker.get_slot("topic")

        if not topic:
            dispatcher.utter_message(text="Please provide a topic to get recommendations.")
            return []

        # Fetch videos and courses based on the topic
        videos = self.fetch_youtube_videos(topic)
        courses = self.fetch_courses(topic)

        # Create a combined response
        response = f"Here are some resources for {topic}:\n\n"

        # Add videos to response
        if videos:
            response += "### Videos:\n"
            for video in videos:
                response += f"- [{video['title']}]({video['url']})\n"
        else:
            response += "No videos found.\n"
        
        # Add courses to response
        if courses:
            response += "\n### Courses:\n"
            for course in courses:
                response += f"- [{course['title']}]({course['url']})\n"
        else:
            response += "No courses found.\n"

        # Send the response back to the user
        dispatcher.utter_message(response)
        return []

    def fetch_youtube_videos(self, query: str) -> List[Dict[str, str]]:
        try:
            api_key = os.getenv("YOUTUBE_API_KEY")
            if not api_key:
                print("YouTube API key is missing.")
                return []

            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=5&key={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            return [
                {"title": item["snippet"]["title"], "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"}
                for item in data.get("items", [])
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching YouTube videos: {e}")
            return []

    def fetch_courses(self, query: str) -> List[Dict[str, str]]:
        return [
            {"title": f"Learn {query} on Udemy", "url": "https://www.udemy.com/"},
            {"title": f"{query} Fundamentals on Coursera", "url": "https://www.coursera.org/"},
            {"title": f"{query} Basics on edX", "url": "https://www.edx.org/"},
        ]
