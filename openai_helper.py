
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

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

    def generate_response(self, query: str, file_content: str = None) -> str:
        self.api_calls += 1
        self.save_counter()
        
        if not os.getenv('OPENAI_API_KEY'):
            return "Error: OpenAI API key not found. Please add your API key to the Secrets tab."
            
        try:
            # Base system prompt
            system_prompt = """You are a cloud engineering assistant specializing in AWS, Azure, and GCP. 
When analyzing files, first examine the content and then provide insights based on the query.
Format your responses with clear sections:

ANALYSIS (if file provided)
• Brief analysis of the provided file
• Key points and structure identified

RESPONSE
• Direct answer to the query
• Relevant examples or suggestions
• Step-by-step instructions if needed

CODE (if applicable)
```language
code-snippets-here
```

RECOMMENDATIONS
• Best practices
• Potential improvements
• Important considerations"""

            messages = [{"role": "system", "content": system_prompt}]
            
            if file_content:
                # Create a more detailed prompt that includes file analysis
                user_prompt = f"""FILE CONTENT:
{file_content}

USER QUERY:
{query}

Please analyze the file content and provide a response that addresses the query while considering the file's content."""
            else:
                user_prompt = query

            messages.append({"role": "user", "content": user_prompt})
                
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=800  # Increased to accommodate file analysis
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}\nPlease verify your OpenAI API key is valid."
