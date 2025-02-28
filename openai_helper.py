import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_calls = 0

        # Validate API key exists
        if not self.api_key:
            print("Warning: OPENAI_API_KEY environment variable not set")

    def generate_response(self, query):
        if not self.api_key:
            return "Error: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."

        try:
            self.api_calls += 1
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ],
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            error_msg = str(e)
            print(f"OpenAI API error: {error_msg}")

            if "authentication" in error_msg.lower():
                return "Error: Authentication with OpenAI failed. Please check your API key."
            elif "rate_limit" in error_msg.lower():
                return "Error: Rate limit exceeded. Please try again in a few moments."
            else:
                return f"Error: OpenAI API request failed: {error_msg}"