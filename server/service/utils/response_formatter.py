import re
from typing import Dict, Optional, Tuple

def format_agent_response(response) -> Dict:
    """
    Format the agent response by:
    1. Removing the <think> section
    2. Formatting citations
    3. Structuring the response for frontend consumption
    
    Args:
        response: The raw response from the model
        
    Returns:
        Dict containing formatted content and metadata
    """
    content = response.content
    print("Printing response")
    citations = response.additional_kwargs.get('citations', [])
    
    # Remove think section
    content = remove_think_section(content)
    
    # Format citations in content
    content = format_citations(content, citations)
    
    return {
        "content": content.strip(),
        "metadata": {
            "citations": citations
        }
    }

def remove_think_section(content: str) -> str:
    """Remove the <think> section from the content"""
    think_pattern = r'<think>.*?</think>\n*'
    return re.sub(think_pattern, '', content, flags=re.DOTALL)

def format_citations(content: str, citations: list) -> str:
    """
    Format citations by adding them as a separate section at the end of the content
    with proper formatting and numbering.
    """
    if not citations:
        return content
        
    # Remove any existing citation numbers from the content
    content = re.sub(r'\[(\d+)\]', '', content)
    
    # Add citations section at the end
    if citations:
        content = content.strip()
        content += "\n\n---\n\nTo learn more, you can refer to these sources:\n"
        
        for i, url in enumerate(citations, 1):
            # Extract domain name for better readability
            domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain:
                site_name = domain.group(1).replace('.com', '').replace('.org', '')
                site_name = ' '.join(word.capitalize() for word in site_name.split('.'))
                content += f"\n{i}. {site_name} - [Read more]({url})"
            else:
                content += f"\n{i}. [Source {i}]({url})"
    
    return content 