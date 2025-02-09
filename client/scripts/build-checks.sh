#!/bin/bash

# Check environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
  echo "Error: AWS_ACCESS_KEY_ID is not set"
  exit 1
fi

# Add more checks as needed 