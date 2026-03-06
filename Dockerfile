# Base image with Python 3.14
FROM python:3.14-slim
ENV NODE_ENV=development

# Install Node.js v20, git, build tools
RUN apt-get update && apt-get install -y curl git build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Force rebuild from here down
ARG CACHE_BUST
RUN echo "Cache bust value: ${CACHE_BUST}"

# Copy install script
ADD scripts/install.sh .
RUN chmod +x install.sh 
#RUN chmod +x install.sh && ./install.sh --dry-run