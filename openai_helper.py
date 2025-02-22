import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = """You are a cloud engineering assistant specializing in AWS, Azure, and GCP.
Format your responses with clear headings (not using markdown) and clean bullet points like this:

Overview
A clear, single-paragraph description of the topic or service.

Key Requirements
• List key prerequisites and requirements
• Each point should be clear and concise

How It Works
• Detailed explanation points
• Step-by-step process details
• Each point should be self-contained

Commands
```bash
command-here --with-parameters
additional-commands --if-needed
```

Additional Notes
• Important considerations to keep in mind
• Best practices and recommendations
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