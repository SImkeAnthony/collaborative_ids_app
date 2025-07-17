#!/bin/sh
curl -X POST http://localhost:8000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.0.1",
    "target_ip": "192.168.0.2",
    "service": "sshd",
    "timestamp": "2025-07-09T14:00:00Z",
    "reason": "Multiple failed login attempts",
    "level": "CRITICAL"
  }'
