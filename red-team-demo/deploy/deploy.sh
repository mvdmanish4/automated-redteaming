#!/bin/bash
#
# GCP Cloud Run Deployment Script
# ================================
# ⚠️ WARNING: This deploys an INTENTIONALLY VULNERABLE application
# ⚠️ FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY
#
# Usage: ./deploy.sh
#

set -e

# Configuration
GCP_PROJECT="${GCP_PROJECT:-yc-hack-org}"
GCP_REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="vulnerable-ecommerce"
IMAGE_NAME="gcr.io/${GCP_PROJECT}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Print functions
print_banner() {
    echo -e "${RED}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║   🚀 VULNERABLE E-COMMERCE DEPLOYMENT SCRIPT 🚀                   ║"
    echo "║                                                                   ║"
    echo "║   ⚠️  WARNING: INTENTIONALLY VULNERABLE APPLICATION ⚠️             ║"
    echo "║   FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY           ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${BOLD}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "CHECKING PREREQUISITES"
    
    # Check for gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed."
        echo ""
        echo "Please install the Google Cloud SDK:"
        echo "  https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI found: $(gcloud --version | head -n 1)"
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed."
        echo ""
        echo "Please install Docker:"
        echo "  https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_success "Docker daemon is running"
}

# Authenticate with GCP
authenticate_gcp() {
    print_step "GCP AUTHENTICATION"
    
    # Check if already authenticated
    CURRENT_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
    
    if [ -z "$CURRENT_ACCOUNT" ]; then
        print_warning "Not authenticated with GCP. Starting authentication..."
        gcloud auth login
    else
        print_success "Already authenticated as: $CURRENT_ACCOUNT"
    fi
    
    # Set project
    print_info "Setting project to: $GCP_PROJECT"
    gcloud config set project "$GCP_PROJECT"
    print_success "Project set to: $GCP_PROJECT"
    
    # Configure Docker for GCR
    print_info "Configuring Docker for Google Container Registry..."
    gcloud auth configure-docker gcr.io --quiet
    print_success "Docker configured for GCR"
}

# Enable required APIs
enable_apis() {
    print_step "ENABLING REQUIRED APIs"
    
    APIS=(
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "cloudbuild.googleapis.com"
    )
    
    for api in "${APIS[@]}"; do
        print_info "Enabling $api..."
        gcloud services enable "$api" --quiet
        print_success "Enabled: $api"
    done
}

# Build Docker image
build_image() {
    print_step "BUILDING DOCKER IMAGE"
    
    # Get the script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    APP_DIR="$SCRIPT_DIR/../app"
    
    if [ ! -f "$APP_DIR/Dockerfile" ]; then
        print_error "Dockerfile not found at $APP_DIR/Dockerfile"
        exit 1
    fi
    
    print_info "Building image from: $APP_DIR"
    print_info "Image name: $IMAGE_NAME"
    
    docker build -t "$IMAGE_NAME" "$APP_DIR"
    
    print_success "Docker image built successfully"
}

# Push image to GCR
push_image() {
    print_step "PUSHING IMAGE TO GOOGLE CONTAINER REGISTRY"
    
    print_info "Pushing: $IMAGE_NAME"
    docker push "$IMAGE_NAME"
    
    print_success "Image pushed to GCR"
}

# Deploy to Cloud Run
deploy_cloud_run() {
    print_step "DEPLOYING TO CLOUD RUN"
    
    print_info "Service name: $SERVICE_NAME"
    print_info "Region: $GCP_REGION"
    print_info "Image: $IMAGE_NAME"
    
    print_warning "Deploying with --allow-unauthenticated (publicly accessible)"
    
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_NAME" \
        --platform managed \
        --region "$GCP_REGION" \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 3 \
        --port 8080 \
        --set-env-vars "ENVIRONMENT=production"
    
    print_success "Cloud Run deployment complete"
}

# Get service URL
get_service_url() {
    print_step "DEPLOYMENT INFORMATION"
    
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$GCP_REGION" \
        --format "value(status.url)")
    
    # Save deployment info
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    INFO_FILE="$SCRIPT_DIR/deployment-info.txt"
    
    cat > "$INFO_FILE" << EOF
================================================================================
                    VULNERABLE E-COMMERCE DEPLOYMENT INFO
================================================================================
Deployment Time: $(date)
================================================================================

Service URL:  $SERVICE_URL
Project:      $GCP_PROJECT
Region:       $GCP_REGION
Service Name: $SERVICE_NAME
Image:        $IMAGE_NAME

================================================================================
                              EXPLOIT COMMAND
================================================================================

python exploit/exploit.py $SERVICE_URL

================================================================================
                              CLEANUP COMMAND
================================================================================

./deploy/cleanup.sh

================================================================================
EOF
    
    print_success "Deployment info saved to: $INFO_FILE"
    
    echo -e "\n${GREEN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║               ✅ DEPLOYMENT COMPLETE! ✅                          ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}Service URL:${NC}  ${YELLOW}${BOLD}$SERVICE_URL${NC}"
    echo -e "${CYAN}Project:${NC}      $GCP_PROJECT"
    echo -e "${CYAN}Region:${NC}       $GCP_REGION"
    echo ""
    echo -e "${BOLD}To exploit, run:${NC}"
    echo -e "${YELLOW}  python exploit/exploit.py $SERVICE_URL${NC}"
    echo ""
    echo -e "${BOLD}To cleanup, run:${NC}"
    echo -e "${YELLOW}  ./deploy/cleanup.sh${NC}"
    echo ""
    
    # Test the deployment
    print_info "Testing deployment..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Health check passed! Service is ready."
    else
        print_warning "Health check returned HTTP $HTTP_CODE"
    fi
}

# Main execution
main() {
    print_banner
    
    echo -e "${YELLOW}${BOLD}Configuration:${NC}"
    echo -e "  GCP Project: ${CYAN}$GCP_PROJECT${NC}"
    echo -e "  GCP Region:  ${CYAN}$GCP_REGION${NC}"
    echo -e "  Service:     ${CYAN}$SERVICE_NAME${NC}"
    echo ""
    
    check_prerequisites
    authenticate_gcp
    enable_apis
    build_image
    push_image
    deploy_cloud_run
    get_service_url
}

# Run main function
main "$@"
