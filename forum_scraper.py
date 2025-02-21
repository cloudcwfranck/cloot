
import requests
from bs4 import BeautifulSoup
import random

def scrape_suggestions():
    suggestions = []
    
    # List of tech forums to scrape
    sources = [
        {
            'url': 'https://www.quora.com/topic/Cloud-Computing',
            'element': 'span',
            'class': 'qu-cursor--pointer',
            'site': 'Quora'
        },
        {
            'url': 'https://stackoverflow.com/questions/tagged/cloud-computing',
            'element': 'h3',
            'class': 's-post-summary--content-title',
            'site': 'StackOverflow'
        }
    ]
    
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Try to scrape from each source
    for source in sources:
        try:
            response = requests.get(source['url'], headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            questions = soup.find_all(source['element'], {'class': source['class']})
            
            for q in questions[:5]:  # Limit to 5 questions per source
                if q.text:
                    text = q.text.strip()
                    suggestions.append({
                        'text': text[:60] + '...' if len(text) > 60 else text,
                        'query': text,
                        'source': source['site']
                    })
        except:
            continue
    
    # If scraping fails or gets too few results, add fallback suggestions
    if len(suggestions) < 5:
        suggestions.extend(fallback)
    
    # Shuffle the suggestions
    random.shuffle(suggestions)
    
    return suggestions[:8]  # Return up to 8 random suggestions
