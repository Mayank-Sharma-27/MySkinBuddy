# AWS Target Group Settings

## Backend Target Group Configuration

The following settings have been tested and confirmed working for the backend service:

### Target Group Details

- Name: `myskinbuddy-backend-8080`
- Protocol: HTTP
- Port: 8080
- Target Type: ip

### Health Check Settings

```json
{
  "HealthCheckProtocol": "HTTP",
  "HealthCheckPort": "traffic-port",
  "HealthCheckPath": "/health",
  "HealthCheckIntervalSeconds": 60,
  "HealthCheckTimeoutSeconds": 30,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 5,
  "Matcher": {
    "HttpCode": "200"
  }
}
```

### AWS CLI Reference

To modify these settings for a target group:

```bash
aws elbv2 modify-target-group \
  --target-group-arn <target-group-arn> \
  --health-check-interval-seconds 60 \
  --health-check-timeout-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 5
```

### Important Notes

1. These settings provide optimal balance between:

   - Quick detection of unhealthy instances (2 successful checks needed)
   - Tolerance for temporary issues (5 failed checks before marking unhealthy)
   - Adequate time for container startup (30s timeout)
   - Reasonable check frequency (60s interval)

2. The health check endpoint `/health` should return a 200 status code
