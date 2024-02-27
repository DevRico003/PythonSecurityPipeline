FROM jenkins/jenkins:lts

# Copy plugins.txt
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt

# Install Jenkins plugins
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Copy script to auto create user to Jenkins init folder
COPY setupJenkins.groovy /usr/share/jenkins/ref/init.groovy.d/

# Setup the docker container for scanners
USER root
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    curl \
    maven \
    git \
    perl \
    wget \
    kbtin \
    libnet-ssleay-perl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Add public key for the multiverse repo which has nikto
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
RUN add-apt-repository 'deb http://archive.ubuntu.com/ubuntu bionic multiverse'
RUN add-apt-repository 'deb http://archive.ubuntu.com/ubuntu bionic-security multiverse'
RUN add-apt-repository 'deb http://archive.ubuntu.com/ubuntu bionic-updates multiverse'

RUN apt-get update -y && apt-get install -y nikto

# Create a virtual environment to avoid conflicts with the system Python packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install various Python tools within the virtual environment
RUN pip3 install --upgrade pip && \
    pip3 install virtualenv safety liccheck trufflehog bandit selenium ansible boto boto3 --no-cache-dir

RUN ansible-galaxy collection install amazon.aws

# Configure Ansible to use right keys and not check host auth for this ephemeral/temp AWS host
COPY ansible.cfg /etc/ansible/ansible.cfg

COPY ~/.ssh/techstarter.pem /var/jenkins_home/.ssh/techstarter.pem

# Drop back to the regular Jenkins user - good practice
USER jenkins
