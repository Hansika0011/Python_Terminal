import os
import re
from typing import List, Dict, Any

def validate_path(path: str) -> bool:
    """Validate if a path is safe to use"""
    # Prevent directory traversal attacks
    if '..' in path or path.startswith('/'):
        return False
    return True

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent command injection"""
    # Remove dangerous characters and patterns
    dangerous_patterns = [
        r'[;&|`$()]',  # Command separators and substitution
        r'>\s*[^>\s]',  # Output redirection
        r'<\s*[^<\s]',  # Input redirection
    ]
    
    sanitized = input_str
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_type(file_path: str) -> str:
    """Get file type based on extension"""
    _, ext = os.path.splitext(file_path.lower())
    
    type_mapping = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.txt': 'Text',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.png': 'Image',
        '.jpg': 'Image',
        '.jpeg': 'Image',
        '.gif': 'Image',
        '.pdf': 'PDF',
        '.doc': 'Document',
        '.docx': 'Document',
        '.zip': 'Archive',
        '.tar': 'Archive',
        '.gz': 'Archive',
    }
    
    return type_mapping.get(ext, 'Unknown')

def parse_command_args(command: str) -> List[str]:
    """Parse command string into arguments, handling quotes"""
    import shlex
    try:
        return shlex.split(command)
    except ValueError:
        # Fallback to simple split if shlex fails
        return command.split()