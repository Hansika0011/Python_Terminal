import os
from flask import Flask, render_template, request, jsonify
from .terminal import PythonTerminal
from .ai_processor import AIProcessor
from .system_monitor import SystemMonitor

# Get the correct paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
template_dir = os.path.join(parent_dir, 'templates')
static_dir = os.path.join(parent_dir, 'static')

# Initialize Flask app with correct paths
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
app.secret_key = os.urandom(24)

# Initialize core components
terminal = PythonTerminal()
ai_processor = AIProcessor()
system_monitor = SystemMonitor()

@app.route('/')
def index():
    """Render the main terminal interface"""
    # Debug information (remove in production)
    print(f"Template folder: {template_dir}")
    print(f"Template folder exists: {os.path.exists(template_dir)}")
    if os.path.exists(template_dir):
        print(f"Files in templates: {os.listdir(template_dir)}")
    
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute terminal commands or AI queries"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({
                'success': False,
                'output': 'Error: Empty command',
                'type': 'error'
            })
        
        # Check if it's an AI query (starts with natural language indicators)
        ai_indicators = ['create', 'make', 'show me', 'list all', 'find', 'search', 'what is']
        is_ai_query = any(command.lower().startswith(indicator) for indicator in ai_indicators)
        
        if is_ai_query:
            # Process with AI
            result = ai_processor.process_query(command)
            if result['requires_execution']:
                # Execute the generated command
                output = terminal.execute_command(result['command'])
                return jsonify({
                    'success': True,
                    'output': f"AI: {result['explanation']}\nExecuting: {result['command']}\n\n{output}",
                    'type': 'ai_command'
                })
            else:
                return jsonify({
                    'success': True,
                    'output': result['explanation'],
                    'type': 'ai_response'
                })
        else:
            # Direct command execution
            output = terminal.execute_command(command)
            return jsonify({
                'success': True,
                'output': output,
                'type': 'command'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'Error: {str(e)}',
            'type': 'error'
        })

@app.route('/system_info')
def get_system_info():
    """Get current system information"""
    try:
        info = system_monitor.get_system_info()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/history')
def get_command_history():
    """Get command execution history"""
    try:
        history = terminal.get_command_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)