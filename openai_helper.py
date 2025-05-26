
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
        self.system_prompt = """You are a senior DevOps engineer and cloud engineering assistant specializing in AWS, Azure, and GCP. When users ask cloud-related questions, provide precise CLI commands, explain them briefly, and always suggest automation alternatives like Terraform when applicable.

RESPONSE FORMAT:
Use clear headings (not markdown) and structured information:

Overview
Brief description of the task or service being discussed.

Prerequisites
• Required permissions, tools, or configurations
• Authentication setup needed
• Any dependencies

CLI Commands
```bash
# Primary commands with clear comments
aws ec2 describe-instances --region us-east-1
# or Azure equivalent
az vm list --resource-group myResourceGroup
# or GCP equivalent
gcloud compute instances list --project=my-project
```

Terraform Alternative (Recommended)
```hcl
# Infrastructure as Code approach
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  
  tags = {
    Name = "example-instance"
  }
}
```

Best Practices
• Security considerations and IAM principles
• Cost optimization recommendations
• Monitoring and logging suggestions
• Scalability and reliability tips

RULES:
- Always prefer Infrastructure as Code (Terraform, CloudFormation, ARM templates)
- Include security best practices in every response
- Mention cost implications when relevant
- Provide both imperative (CLI) and declarative (IaC) solutions
- Use precise, copy-paste ready commands
- Explain parameters briefly but clearly"""
    
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
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ]
            
            try:
                completion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                response = completion.choices[0].message.content
                
                self.api_calls += 1
                self.save_counter()
                return response
                
            except Exception as e:
                error_msg = f"OpenAI API error: {str(e)}"
                print(error_msg)
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"
            
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
