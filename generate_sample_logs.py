#!/usr/bin/env python3
"""
Sample log generator for testing PySyslog LFC
Generates various types of system logs similar to what rsyslog would handle
"""

import time
import random
import socket
import os
import sys
from datetime import datetime
from typing import List

class LogGenerator:
    """Generate sample system logs in RFC 3164 format"""
    
    def __init__(self):
        self.hostname = socket.gethostname()
        self.facilities = {
            'kern': 0,      # kernel messages
            'user': 1,      # user-level messages  
            'mail': 2,      # mail system
            'daemon': 3,    # system daemons
            'auth': 4,      # security/authorization messages
            'syslog': 5,    # messages generated internally by syslogd
            'lpr': 6,       # line printer subsystem
            'news': 7,      # network news subsystem
            'uucp': 8,      # UUCP subsystem
            'cron': 9,      # clock daemon
            'authpriv': 10, # security/authorization messages
            'ftp': 11,      # FTP daemon
            'local0': 16,   # local use facility 0
            'local1': 17,   # local use facility 1
            'local2': 18,   # local use facility 2
            'local3': 19,   # local use facility 3
            'local4': 20,   # local use facility 4
            'local5': 21,   # local use facility 5
            'local6': 22,   # local use facility 6
            'local7': 23,   # local use facility 7
        }
        
        self.severities = {
            'emerg': 0,     # Emergency: system is unusable
            'alert': 1,     # Alert: action must be taken immediately
            'crit': 2,      # Critical: critical conditions
            'err': 3,       # Error: error conditions
            'warning': 4,   # Warning: warning conditions
            'notice': 5,    # Notice: normal but significant condition
            'info': 6,      # Informational: informational messages
            'debug': 7,     # Debug: debug-level messages
        }
        
        # Sample log messages by category
        self.sample_messages = {
            'auth': [
                "pam_unix(sshd:session): session opened for user {user} by (uid=0)",
                "pam_unix(sshd:session): session closed for user {user}",
                "sshd[{pid}]: Accepted publickey for {user} from {ip} port {port} ssh2",
                "sshd[{pid}]: Failed password for {user} from {ip} port {port} ssh2",
                "sudo: {user} : TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND=/bin/ls",
                "su: pam_authenticate: Authentication failure",
            ],
            'daemon': [
                "systemd[1]: Started {service}.service",
                "systemd[1]: Stopped {service}.service", 
                "systemd[1]: {service}.service: Main process exited, code=exited, status=0/SUCCESS",
                "NetworkManager[{pid}]: <info>  [1234567890.123] device (eth0): state change: activated -> disconnected",
                "cron[{pid}]: (root) CMD ({command})",
                "dockerd[{pid}]: time=\"{timestamp}\" level=info msg=\"Container started\" containerID={container_id}",
            ],
            'kern': [
                "Out of memory: Kill process {pid} ({process}) score {score} or sacrifice child",
                "TCP: Peer {ip}:{port} unexpectedly shrunk window {window}",
                "ata1.00: exception Emask 0x0 SAct 0x0 SErr 0x0 action 0x0",
                "usb 1-1: new high-speed USB device number {device_num} using ehci-pci",
                "IPv4: martian source {ip} from {src_ip}, on dev eth0",
            ],
            'mail': [
                "postfix/pickup[{pid}]: {queue_id}: uid={uid} from=<{email}>",
                "postfix/cleanup[{pid}]: {queue_id}: message-id=<{message_id}>",
                "postfix/qmgr[{pid}]: {queue_id}: from=<{email}>, size={size}, nrcpt=1",
                "postfix/smtp[{pid}]: {queue_id}: to=<{email}>, relay={relay}, status=sent",
            ],
            'cron': [
                "(root) CMD ({command})",
                "(CRON) info (No MTA installed, discarding output)",
                "pam_unix(cron:session): session opened for user root by (uid=0)",
                "pam_unix(cron:session): session closed for user root",
            ]
        }
        
        # Sample data for placeholders
        self.users = ['root', 'admin', 'user1', 'developer', 'www-data', 'mysql']
        self.services = ['nginx', 'apache2', 'mysql', 'postgresql', 'redis', 'docker']
        self.processes = ['bash', 'python', 'node', 'java', 'nginx', 'systemd']
        self.commands = ['/usr/bin/updatedb', '/usr/bin/logrotate /etc/logrotate.conf', 
                        'test -x /usr/sbin/anacron', '/usr/bin/apt update']
        
    def generate_priority(self, facility: str, severity: str) -> int:
        """Generate RFC 3164 priority value"""
        return self.facilities[facility] * 8 + self.severities[severity]
    
    def generate_timestamp(self) -> str:
        """Generate RFC 3164 timestamp"""
        now = datetime.now()
        return now.strftime("%b %d %H:%M:%S")
    
    def fill_placeholders(self, message: str) -> str:
        """Fill placeholder values in message templates"""
        replacements = {
            'user': random.choice(self.users),
            'pid': random.randint(1000, 99999),
            'ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'port': random.randint(1024, 65535),
            'service': random.choice(self.services),
            'process': random.choice(self.processes),
            'score': random.randint(1, 1000),
            'device_num': random.randint(1, 10),
            'window': random.randint(1000, 9999),
            'src_ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'email': f"user{random.randint(1,100)}@example.com",
            'queue_id': ''.join(random.choices('ABCDEF0123456789', k=10)),
            'uid': random.randint(1000, 2000),
            'message_id': f"<{random.randint(1000000000, 9999999999)}@{self.hostname}>",
            'size': random.randint(1000, 50000),
            'relay': f"smtp{random.randint(1,5)}.example.com[{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}]:25",
            'command': random.choice(self.commands),
            'timestamp': datetime.now().isoformat(),
            'container_id': ''.join(random.choices('abcdef0123456789', k=12)),
        }
        
        for key, value in replacements.items():
            message = message.replace(f'{{{key}}}', str(value))
        
        return message
    
    def generate_log_entry(self, facility: str = None, severity: str = None) -> str:
        """Generate a single RFC 3164 log entry"""
        if facility is None:
            facility = random.choice(list(self.facilities.keys()))
        if severity is None:
            severity = random.choice(list(self.severities.keys()))
        
        priority = self.generate_priority(facility, severity)
        timestamp = self.generate_timestamp()
        
        # Choose appropriate message based on facility
        if facility in self.sample_messages:
            message_template = random.choice(self.sample_messages[facility])
        else:
            message_template = f"Sample {facility} message with pid {{pid}}"
        
        message = self.fill_placeholders(message_template)
        
        # RFC 3164 format: <priority>timestamp hostname tag: message
        tag = f"{facility}d" if facility != 'kern' else 'kernel'
        
        return f"<{priority}>{timestamp} {self.hostname} {tag}: {message}"
    
    def generate_batch(self, count: int = 10, facility: str = None) -> List[str]:
        """Generate a batch of log entries"""
        return [self.generate_log_entry(facility) for _ in range(count)]
    
    def write_to_file(self, filename: str, count: int = 100):
        """Write sample logs to a file"""
        with open(filename, 'w') as f:
            for _ in range(count):
                f.write(self.generate_log_entry() + '\n')
        print(f"Generated {count} log entries in {filename}")
    
    def send_to_socket(self, socket_path: str, count: int = 10):
        """Send sample logs to a Unix socket (like rsyslog would)"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            for _ in range(count):
                log_entry = self.generate_log_entry()
                sock.sendto(log_entry.encode(), socket_path)
                time.sleep(0.1)  # Small delay between messages
            sock.close()
            print(f"Sent {count} log entries to {socket_path}")
        except Exception as e:
            print(f"Error sending to socket {socket_path}: {e}")
    
    def continuous_generation(self, output_file: str, interval: float = 1.0):
        """Continuously generate logs (like a real system)"""
        print(f"Starting continuous log generation to {output_file}")
        print("Press Ctrl+C to stop")
        
        try:
            with open(output_file, 'a') as f:
                while True:
                    log_entry = self.generate_log_entry()
                    f.write(log_entry + '\n')
                    f.flush()
                    print(f"Generated: {log_entry}")
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped log generation")

def main():
    """Main function with command line interface"""
    generator = LogGenerator()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 generate_sample_logs.py file <filename> [count]")
        print("  python3 generate_sample_logs.py socket <socket_path> [count]")
        print("  python3 generate_sample_logs.py continuous <filename> [interval]")
        print("  python3 generate_sample_logs.py demo")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "demo":
        print("=== PySyslog LFC Sample Log Generator Demo ===")
        print("\nGenerating sample logs for different facilities:\n")
        
        for facility in ['auth', 'daemon', 'kern', 'mail', 'cron']:
            print(f"--- {facility.upper()} logs ---")
            logs = generator.generate_batch(3, facility)
            for log in logs:
                print(log)
            print()
    
    elif command == "file":
        if len(sys.argv) < 3:
            print("Error: filename required")
            sys.exit(1)
        filename = sys.argv[2]
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        generator.write_to_file(filename, count)
    
    elif command == "socket":
        if len(sys.argv) < 3:
            print("Error: socket path required")
            sys.exit(1)
        socket_path = sys.argv[2]
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        generator.send_to_socket(socket_path, count)
    
    elif command == "continuous":
        if len(sys.argv) < 3:
            print("Error: filename required")
            sys.exit(1)
        filename = sys.argv[2]
        interval = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        generator.continuous_generation(filename, interval)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
