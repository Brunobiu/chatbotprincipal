#!/bin/bash
cd /app
python test_full_embedding.py > /tmp/test_output.txt 2>&1
echo "Exit code: $?" >> /tmp/test_output.txt
cat /tmp/test_output.txt
