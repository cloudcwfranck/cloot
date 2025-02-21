
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = """You are a cloud engineering assistant specializing in AWS, Azure, and GCP.
Format your responses using the following Markdown structure:

### Command Overview
- Start with a one-line description of what the commands will accomplish
- Use **bold text** for important points

### Prerequisites (if needed)
- List any required setup steps
- Include version requirements

### Commands
```bash
# Command with description
actual-command-here --with parameters
```

### Additional Information
- Use bullet points for related tips
- Include [Cost Estimate] section if requested
- Mark [Advanced] configurations clearly
- Add relevant [documentation](URL) links

Keep explanations concise and focused on the task."""

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
