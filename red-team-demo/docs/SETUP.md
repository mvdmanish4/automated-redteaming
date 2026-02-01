# Setup Instructions

This document provides detailed instructions for setting up the Red Team Demonstration environment.

## System Requirements

### Hardware
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 5GB free space

### Software
- **Operating System**: macOS, Linux, or Windows with WSL2
- **Python**: 3.8 or higher
- **Docker**: 20.10 or higher
- **Google Cloud SDK**: Latest version

---

## Step 1: Install Prerequisites

### Python

**macOS (with Homebrew):**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Verify installation:**
```bash
python3 --version
# Should output: Python 3.8+ or higher
```

### Docker

**macOS:**
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or with Homebrew:
brew install --cask docker
```

**Ubuntu:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
```

**Verify Docker is running:**
```bash
docker info
```

### Google Cloud SDK

**macOS (with Homebrew):**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
# Download and install
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
tar -xf google-cloud-cli-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Restart your shell or run:
source ~/.bashrc  # or ~/.zshrc
```

**Verify installation:**
```bash
gcloud --version
```

---

## Step 2: GCP Project Setup

### Create or Select a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Note your **Project ID** (e.g., `yc-hack-org`)

### Enable Billing

1. Navigate to **Billing** in the Cloud Console
2. Link a billing account to your project
3. Cloud Run has a generous free tier, but billing must be enabled

### Enable Required APIs

You can enable APIs via the console or CLI:

**Using gcloud CLI:**
```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

**Using Cloud Console:**
1. Go to **APIs & Services** > **Library**
2. Search and enable:
   - Cloud Run API
   - Container Registry API
   - Cloud Build API

### Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set your default project
gcloud config set project YOUR_PROJECT_ID

# Configure Docker for GCR
gcloud auth configure-docker gcr.io
```

---

## Step 3: Clone and Configure the Project

### Get the Project Files

If the project is in a Git repository:
```bash
git clone <repository-url>
cd red-team-demo
```

Or if you have the files locally:
```bash
cd /path/to/red-team-demo
```

### Make Scripts Executable

```bash
chmod +x deploy/deploy.sh
chmod +x deploy/test-local.sh
chmod +x deploy/cleanup.sh
```

### Configure Environment Variables (Optional)

```bash
# Set your GCP project ID (if different from yc-hack-org)
export GCP_PROJECT="your-project-id"

# Set region (default: us-central1)
export GCP_REGION="us-central1"
```

You can add these to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export GCP_PROJECT="your-project-id"' >> ~/.bashrc
echo 'export GCP_REGION="us-central1"' >> ~/.bashrc
source ~/.bashrc
```

### Install Python Dependencies

```bash
# For the exploit script
pip install requests

# Or use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests
```

---

## Step 4: Verify Setup

### Test Docker

```bash
# Pull a test image
docker pull hello-world

# Run it
docker run hello-world
```

### Test GCP Authentication

```bash
# Check current account
gcloud auth list

# Check current project
gcloud config get-value project

# Test API access
gcloud run services list --region=us-central1
```

### Test Local Build

```bash
# Build the vulnerable application
cd red-team-demo
./deploy/test-local.sh --no-test

# This should build the Docker image without errors
```

---

## Troubleshooting

### Docker Permission Denied

**Error:** `Got permission denied while trying to connect to the Docker daemon`

**Solution:**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### GCloud Not Found

**Error:** `gcloud: command not found`

**Solution:**
```bash
# Add to PATH (adjust path as needed)
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Or reinstall and follow the prompts
./google-cloud-sdk/install.sh
```

### API Not Enabled

**Error:** `PERMISSION_DENIED: Cloud Run API has not been enabled`

**Solution:**
```bash
gcloud services enable run.googleapis.com
```

### Authentication Issues

**Error:** `Your default credentials were not found`

**Solution:**
```bash
gcloud auth application-default login
```

### Docker Build Failures

**Error:** Build fails during `apt-get install`

**Solution:**
```bash
# If behind a proxy, configure Docker
# Or try building without cache
docker build --no-cache -t vulnerable-ecommerce ./app
```

---

## Next Steps

Once setup is complete:

1. **Test Locally**: Run `./deploy/test-local.sh` to test the application
2. **Deploy**: Run `./deploy/deploy.sh` to deploy to GCP Cloud Run
3. **Exploit**: Run `python exploit/exploit.py <url>` to test the vulnerability
4. **Clean Up**: Run `./deploy/cleanup.sh` to remove resources

See [ATTACK-DEMO.md](ATTACK-DEMO.md) for a complete walkthrough.

---

## Security Reminders

⚠️ **Before deploying:**
- Ensure you have authorization to deploy vulnerable applications
- Never deploy to production GCP projects
- Always clean up resources after testing
- Monitor for any unexpected access during testing

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review GCP logs: `gcloud logging read`
3. Check Docker logs: `docker logs <container-name>`
4. Verify all prerequisites are installed correctly
