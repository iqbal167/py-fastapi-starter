"""
Utilities for parsing and analyzing JSON logs.
"""
import json
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime
from pathlib import Path


class LogEntry:
    """Represents a single log entry."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.timestamp = data.get("timestamp")
        self.level = data.get("level")
        self.logger = data.get("logger")
        self.event = data.get("event")
        self.service = data.get("service")
        self.version = data.get("version")
        self.environment = data.get("environment")
        self.request_id = data.get("request_id")
    
    def __repr__(self):
        return f"LogEntry(timestamp={self.timestamp}, level={self.level}, event={self.event})"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from log data."""
        return self.data.get(key, default)
    
    def has_field(self, field: str) -> bool:
        """Check if log entry has a specific field."""
        return field in self.data
    
    def matches_filter(self, **filters) -> bool:
        """Check if log entry matches given filters."""
        for key, value in filters.items():
            if key not in self.data or self.data[key] != value:
                return False
        return True


class LogParser:
    """Parser for JSON log files."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.entries: List[LogEntry] = []
    
    def parse_file(self, file_path: str) -> List[LogEntry]:
        """Parse JSON log file and return list of log entries."""
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        log_data = json.loads(line)
                        entries.append(LogEntry(log_data))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON on line {line_num}: {e}")
                        continue
        
        except FileNotFoundError:
            print(f"Error: Log file '{file_path}' not found")
            return []
        except Exception as e:
            print(f"Error reading log file: {e}")
            return []
        
        self.entries = entries
        return entries
    
    def parse_string(self, log_string: str) -> List[LogEntry]:
        """Parse JSON log string and return list of log entries."""
        entries = []
        
        for line_num, line in enumerate(log_string.strip().split('\n'), 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                log_data = json.loads(line)
                entries.append(LogEntry(log_data))
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
                continue
        
        self.entries = entries
        return entries
    
    def filter_by_level(self, level: str) -> List[LogEntry]:
        """Filter log entries by level."""
        return [entry for entry in self.entries if entry.level == level.lower()]
    
    def filter_by_logger(self, logger: str) -> List[LogEntry]:
        """Filter log entries by logger name."""
        return [entry for entry in self.entries if entry.logger == logger]
    
    def filter_by_request_id(self, request_id: str) -> List[LogEntry]:
        """Filter log entries by request ID."""
        return [entry for entry in self.entries if entry.request_id == request_id]
    
    def filter_by_timerange(self, start_time: str, end_time: str) -> List[LogEntry]:
        """Filter log entries by time range."""
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            filtered = []
            for entry in self.entries:
                if entry.timestamp:
                    entry_dt = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))
                    if start_dt <= entry_dt <= end_dt:
                        filtered.append(entry)
            
            return filtered
        except ValueError as e:
            print(f"Error parsing datetime: {e}")
            return []
    
    def get_error_logs(self) -> List[LogEntry]:
        """Get all error level logs."""
        return self.filter_by_level("error")
    
    def get_request_logs(self) -> List[LogEntry]:
        """Get all request-related logs."""
        return [entry for entry in self.entries if entry.request_id is not None]
    
    def get_unique_request_ids(self) -> List[str]:
        """Get list of unique request IDs."""
        request_ids = set()
        for entry in self.entries:
            if entry.request_id:
                request_ids.add(entry.request_id)
        return list(request_ids)
    
    def get_request_trace(self, request_id: str) -> List[LogEntry]:
        """Get all log entries for a specific request ID."""
        return self.filter_by_request_id(request_id)
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        durations = []
        status_codes = {}
        
        for entry in self.entries:
            # Collect duration data
            if entry.has_field("duration_ms"):
                durations.append(entry.get("duration_ms"))
            
            # Collect status code data
            if entry.has_field("status_code"):
                status_code = entry.get("status_code")
                status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        analysis = {
            "total_requests": len([e for e in self.entries if e.has_field("status_code")]),
            "status_codes": status_codes,
        }
        
        if durations:
            analysis.update({
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "slow_requests": len([d for d in durations if d > 1000]),  # > 1 second
            })
        
        return analysis
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary statistics of logs."""
        levels = {}
        loggers = {}
        
        for entry in self.entries:
            # Count by level
            if entry.level:
                levels[entry.level] = levels.get(entry.level, 0) + 1
            
            # Count by logger
            if entry.logger:
                loggers[entry.logger] = loggers.get(entry.logger, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "levels": levels,
            "loggers": loggers,
            "unique_request_ids": len(self.get_unique_request_ids()),
            "time_range": {
                "start": self.entries[0].timestamp if self.entries else None,
                "end": self.entries[-1].timestamp if self.entries else None,
            }
        }
    
    def export_filtered_logs(self, entries: List[LogEntry], output_file: str) -> None:
        """Export filtered log entries to a file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(json.dumps(entry.data) + '\n')
            print(f"Exported {len(entries)} log entries to {output_file}")
        except Exception as e:
            print(f"Error exporting logs: {e}")


def parse_log_file(file_path: str) -> LogParser:
    """Convenience function to parse a log file."""
    parser = LogParser()
    parser.parse_file(file_path)
    return parser


def parse_log_string(log_string: str) -> LogParser:
    """Convenience function to parse a log string."""
    parser = LogParser()
    parser.parse_string(log_string)
    return parser


# Example usage functions
def analyze_request_performance(log_file: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze performance for a specific request or all requests."""
    parser = parse_log_file(log_file)
    
    if request_id:
        entries = parser.get_request_trace(request_id)
        if not entries:
            return {"error": f"No logs found for request_id: {request_id}"}
        
        # Analyze specific request
        start_time = None
        end_time = None
        events = []
        
        for entry in entries:
            events.append({
                "timestamp": entry.timestamp,
                "event": entry.event,
                "logger": entry.logger,
                "duration_ms": entry.get("duration_ms")
            })
            
            if not start_time or entry.timestamp < start_time:
                start_time = entry.timestamp
            if not end_time or entry.timestamp > end_time:
                end_time = entry.timestamp
        
        return {
            "request_id": request_id,
            "start_time": start_time,
            "end_time": end_time,
            "total_events": len(events),
            "events": events
        }
    else:
        return parser.analyze_performance()


def find_slow_requests(log_file: str, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
    """Find requests that took longer than threshold."""
    parser = parse_log_file(log_file)
    slow_requests = []
    
    for entry in parser.entries:
        if (entry.has_field("duration_ms") and 
            entry.get("duration_ms") > threshold_ms and
            entry.request_id):
            
            slow_requests.append({
                "request_id": entry.request_id,
                "duration_ms": entry.get("duration_ms"),
                "method": entry.get("method"),
                "url": entry.get("url"),
                "status_code": entry.get("status_code"),
                "timestamp": entry.timestamp
            })
    
    return sorted(slow_requests, key=lambda x: x["duration_ms"], reverse=True)


def find_error_patterns(log_file: str) -> Dict[str, Any]:
    """Find common error patterns in logs."""
    parser = parse_log_file(log_file)
    error_logs = parser.get_error_logs()
    
    error_types = {}
    error_messages = {}
    
    for entry in error_logs:
        # Group by error type
        error_type = entry.get("error_type", "Unknown")
        error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Group by error message
        error_msg = entry.get("error", entry.event)
        if error_msg:
            error_messages[error_msg] = error_messages.get(error_msg, 0) + 1
    
    return {
        "total_errors": len(error_logs),
        "error_types": error_types,
        "common_messages": dict(sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10])
    }
