class Terminal {
    constructor() {
        this.input = document.getElementById('command-input');
        this.output = document.getElementById('terminal-output');
        this.status = document.getElementById('status-text');
        this.currentDir = document.getElementById('current-directory');
        this.suggestions = document.getElementById('suggestions');
        
        this.commandHistory = [];
        this.historyIndex = -1;
        
        this.init();
    }
    
    init() {
        this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
        this.input.addEventListener('input', this.handleInput.bind(this));
        
        // Update system info periodically
        this.updateSystemInfo();
        setInterval(() => this.updateSystemInfo(), 5000);
    }
    
    handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.executeCommand();
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            this.navigateHistory(-1);
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            this.navigateHistory(1);
        } else if (event.key === 'Tab') {
            event.preventDefault();
            this.handleTabCompletion();
        }
    }
    
    handleInput(event) {
        this.showSuggestions(event.target.value);
    }
    
    async executeCommand() {
        const command = this.input.value.trim();
        if (!command) return;
        
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;
        
        this.appendOutput(`user@python-terminal:~$ ${command}`, 'command');
        this.status.textContent = 'Executing...';
        
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.appendOutput(result.output, result.type);
            } else {
                this.appendOutput(result.output, 'error');
            }
        } catch (error) {
            this.appendOutput(`Error: ${error.message}`, 'error');
        }
        
        this.status.textContent = 'Ready';
        this.input.value = '';
        this.hideSuggestions();
    }
    
    appendOutput(text, type = 'normal') {
        const outputLine = document.createElement('div');
        outputLine.className = `command-output output-${type}`;
        outputLine.textContent = text;
        this.output.appendChild(outputLine);
        
        this.output.scrollTop = this.output.scrollHeight;
    }
    
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;
        
        this.historyIndex = Math.max(-1, 
            Math.min(this.commandHistory.length - 1, this.historyIndex + direction));
        
        if (this.historyIndex >= 0) {
            this.input.value = this.commandHistory[this.historyIndex];
        } else {
            this.input.value = '';
        }
    }
    
    showSuggestions(input) {
        if (input.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        const commonCommands = [
            'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv', 'cat', 'grep',
            'python', 'pip install', 'git status', 'git add', 'git commit',
            'create a folder', 'show me files', 'list all files', 'find files'
        ];
        
        const matches = commonCommands.filter(cmd => 
            cmd.toLowerCase().includes(input.toLowerCase())
        );
        
        if (matches.length > 0) {
            this.suggestions.innerHTML = matches
                .slice(0, 5)
                .map(cmd => `<span style="margin-right: 15px; cursor: pointer;" data-command="${cmd}">${cmd}</span>`)
                .join('');
            
            this.suggestions.style.display = 'block';
            
            this.suggestions.querySelectorAll('[data-command]').forEach(item => {
                item.addEventListener('click', () => {
                    this.input.value = item.dataset.command;
                    this.hideSuggestions();
                    this.input.focus();
                });
            });
        } else {
            this.hideSuggestions();
        }
    }
    
    hideSuggestions() {
        this.suggestions.style.display = 'none';
    }
    
    handleTabCompletion() {
        const input = this.input.value;
        const commonCommands = ['ls', 'cd', 'pwd', 'python', 'pip', 'git'];
        
        const matches = commonCommands.filter(cmd => cmd.startsWith(input));
        if (matches.length === 1) {
            this.input.value = matches[0] + ' ';
        }
    }
    
    async updateSystemInfo() {
        try {
            const response = await fetch('/system_info');
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('cpu-usage').textContent = 
                    `CPU: ${result.data.cpu_percent || '--'}%`;
                document.getElementById('memory-usage').textContent = 
                    `MEM: ${result.data.memory_percent || '--'}%`;
            }
        } catch (error) {
            // Silently handle errors
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Terminal();
});