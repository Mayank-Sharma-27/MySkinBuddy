#!/bin/bash

# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repositories if they don't exist
aws ecr create-repository --repository-name myskinbuddy-backend --region us-east-1 || true
aws ecr create-repository --repository-name myskinbuddy-frontend --region us-east-1 || true

# Build and tag images
docker build -t myskinbuddy-backend ./server
docker build -t myskinbuddy-frontend ./client

# Tag images for ECR
docker tag myskinbuddy-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-backend:latest
docker tag myskinbuddy-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-frontend:latest

# Push images to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-frontend:latest 