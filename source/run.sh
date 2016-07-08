#!/bin/bash

cd /home-backup/ADT/adt_tools/
source /tmp/adt_tool_v1/bin/activate
gunicorn -t 10000 -b 0.0.0.0:8080 wsgi