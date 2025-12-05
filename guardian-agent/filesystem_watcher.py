"""
Filesystem watcher for monitoring workflow logs.
"""
import os
import json
import time
from pathlib import Path
from typing import List, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import guardian_logger
from guardian_agent.config import config
from guardian_agent.event_collector import EventCollector


class LogFileHandler(FileSystemEventHandler):
    """Handles log file changes."""
    
    def __init__(self, event_collector: EventCollector):
        self.event_collector = event_collector
        self.processed_files = set()
        self.last_position = {}  # Track file positions for incremental reading
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        if isinstance(event, FileModifiedEvent):
            self._process_file(event.src_path)
    
    def _process_file(self, file_path: str):
        """Process a log file for new events."""
        try:
            if file_path.endswith('.jsonl'):
                self._process_jsonl(file_path)
            elif file_path.endswith('.log'):
                self._process_log(file_path)
        except Exception as e:
            guardian_logger.error(f"Error processing file {file_path}: {e}")
    
    def _process_jsonl(self, file_path: str):
        """Process a JSONL log file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Get last known position
                last_pos = self.last_position.get(file_path, 0)
                f.seek(last_pos)
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        self._parse_jsonl_event(data, file_path)
                    except json.JSONDecodeError:
                        guardian_logger.warning(f"Invalid JSON in {file_path}: {line[:100]}")
                
                # Update position
                self.last_position[file_path] = f.tell()
        
        except FileNotFoundError:
            pass
        except Exception as e:
            guardian_logger.error(f"Error reading JSONL file {file_path}: {e}")
    
    def _process_log(self, file_path: str):
        """Process a plain text log file."""
        # Basic log parsing - can be extended
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                last_pos = self.last_position.get(file_path, 0)
                f.seek(last_pos)
                
                for line in f:
                    # Simple heuristic: look for suspicious patterns
                    line_lower = line.lower()
                    if any(pattern in line_lower for pattern in ["error", "warning", "unauthorized", "failed"]):
                        self.event_collector.collect_system_anomaly(
                            anomaly_type="log_warning",
                            description=line.strip()[:500],
                            metadata={"log_file": file_path}
                        )
                
                self.last_position[file_path] = f.tell()
        
        except FileNotFoundError:
            pass
        except Exception as e:
            guardian_logger.error(f"Error reading log file {file_path}: {e}")
    
    def _parse_jsonl_event(self, data: dict, source_file: str):
        """Parse a JSONL event and collect it."""
        event_type = data.get("type", "unknown")
        
        if event_type == "tool_call":
            self.event_collector.collect_tool_call(
                tool_name=data.get("tool", "unknown"),
                tool_args=data.get("args", {}),
                return_value=data.get("return_value"),
                metadata={"source_file": source_file, **data.get("metadata", {})}
            )
        elif event_type == "llm_completion":
            self.event_collector.collect_llm_completion(
                prompt=data.get("prompt", ""),
                response=data.get("response", ""),
                model=data.get("model"),
                metadata={"source_file": source_file, **data.get("metadata", {})}
            )
        elif event_type == "api_access":
            self.event_collector.collect_api_access(
                endpoint=data.get("endpoint", ""),
                method=data.get("method", "GET"),
                status_code=data.get("status_code"),
                metadata={"source_file": source_file, **data.get("metadata", {})}
            )


class FilesystemWatcher:
    """Watches filesystem for workflow logs."""
    
    def __init__(self, event_collector: EventCollector):
        self.event_collector = event_collector
        self.observer = Observer()
        self.handler = LogFileHandler(event_collector)
        self.watched_paths = []
    
    def start(self, watch_paths: Optional[List[str]] = None):
        """
        Start watching filesystem.
        
        Args:
            watch_paths: Optional list of paths to watch (defaults to current directory)
        """
        if watch_paths is None:
            watch_paths = ["."]
        
        for path in watch_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                self.observer.schedule(self.handler, abs_path, recursive=True)
                self.watched_paths.append(abs_path)
                guardian_logger.info(f"Watching path: {abs_path}")
            else:
                guardian_logger.warning(f"Path does not exist: {abs_path}")
        
        self.observer.start()
        guardian_logger.info("Filesystem watcher started")
    
    def stop(self):
        """Stop watching filesystem."""
        self.observer.stop()
        self.observer.join()
        guardian_logger.info("Filesystem watcher stopped")

