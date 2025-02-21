
import requests
from bs4 import BeautifulSoup
import random

def scrape_suggestions():
    suggestions = []
    
    # Quora topics related to cloud computing
    try:
        quora_url = "https://www.quora.com/topic/Cloud-Computing"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(quora_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        questions = soup.find_all('span', {'class': 'qu-cursor--pointer'})
        
        for q in questions[:10]:
            if q.text:
                suggestions.append({
                    'text': q.text[:60] + '...' if len(q.text) > 60 else q.text,
                    'query': q.text,
                    'source': 'Quora'
                })
    except:
        # Fallback suggestions if scraping fails
        fallback = [
            { 'text': 'AWS Lambda vs Azure Functions', 'query': 'Compare AWS Lambda and Azure Functions', 'source': 'Cloud Computing' },
            { 'text': 'Kubernetes vs Docker Swarm', 'query': 'Kubernetes vs Docker Swarm comparison', 'source': 'Container Orchestration' },
            { 'text': 'Multi-Cloud Strategy', 'query': 'How to implement multi-cloud strategy?', 'source': 'Cloud Architecture' },
            { 'text': 'Serverless Architecture', 'query': 'Best practices for serverless architecture', 'source': 'Cloud Design' },
            { 'text': 'Cloud Security Best Practices', 'query': 'Cloud security best practices and implementations', 'source': 'Security' },
            { 'text': 'Cost Optimization in Cloud', 'query': 'How to optimize cloud costs?', 'source': 'Cloud Management' },
            { 'text': 'DevOps in Cloud', 'query': 'Implementing DevOps in cloud environment', 'source': 'DevOps' },
            { 'text': 'Microservices Architecture', 'query': 'Design patterns for microservices', 'source': 'Architecture' }
        ]
        suggestions.extend(fallback)
    
    return suggestions
