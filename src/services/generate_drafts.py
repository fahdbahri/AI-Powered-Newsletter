import os
from dotenv import load_dotenv
from pydantic import HttpUrl, BaseModel, ValidationError
from typing import List
from datetime import datetime
import json
from together import Together

load_dotenv()


# Define the schema
class Story(BaseModel):
    story_or_tweets_link: HttpUrl
    description: str


class DraftPost(BaseModel):
    interesting_stories_or_tweets: List[Story]


async def generate_drafts(raw_stories: str):

    try:

        together = Together()

        print(f"Generating a post draft with raw stories ({len(raw_stories)})")

        current_date = datetime.now().strftime("%m/%d")

        draft_post = DraftPost(interesting_stories_or_tweets=[])
        chat_completion = together.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': """You are given a list of raw AI and LLM-related tweets sourced from X/Twitter.
                Only respond in valid JSON that matches the provided schema(no extra keys).
                """
            },
            {
                'role': 'user',
                'content': f"""Your task is to find interesting trends, launches, or interesting examples from the tweets or stories.
                For each tweet or story, provide a 'story_or_tweet_link' and a one-sentence 'description'.
                Return all relevant tweets or stories as separate objects.
                Aim to pick at least 10 tweets or stories unless there are fewer than 10 available. If there are less than 10 tweets or stories, return ALL of them. Here are the raw tweets or stories you can pick from:\n\n{raw_stories}\n\n
                """
            }
        ],
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        response_format={
            'type': 'json_object',
            'schema': draft_post.schema()
        }
    )

    # Access the response content
        raw_json = chat_completion.choices[0].message.content

        if not raw_json:
            print("No JSON output returned from Together")
            return "No output."

        print(raw_json)

        try:
            parsed_response = json.loads(raw_json)
        except json.JSONDecodeError:
            print("Failed to parse json.")
            return "Invailid JSON output."

        header = f"🚀 AI and LLM Trends on X for {current_date}\n\n"

        # Assuming parsed_response has the same structure as in the JavaScript code

        draft_post = header + "\n\n".join(

            f"• {tweet_or_story['description']}\n  {
                tweet_or_story['story_or_tweets_link']}"

            for tweet_or_story in parsed_response.get('interesting_stories_or_tweets', [])

        )
    except Exception as e:
        print(f"Error in the function generate_draft: {e}")

    return draft_post