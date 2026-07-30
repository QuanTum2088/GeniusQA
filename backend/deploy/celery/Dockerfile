FROM mcr.microsoft.com/playwright:v1.51.0-jammy

# Install agent-browser CLI (optional but improves startup)
RUN npm i -g agent-browser@latest || true

# Create working dirs (will be mounted)
RUN mkdir -p /skill /runtime/screenshots /runtime/artifacts

WORKDIR /skill

# Entrypoint executes provided shell command
ENTRYPOINT ["/bin/bash","-lc"]

