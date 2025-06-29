#!/bin/bash
# Bind to the dynamic PORT provided by Render, default to 10000
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
