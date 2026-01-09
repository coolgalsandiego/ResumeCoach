/**
 * Frontend Logger for Resume Coach
 * Logs to console and saves to localStorage for debugging
 */

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs: number = 1000;
  private storageKey: string = 'resume_coach_frontend_logs';

  constructor() {
    // Load existing logs from localStorage
    this.loadLogs();
    
    // Log startup
    this.info('Frontend logger initialized');
  }

  private loadLogs(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to load logs from localStorage:', e);
      this.logs = [];
    }
  }

  private saveLogs(): void {
    try {
      // Keep only last maxLogs entries
      if (this.logs.length > this.maxLogs) {
        this.logs = this.logs.slice(-this.maxLogs);
      }
      localStorage.setItem(this.storageKey, JSON.stringify(this.logs));
    } catch (e) {
      console.error('Failed to save logs to localStorage:', e);
    }
  }

  private formatTimestamp(): string {
    const now = new Date();
    return now.toISOString().replace('T', ' ').replace('Z', '');
  }

  private log(level: LogLevel, message: string, data?: any): void {
    const timestamp = this.formatTimestamp();
    const entry: LogEntry = { timestamp, level, message, data };
    
    // Add to logs array
    this.logs.push(entry);
    this.saveLogs();

    // Console output with styling
    const styles: Record<LogLevel, string> = {
      DEBUG: 'color: #888',
      INFO: 'color: #2196F3',
      WARN: 'color: #FF9800',
      ERROR: 'color: #F44336; font-weight: bold',
    };

    const prefix = `[${timestamp}] [${level}]`;
    
    if (data !== undefined) {
      console.log(`%c${prefix} ${message}`, styles[level], data);
    } else {
      console.log(`%c${prefix} ${message}`, styles[level]);
    }
  }

  debug(message: string, data?: any): void {
    this.log('DEBUG', message, data);
  }

  info(message: string, data?: any): void {
    this.log('INFO', message, data);
  }

  warn(message: string, data?: any): void {
    this.log('WARN', message, data);
  }

  error(message: string, data?: any): void {
    this.log('ERROR', message, data);
  }

  // Get all logs as formatted string for export
  exportLogs(): string {
    return this.logs
      .map(entry => {
        const dataStr = entry.data ? ` | ${JSON.stringify(entry.data)}` : '';
        return `${entry.timestamp} | ${entry.level.padEnd(5)} | ${entry.message}${dataStr}`;
      })
      .join('\n');
  }

  // Download logs as a file
  downloadLogs(): void {
    const content = this.exportLogs();
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frontend-logs-${new Date().toISOString().split('T')[0]}.log`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Clear all logs
  clearLogs(): void {
    this.logs = [];
    localStorage.removeItem(this.storageKey);
    this.info('Logs cleared');
  }

  // Get recent logs
  getRecentLogs(count: number = 50): LogEntry[] {
    return this.logs.slice(-count);
  }
}

// Export singleton instance
export const logger = new Logger();

// Make logger available in browser console for debugging
if (typeof window !== 'undefined') {
  (window as any).frontendLogger = logger;
}

export default logger;

