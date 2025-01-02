# MySkinBuddy Deployment Guide

This guide documents the complete deployment process for MySkinBuddy application on AWS using ECS Fargate.

## 1. Docker Image Creation and Push

### Frontend Image

#### Step

Build and push the frontend Docker image to Amazon ECR.

#### Why

- Containerization ensures consistent environment across development and production
- ECR provides secure, scalable container image storage
- Enables easy deployment and version management

#### How

```bash
# Build the image
docker build -t myskinbuddy-frontend:latest ./client

# Tag the image
docker tag myskinbuddy-frontend:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-frontend:latest

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-frontend:latest
```

#### What if we skip this

- No containerized application to deploy
- Inconsistent environments between development and production
- Manual dependency management on production servers

### Backend Image

#### Step

Build and push the backend Docker image to Amazon ECR.

#### Why

- Ensures Python environment consistency
- Packages all dependencies
- Enables scalable deployment

#### How

```bash
# Build the image
docker build -t myskinbuddy-backend:latest ./server

# Tag the image
docker tag myskinbuddy-backend:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-backend:latest

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/myskinbuddy-backend:latest
```

#### What if we skip this

- No containerized backend service
- Difficult dependency management
- Inconsistent Python environments

## 2. AWS Infrastructure Setup

### 2.1 IAM Role Creation

#### Step

Create IAM roles for ECS tasks execution.

#### Why

- Provides necessary permissions for ECS tasks
- Enables secure access to AWS services
- Follows principle of least privilege

#### How

```bash
# Create task execution role
aws iam create-role --role-name MySkinBuddyECSTaskExecutionRole --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

# Attach necessary policies
aws iam attach-role-policy --role-name MySkinBuddyECSTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

#### What if we skip this

- ECS tasks won't have permissions to access AWS services
- Cannot pull images from ECR
- Cannot write logs to CloudWatch

### 2.2 Security Groups

#### Step

Create security groups for ALB and ECS tasks.

#### Why

- Controls inbound/outbound traffic
- Secures application components
- Enables proper network isolation

#### How

```bash
# Create ALB security group
aws ec2 create-security-group --group-name myskinbuddy-alb-sg --description "Security group for MySkinBuddy ALB"

# Create ECS tasks security group
aws ec2 create-security-group --group-name myskinbuddy-ecs-sg --description "Security group for MySkinBuddy ECS tasks"

# Configure security group rules
aws ec2 authorize-security-group-ingress --group-name myskinbuddy-alb-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-name myskinbuddy-ecs-sg --protocol tcp --port 3000 --source-group myskinbuddy-alb-sg
aws ec2 authorize-security-group-ingress --group-name myskinbuddy-ecs-sg --protocol tcp --port 5000 --source-group myskinbuddy-alb-sg
```

#### What if we skip this

- No network security
- Exposed services to unauthorized access
- No traffic control between components

### 2.3 Parameter Store Setup

#### Step

Store sensitive configuration in AWS Systems Manager Parameter Store.

#### Why

- Secure storage for sensitive data
- Centralized configuration management
- Easy rotation of secrets

#### How

```bash
# Create parameters
aws ssm put-parameter --name "/myskinbuddy/AWS_ACCESS_KEY_ID" --type "SecureString" --value "YOUR_VALUE"
aws ssm put-parameter --name "/myskinbuddy/AWS_SECRET_ACCESS_KEY" --type "SecureString" --value "YOUR_VALUE"
aws ssm put-parameter --name "/myskinbuddy/GOOGLE_CLIENT_ID" --type "SecureString" --value "YOUR_VALUE"
# ... (other parameters)
```

#### What if we skip this

- Exposed sensitive data in code/configuration
- Difficult secrets management
- Security vulnerabilities

## 3. Load Balancer Setup

### Step

Create Application Load Balancer and target groups.

### Why

- Distributes traffic across tasks
- Enables high availability
- Provides single entry point for application

### How

```bash
# Create ALB
aws elbv2 create-load-balancer --name myskinbuddy-alb --subnets subnet-xxx subnet-yyy --security-groups sg-xxx

# Create target groups
aws elbv2 create-target-group --name myskinbuddy-frontend --protocol HTTP --port 3000 --vpc-id vpc-xxx --target-type ip
aws elbv2 create-target-group --name myskinbuddy-backend --protocol HTTP --port 5000 --vpc-id vpc-xxx --target-type ip

# Create listener rules
aws elbv2 create-listener --load-balancer-arn alb-arn --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=frontend-tg-arn
```

### What if we skip this

- No load distribution
- Single point of failure
- No health checks
- Difficult scaling

## 4. ECS Cluster and Services

### 4.1 ECS Cluster Creation

#### Step

Create ECS cluster for running containerized applications.

#### Why

- Provides container orchestration
- Manages task placement
- Enables service scaling

#### How

```bash
aws ecs create-cluster --cluster-name myskinbuddy-cluster --capacity-providers FARGATE
```

#### What if we skip this

- No container orchestration platform
- Manual container management
- No automated scaling

### 4.2 Task Definitions

#### Step

Create task definitions for frontend and backend services.

#### Why

- Defines container configurations
- Specifies resource requirements
- Sets environment variables

#### How

```bash
aws ecs register-task-definition --cli-input-json file://task-definition-frontend.json
aws ecs register-task-definition --cli-input-json file://task-definition-backend.json
```

#### What if we skip this

- No container configuration
- Cannot run tasks
- No resource allocation

### 4.3 ECS Services

#### Step

Create ECS services to run and maintain tasks.

#### Why

- Ensures desired number of tasks
- Handles task failures
- Integrates with load balancer

#### How

```bash
aws ecs create-service --cluster myskinbuddy-cluster --service-name myskinbuddy-frontend --task-definition myskinbuddy-frontend:1 --desired-count 1 --launch-type FARGATE
aws ecs create-service --cluster myskinbuddy-cluster --service-name myskinbuddy-backend --task-definition myskinbuddy-backend:1 --desired-count 1 --launch-type FARGATE
```

#### What if we skip this

- No automated task management
- Manual scaling
- No high availability

## 5. DNS and SSL (Optional)

### Step

Configure custom domain and SSL certificate.

### Why

- Professional appearance
- Secure communication
- Better user trust

### How

```bash
# Create SSL certificate
aws acm request-certificate --domain-name myskinbuddy.com

# Create Route 53 records
aws route53 change-resource-record-sets --hosted-zone-id ZONE_ID --change-batch file://dns-records.json
```

### What if we skip this

- No custom domain
- Insecure HTTP communication
- Less professional appearance

## 6. Monitoring and Logging

### Step

Set up CloudWatch logs and metrics.

### Why

- Application monitoring
- Performance tracking
- Issue diagnosis

### How

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/myskinbuddy

# Set retention policy
aws logs put-retention-policy --log-group-name /ecs/myskinbuddy --retention-in-days 7
```

### What if we skip this

- No application logs
- Difficult troubleshooting
- No performance metrics

```

```
