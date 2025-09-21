import psutil
import platform
from datetime import datetime
from typing import Dict, List

class SystemMonitor:
    """Monitor system resources and processes"""
    
    def __init__(self):
        pass
    
    def get_system_info(self) -> Dict:
        """Get basic system information"""
        try:
            return {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
            }
        except Exception as e:
            return {'error': str(e), 'cpu_percent': 0, 'memory_percent': 0}
    
    def get_detailed_system_info(self) -> str:
        """Get detailed system information as formatted string"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"""System Information:
===================

Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor()}
CPU Cores: {psutil.cpu_count()}
CPU Usage: {psutil.cpu_percent(interval=1)}%

Memory:
  Total: {self._format_bytes(memory.total)}
  Used: {self._format_bytes(memory.used)} ({memory.percent:.1f}%)
  Available: {self._format_bytes(memory.available)}

Disk:
  Total: {self._format_bytes(disk.total)}
  Used: {self._format_bytes(disk.used)} ({disk.percent:.1f}%)
  Free: {self._format_bytes(disk.free)}

Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}
"""
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_process_list(self) -> str:
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'][:20],
                        'cpu': proc.info['cpu_percent'] or 0.0,
                        'memory': proc.info['memory_percent'] or 0.0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            
            header = f"{'PID':<8} {'NAME':<20} {'CPU%':<8} {'MEM%':<8}"
            separator = "-" * 50
            lines = [header, separator]
            
            for proc in processes[:20]:
                line = f"{proc['pid']:<8} {proc['name']:<20} {proc['cpu']:<8.1f} {proc['memory']:<8.1f}"
                lines.append(line)
            
            return '\n'.join(lines)
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_top_processes(self) -> str:
        """Get top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'][:15],
                        'cpu': proc.info['cpu_percent'] or 0.0,
                        'memory': proc.info['memory_percent'] or 0.0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            
            header = f"{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'COMMAND':<15}"
            separator = "-" * 45
            lines = [header, separator]
            
            for proc in processes[:15]:
                line = f"{proc['pid']:<8} {proc['cpu']:<8.1f} {proc['memory']:<8.1f} {proc['name']:<15}"
                lines.append(line)
            
            return '\n'.join(lines)
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"