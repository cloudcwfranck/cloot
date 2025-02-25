
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import os.path
from openai import OpenAIError

load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class OpenAIHelper:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not api_key.startswith('sk-'):
            raise ValueError("Invalid OPENAI_API_KEY format")
        self.client = OpenAI(api_key=api_key)
        self.counter_file = 'question_counter.json'
        self.load_counter()
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

    def generate_response(self, query: str) -> str:
        try:
            print("Starting generate_response")
            print(f"Query received: {query}")
            
            try:
                self.api_calls += 1
                self.save_counter()
            except Exception as counter_error:
                print(f"Counter error (non-fatal): {str(counter_error)}")
            
            api_key = os.getenv('OPENAI_API_KEY')
            print(f"API key present and valid format: {bool(api_key and api_key.startswith('sk-'))}")
            
            if not api_key:
                print("OpenAI API key not found in environment")
                return "Error: OpenAI API key not found. Please add your API key to the Secrets tab."
                
            if not api_key.startswith('sk-'):
                print("Invalid API key format")
                return "Error: Invalid OpenAI API key format. API key should start with 'sk-'"
                
            try:
                print(f"Making API call with key starting with: {api_key[:5]}...")
                print("Creating chat completion with query:", query)
                
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ]
                
                print("Sending request to OpenAI...")
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                print("Response object:", response)
                
                print("Response received from OpenAI")
                if hasattr(response.choices[0].message, 'content'):
                    return response.choices[0].message.content
                    
                return "Error: Could not extract response content"
                
            except Exception as api_error:
                error_msg = str(api_error)
                print(f"OpenAI API error details: {error_msg}")
                if "invalid_api_key" in error_msg.lower():
                    return "Error: Invalid API key. Please check your OpenAI API key in the Secrets tab."
                elif "rate_limit" in error_msg.lower():
                    return "Error: Rate limit exceeded. Please try again in a few moments."
                else:
                    return f"Error: OpenAI API request failed: {error_msg}"
                
        except Exception as e:
            print(f"General error in generate_response: {str(e)}")
            return f"Error: An unexpected error occurred: {str(e)}"
