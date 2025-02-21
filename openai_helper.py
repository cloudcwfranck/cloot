
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = """You are a cloud engineering assistant specializing in AWS, Azure, and GCP.
Format your responses exactly like this:

<b>Overview</b>
Brief description of the task or service.

<b>Key Requirements</b>
• List key prerequisites and requirements

<b>Implementation Steps</b>
• Step-by-step implementation details
• Use bullet points for clarity

<b>Commands</b>
```bash
command-here --with-parameters
additional-command --with-options
```

<b>Additional Notes</b>
• Important considerations
• Best practices
• Cost implications when relevant"""

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
