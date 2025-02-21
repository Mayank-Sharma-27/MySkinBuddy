import re
from typing import Dict, Optional, Tuple, Union, Generator, List
from enum import Enum

class MessageType(Enum):
    CHUNK = "assistant_chunk"
    CITATION = "citations"
    DONE = "done"
    ERROR = "error"

class ResponseFormatter:
    @staticmethod
    def chunk_content(content: str, in_think_section: bool = False) -> Tuple[List[str], bool]:
        """
        Split content into meaningful chunks using regex patterns.
        Returns a tuple of (chunks list, updated think section state).
        """
        # Check and update think section state
        if '<think>' in content:
            return [], True
        elif '</think>' in content:
            return [], False
        elif in_think_section:
            return [], True
            
        # Define regex patterns for splitting
        patterns = [
            r'(?<=\.\s)',      # After periods with space
            r'(?<=\?\s)',      # After question marks with space
            r'(?<=!\s)',       # After exclamation marks with space
            r'(?<=\n)',        # After newlines
            r'(?<=:\s)',       # After colons with space
            r'(?<=\*\*\s)',    # After bold markers with space
            r'(?<=\*\s)',      # After italic marker with space
            r'(?<=\*)',        # After italic marker
            r'(?<=# )',        # After h1 marker
            r'(?<=## )',       # After h2 marker
            r'(?<=### )',      # After h3 marker
            r'(?<=#### )',     # After h4 marker
            r'(?<=##### )',    # After h5 marker
            r'(?<=•\s)',       # After bullet points
        ]
        
        # Combine all patterns
        split_pattern = '|'.join(patterns)
        
        # Split the content while preserving the delimiters
        chunks = re.split(f'({split_pattern})', content)
        
        # Combine chunks meaningfully
        result = []
        current_chunk = ''
        
        for chunk in chunks:
            current_chunk += chunk
            # Check if chunk ends with newline or is a complete heading
            if (
                len(current_chunk.strip()) >= 3 and 
                (re.search(split_pattern, current_chunk) or 
                 re.search(r'#+ .*\n', current_chunk))
            ):
                if current_chunk.strip():
                    result.append(current_chunk)
                current_chunk = ''
                
        # Add any remaining content
        if current_chunk.strip():
            result.append(current_chunk)
            
        return result

    @staticmethod
    def format_chunk(content: str) -> Dict:
        """
        Format a single chunk of content.
        Now supports both direct content and chunked content.
        """
        
        chunks = ResponseFormatter.chunk_content(content)
        if len(chunks) <= 5:
            # Join filtered chunks instead of using original content
            filtered_content = ''.join(chunks)
            return {
                "type": MessageType.CHUNK.value,
                "content": filtered_content
            }
        
        # Return first chunk, queue others for next iterations
        return {
            "type": MessageType.CHUNK.value,
            "content": chunks[0],
            "remaining_chunks": chunks[1:]
        }
    
    @staticmethod
    def format_citation(content: str) -> Dict:
        return {
            "type": MessageType.CITATION.value,
            "content": content
        }
    
    @staticmethod
    def format_done() -> Dict:
        return {"type": MessageType.DONE.value}
    
    @staticmethod
    def format_error(error: str) -> Dict:
        return {
            "type": MessageType.ERROR.value,
            "content": str(error)
        }

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
        content += ""
        
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