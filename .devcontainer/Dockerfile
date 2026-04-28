# Image for a NYU Lab development environment
FROM quay.io/rofrano/nyu-devops-base:sp26

# Install Chromium and chromedriver so Selenium-based BDD tests work out of the box
RUN sudo apt-get update && \
    sudo apt-get install -y --no-install-recommends chromium chromium-driver && \
    sudo rm -rf /var/lib/apt/lists/*

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN sudo python -m pip install --upgrade pip pipenv && \
    sudo pipenv install --system --dev

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh
