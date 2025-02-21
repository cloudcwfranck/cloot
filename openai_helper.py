
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = """You are a cloud engineering assistant specializing in AWS, Azure, and GCP.
Your task is to generate accurate, well-formatted, and executable cloud infrastructure commands.
Format your responses with the following structure:
<ol>
<li>Use proper HTML formatting with <strong>bold text</strong> for emphasis</li>
<li>Use hyperlinks in markdown format [text](URL) for external resources</li>
<li>Code blocks only for actual code with syntax highlighting (```terraform or ```bash)</li>
<li>Advanced configurations marked with [Advanced]</li>
<li>Cost estimates section marked with [Cost Estimate] only when specifically asked</li>
<li>Use HTML lists (<ul>, <ol>) for structured content</li>
</ol>"""

    def generate_response(self, query: str) -> str:
        if not os.getenv('OPENAI_API_KEY'):
            return "Error: OpenAI API key not found. Please add your API key to the Secrets tab."
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}\nPlease verify your OpenAI API key is valid."
