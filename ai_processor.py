import re
import os
from typing import Dict, Any

class AIProcessor:
    """Process natural language queries and convert to terminal commands"""
    
    def __init__(self):
        self.command_patterns = {
            r'create (?:a )?(?:new )?(?:folder|directory) (?:called |named )?([^\s]+)': 'mkdir {}',
            r'make (?:a )?(?:new )?(?:folder|directory) (?:called |named )?([^\s]+)': 'mkdir {}',
            r'create (?:a )?(?:new )?file (?:called |named )?([^\s]+)': 'touch {}',
            r'remove (?:the )?(?:file|folder|directory) ([^\s]+)': 'rm {}',
            r'delete (?:the )?(?:file|folder|directory) ([^\s]+)': 'rm {}',
            r'(?:list|show) (?:all )?(?:the )?files?(?: in ([^\s]+))?': 'ls {}',
            r'show me (?:all )?(?:the )?(?:files?|contents?)(?: (?:in|of) ([^\s]+))?': 'ls {}',
            r'find (?:all )?(?:files? )?(?:called |named )?([^\s]+)': 'find {}',
            r'(?:show|display|read) (?:the )?(?:contents? of )?(?:file )?([^\s]+)': 'cat {}',
            r'what(?:\'s| is) the current (?:directory|folder)': 'pwd',
            r'where am i': 'pwd',
            r'who am i': 'whoami',
            r'go to (?:the )?(?:directory|folder) ([^\s]+)': 'cd {}',
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return command or response"""
        query = query.strip().lower()
        
        # Try to match command patterns
        for pattern, command_template in self.command_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                groups = match.groups()
                args = [arg for arg in groups if arg]
                
                try:
                    if '{}' in command_template:
                        if len(args) == 0:
                            command = command_template.replace(' {}', '')
                        else:
                            command = command_template.format(*args)
                    else:
                        command = command_template
                    
                    return {
                        'requires_execution': True,
                        'command': command,
                        'explanation': f'Interpreting "{query}" as: {command}'
                    }
                except (IndexError, KeyError):
                    command = command_template.split()[0]
                    return {
                        'requires_execution': True,
                        'command': command,
                        'explanation': f'Interpreting "{query}" as: {command}'
                    }
        
        # File extension queries
        if 'python files' in query or '.py files' in query:
            return {
                'requires_execution': True,
                'command': 'find *.py',
                'explanation': 'Searching for Python files'
            }
        
        # Default response
        return {
            'requires_execution': False,
            'explanation': f'I couldn\'t understand "{query}". Try using specific commands like "ls", "mkdir test", or "show me all files".'
        }