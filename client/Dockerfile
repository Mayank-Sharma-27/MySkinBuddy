# This is a multi-stage build Dockerfile for the frontend
FROM --platform=linux/amd64 node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY ["package.json", "package-lock.json", "./"]
RUN echo "Contents of current directory:" && \
    ls -la && \
    echo "Installing dependencies..." && \
    npm install

# Copy environment file first
COPY [".env.production", ".env.local"]

# Copy rest of the source code
COPY . .

# Build the application
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV=production
ENV NEXT_SKIP_STATIC_GENERATION=true
# Add these environment variables to skip static generation
ENV NEXT_STATIC_BUILD=false
ENV NEXT_FORCE_DYNAMIC=true
RUN npm run build

# Production image
FROM --platform=linux/amd64 node:18-alpine AS runner
WORKDIR /app

# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Set environment variables
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

USER nextjs

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]