import os
import subprocess
import platform
import shlex
from datetime import datetime
from .system_monitor import SystemMonitor

class PythonTerminal:
    """Main terminal class that handles command execution"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.command_history = []
        self.system_monitor = SystemMonitor()
        self.supported_commands = {
            'ls', 'dir', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv',
            'cat', 'echo', 'touch', 'find', 'grep', 'ps', 'kill', 'top',
            'whoami', 'date', 'clear', 'help', 'history', 'sysinfo'
        }
    
    def execute_command(self, command):
        """Execute a given command and return the output"""
        try:
            # Log command to history
            self._add_to_history(command)
            
            # Parse command
            if not command.strip():
                return "Error: Empty command"
            
            parts = shlex.split(command.strip())
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Handle built-in commands
            if cmd in ['ls', 'dir']:
                return self._list_directory(args)
            elif cmd == 'cd':
                return self._change_directory(args)
            elif cmd == 'pwd':
                return self.current_directory
            elif cmd == 'mkdir':
                return self._make_directory(args)
            elif cmd in ['rmdir', 'rm']:
                return self._remove_path(args)
            elif cmd == 'cp':
                return self._copy_file(args)
            elif cmd == 'mv':
                return self._move_file(args)
            elif cmd == 'cat':
                return self._read_file(args)
            elif cmd == 'echo':
                return ' '.join(args)
            elif cmd == 'touch':
                return self._create_file(args)
            elif cmd == 'find':
                return self._find_files(args)
            elif cmd == 'grep':
                return self._grep_content(args)
            elif cmd == 'ps':
                return self.system_monitor.get_process_list()
            elif cmd == 'kill':
                return self._kill_process(args)
            elif cmd == 'top':
                return self.system_monitor.get_top_processes()
            elif cmd == 'whoami':
                return os.getlogin() if hasattr(os, 'getlogin') else 'user'
            elif cmd == 'date':
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elif cmd == 'clear':
                return '\033[2J\033[H'  # ANSI clear screen
            elif cmd == 'help':
                return self._show_help()
            elif cmd == 'history':
                return self._show_history()
            elif cmd == 'sysinfo':
                return self.system_monitor.get_detailed_system_info()
            else:
                # Try to execute as system command
                return self._execute_system_command(command)
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _list_directory(self, args):
        """List directory contents"""
        try:
            path = args[0] if args else self.current_directory
            if not os.path.exists(path):
                return f"Error: Path '{path}' does not exist"
            
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"[DIR]  {item}")
                else:
                    size = os.path.getsize(item_path)
                    items.append(f"[FILE] {item} ({size} bytes)")
            
            return '\n'.join(sorted(items))
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _change_directory(self, args):
        """Change current directory"""
        try:
            if not args:
                # Go to home directory
                new_path = os.path.expanduser('~')
            else:
                new_path = args[0]
                if not os.path.isabs(new_path):
                    new_path = os.path.join(self.current_directory, new_path)
            
            new_path = os.path.normpath(new_path)
            
            if not os.path.exists(new_path):
                return f"Error: Directory '{new_path}' does not exist"
            
            if not os.path.isdir(new_path):
                return f"Error: '{new_path}' is not a directory"
            
            self.current_directory = new_path
            os.chdir(self.current_directory)
            return f"Changed directory to: {self.current_directory}"
        
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _make_directory(self, args):
        """Create a new directory"""
        if not args:
            return "Error: Directory name required"
        
        try:
            dir_path = args[0]
            if not os.path.isabs(dir_path):
                dir_path = os.path.join(self.current_directory, dir_path)
            
            os.makedirs(dir_path, exist_ok=False)
            return f"Directory created: {dir_path}"
        
        except FileExistsError:
            return f"Error: Directory '{dir_path}' already exists"
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _remove_path(self, args):
        """Remove file or directory"""
        if not args:
            return "Error: Path required"
        
        try:
            target_path = args[0]
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_directory, target_path)
            
            if not os.path.exists(target_path):
                return f"Error: Path '{target_path}' does not exist"
            
            if os.path.isdir(target_path):
                os.rmdir(target_path)
                return f"Directory removed: {target_path}"
            else:
                os.remove(target_path)
                return f"File removed: {target_path}"
        
        except OSError as e:
            return f"Error: {str(e)}"
    
    def _copy_file(self, args):
        """Copy file from source to destination"""
        if len(args) < 2:
            return "Error: Source and destination required"
        
        try:
            import shutil
            src, dst = args[0], args[1]
            
            if not os.path.isabs(src):
                src = os.path.join(self.current_directory, src)
            if not os.path.isabs(dst):
                dst = os.path.join(self.current_directory, dst)
            
            shutil.copy2(src, dst)
            return f"Copied '{src}' to '{dst}'"
        
        except FileNotFoundError:
            return f"Error: Source file '{src}' not found"
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _move_file(self, args):
        """Move/rename file"""
        if len(args) < 2:
            return "Error: Source and destination required"
        
        try:
            import shutil
            src, dst = args[0], args[1]
            
            if not os.path.isabs(src):
                src = os.path.join(self.current_directory, src)
            if not os.path.isabs(dst):
                dst = os.path.join(self.current_directory, dst)
            
            shutil.move(src, dst)
            return f"Moved '{src}' to '{dst}'"
        
        except FileNotFoundError:
            return f"Error: Source '{src}' not found"
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _read_file(self, args):
        """Read and display file contents"""
        if not args:
            return "Error: Filename required"
        
        try:
            file_path = args[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.current_directory, file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content if content else "(empty file)"
        
        except FileNotFoundError:
            return f"Error: File '{file_path}' not found"
        except PermissionError:
            return "Error: Permission denied"
        except UnicodeDecodeError:
            return "Error: Cannot read binary file"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _create_file(self, args):
        """Create empty file"""
        if not args:
            return "Error: Filename required"
        
        try:
            file_path = args[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.current_directory, file_path)
            
            with open(file_path, 'a'):
                pass  # Create empty file
            return f"File created: {file_path}"
        
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _find_files(self, args):
        """Find files matching pattern"""
        if not args:
            return "Error: Search pattern required"
        
        try:
            import fnmatch
            pattern = args[0]
            search_path = args[1] if len(args) > 1 else self.current_directory
            
            matches = []
            for root, dirs, files in os.walk(search_path):
                for filename in fnmatch.filter(files, pattern):
                    matches.append(os.path.join(root, filename))
            
            return '\n'.join(matches) if matches else "No files found"
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _grep_content(self, args):
        """Search for text in files"""
        if len(args) < 2:
            return "Error: Pattern and filename required"
        
        try:
            pattern, filename = args[0], args[1]
            if not os.path.isabs(filename):
                filename = os.path.join(self.current_directory, filename)
            
            matches = []
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.lower() in line.lower():
                        matches.append(f"{line_num}: {line.strip()}")
            
            return '\n'.join(matches) if matches else "No matches found"
        
        except FileNotFoundError:
            return f"Error: File '{filename}' not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _kill_process(self, args):
        """Kill process by PID"""
        if not args:
            return "Error: Process ID required"
        
        try:
            pid = int(args[0])
            import signal
            os.kill(pid, signal.SIGTERM)
            return f"Process {pid} terminated"
        
        except ValueError:
            return "Error: Invalid process ID"
        except ProcessLookupError:
            return f"Error: Process {pid} not found"
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _execute_system_command(self, command):
        """Execute system command as fallback"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_directory,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            
            return output if output else "Command executed successfully"
        
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _show_help(self):
        """Show available commands"""
        help_text = """
Available Commands:

File Operations:
  ls/dir [path]     - List directory contents
  cd [path]         - Change directory
  pwd               - Show current directory
  mkdir <name>      - Create directory
  rm/rmdir <path>   - Remove file/directory
  cp <src> <dst>    - Copy file
  mv <src> <dst>    - Move/rename file
  cat <file>        - Display file contents
  touch <file>      - Create empty file
  find <pattern>    - Find files matching pattern
  grep <text> <file> - Search text in file

System Operations:
  ps                - List processes
  kill <pid>        - Terminate process
  top               - Show top processes
  sysinfo           - System information
  whoami            - Current user
  date              - Current date/time

Utility:
  echo <text>       - Print text
  clear             - Clear screen
  help              - Show this help
  history           - Command history

AI Commands (Natural Language):
  "create a folder called test"
  "show me all Python files"
  "find files containing 'hello'"
        """
        return help_text.strip()
    
    def _show_history(self):
        """Show command history"""
        if not self.command_history:
            return "No commands in history"
        
        history_lines = []
        for i, entry in enumerate(self.command_history[-20:], 1):  # Last 20 commands
            timestamp = entry['timestamp'].strftime('%H:%M:%S')
            history_lines.append(f"{i:2d}. [{timestamp}] {entry['command']}")
        
        return '\n'.join(history_lines)
    
    def _add_to_history(self, command):
        """Add command to history"""
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now()
        })
        
        # Keep only last 100 commands
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
    
    def get_command_history(self):
        """Get command history for API"""
        return [
            {
                'command': entry['command'],
                'timestamp': entry['timestamp'].isoformat()
            }
            for entry in self.command_history[-50:]  # Last 50 commands
        ]