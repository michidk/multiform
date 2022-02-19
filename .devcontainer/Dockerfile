ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Install various dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y --no-install-recommends install graphviz graphviz-dev

# Get golang installed. See: https://stackoverflow.com/questions/52056387/how-to-install-go-in-alpine-linux
ARG GOLANG_VERSION=1.17
RUN wget https://golang.org/dl/go$GOLANG_VERSION.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go$GOLANG_VERSION.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin
ENV PATH=$PATH:"/root/go/bin"
RUN which go && go version

# Install Azure CLI dependencies
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
RUN az extension add -n azure-devops
RUN which az && az --version

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN which aws && aws --version

# Install terraform
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add - \
    # Link up to repository before installing
    && apt-get --allow-releaseinfo-change update \
    && apt-get install -y software-properties-common --no-install-recommends \
    && apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    && apt-get update \
    && apt-get -y --no-install-recommends install terraform g++ gcc libc6-dev libffi-dev libgmp-dev make xz-utils zlib1g-dev git gnupg netbase graphviz
RUN which terraform && terraform version

# Terraform linting (taken from https://github.com/antonbabenko/pre-commit-terraform)
RUN curl -L https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
RUN which tflint && tflint --version

# Install tfdocs
RUN go install github.com/terraform-docs/terraform-docs@v0.15.0
RUN which terraform-docs && terraform-docs --version

# Install tfsec
RUN go install github.com/aquasecurity/tfsec/cmd/tfsec@latest
RUN which tfsec && tfsec --version

# Copy go installs to vscode user
ENV PATH=$PATH:/home/vscode/go/bin/
RUN mkdir -p /home/vscode/go/bin/ && cp -r root/go/bin/* /home/vscode/go/bin/

# Install just
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /bin

# Setup aliases
RUN echo 'alias tf="terraform"' >> /home/vscode/.bashrc
