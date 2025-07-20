#!/bin/sh
curl -X POST http://localhost:8000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.0.1",
    "target_ip": "192.168.0.2",
    "port": 22,
    "protocol": "ssh",
    "alert_type": "ssh_brute_force",
    "severity": "high",
    "jail": "sshd",
    "action": "banip",
    "ip": "124.56.63.32",
    "reason": "Multiple failed login attempts"
  }'
