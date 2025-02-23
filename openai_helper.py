
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

import json
import os.path

class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.counter_file = 'question_counter.json'
        self.load_counter()
    
    def load_counter(self):
        if os.path.exists(self.counter_file):
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
                self.api_calls = data.get('count', 0)
        else:
            self.api_calls = 0
            self.save_counter()
    
    def save_counter(self):
        with open(self.counter_file, 'w') as f:
            json.dump({'count': self.api_calls}, f)
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
        try:
            self.api_calls += 1
            self.save_counter()
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                print("OpenAI API key not found in environment")
                return "Error: OpenAI API key not found. Please add your API key to the Secrets tab."
                
            if not api_key.startswith('sk-'):
                print("Invalid API key format")
                return "Error: Invalid OpenAI API key format. API key should start with 'sk-'"
                
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
            except Exception as api_error:
                print(f"OpenAI API error: {str(api_error)}")
                return f"Error: OpenAI API request failed: {str(api_error)}"
                
        except Exception as e:
            print(f"General error in generate_response: {str(e)}")
            return f"Error: An unexpected error occurred: {str(e)}"
