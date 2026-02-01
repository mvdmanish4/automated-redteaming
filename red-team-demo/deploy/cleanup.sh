#!/bin/bash
#
# GCP Resource Cleanup Script
# ===========================
# Removes all GCP resources created by the deployment script.
#
# Usage: ./cleanup.sh
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

print_banner() {
    echo -e "${YELLOW}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║   🧹 GCP RESOURCE CLEANUP SCRIPT 🧹                               ║"
    echo "║                                                                   ║"
    echo "║   This will remove all deployed resources from GCP               ║"
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

print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Confirm cleanup
confirm_cleanup() {
    print_step "CONFIRMATION"
    
    echo -e "${YELLOW}The following resources will be deleted:${NC}"
    echo ""
    echo -e "  • Cloud Run Service: ${CYAN}$SERVICE_NAME${NC}"
    echo -e "  • Container Images:  ${CYAN}$IMAGE_NAME${NC}"
    echo -e "  • Project:           ${CYAN}$GCP_PROJECT${NC}"
    echo -e "  • Region:            ${CYAN}$GCP_REGION${NC}"
    echo ""
    
    read -p "Are you sure you want to delete these resources? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleanup cancelled."
        exit 0
    fi
}

# Check if gcloud is configured
check_gcloud() {
    print_step "CHECKING CONFIGURATION"
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed."
        exit 1
    fi
    print_success "gcloud CLI found"
    
    # Set project
    gcloud config set project "$GCP_PROJECT" 2>/dev/null
    print_success "Project set to: $GCP_PROJECT"
}

# Delete Cloud Run service
delete_cloud_run() {
    print_step "DELETING CLOUD RUN SERVICE"
    
    # Check if service exists
    if gcloud run services describe "$SERVICE_NAME" \
        --platform managed \
        --region "$GCP_REGION" &> /dev/null; then
        
        print_info "Deleting service: $SERVICE_NAME"
        gcloud run services delete "$SERVICE_NAME" \
            --platform managed \
            --region "$GCP_REGION" \
            --quiet
        print_success "Cloud Run service deleted"
    else
        print_info "Cloud Run service does not exist (already deleted?)"
    fi
}

# Delete container images
delete_images() {
    print_step "DELETING CONTAINER IMAGES"
    
    print_info "Checking for images in GCR..."
    
    # List all image digests
    DIGESTS=$(gcloud container images list-tags "$IMAGE_NAME" \
        --format="get(digest)" 2>/dev/null || true)
    
    if [ -n "$DIGESTS" ]; then
        print_info "Found images to delete..."
        
        for digest in $DIGESTS; do
            print_info "Deleting: $IMAGE_NAME@$digest"
            gcloud container images delete "$IMAGE_NAME@$digest" \
                --force-delete-tags \
                --quiet 2>/dev/null || true
        done
        print_success "Container images deleted"
    else
        print_info "No images found in GCR (already deleted?)"
    fi
}

# Clean up local resources
cleanup_local() {
    print_step "CLEANING UP LOCAL RESOURCES"
    
    # Remove deployment info file
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    INFO_FILE="$SCRIPT_DIR/deployment-info.txt"
    
    if [ -f "$INFO_FILE" ]; then
        rm "$INFO_FILE"
        print_success "Removed deployment-info.txt"
    else
        print_info "No deployment-info.txt found"
    fi
    
    # Clean up local Docker images (optional)
    print_info "Checking for local Docker images..."
    
    if docker images "$IMAGE_NAME" --format "{{.ID}}" 2>/dev/null | head -n 1 | grep -q .; then
        read -p "Remove local Docker image? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker rmi "$IMAGE_NAME" 2>/dev/null || true
            print_success "Local Docker image removed"
        else
            print_info "Local Docker image kept"
        fi
    else
        print_info "No local Docker images found"
    fi
    
    # Stop any running local containers
    LOCAL_CONTAINER="vulnerable-ecommerce-test"
    if docker ps -a --format '{{.Names}}' | grep -q "^${LOCAL_CONTAINER}$"; then
        print_info "Found local test container..."
        read -p "Stop and remove local test container? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker stop "$LOCAL_CONTAINER" 2>/dev/null || true
            docker rm "$LOCAL_CONTAINER" 2>/dev/null || true
            print_success "Local test container removed"
        else
            print_info "Local test container kept"
        fi
    fi
}

# Print summary
print_summary() {
    print_step "CLEANUP COMPLETE"
    
    echo -e "${GREEN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║               ✅ CLEANUP COMPLETE ✅                              ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BOLD}Resources removed:${NC}"
    echo "  • Cloud Run Service: $SERVICE_NAME"
    echo "  • Container Images from GCR"
    echo "  • Local deployment info file"
    echo ""
    echo -e "${CYAN}Thank you for using the Red Team Demo!${NC}"
}

# Main execution
main() {
    print_banner
    
    echo -e "${YELLOW}${BOLD}Configuration:${NC}"
    echo -e "  GCP Project: ${CYAN}$GCP_PROJECT${NC}"
    echo -e "  GCP Region:  ${CYAN}$GCP_REGION${NC}"
    echo -e "  Service:     ${CYAN}$SERVICE_NAME${NC}"
    echo ""
    
    confirm_cleanup
    check_gcloud
    delete_cloud_run
    delete_images
    cleanup_local
    print_summary
}

# Handle --force flag
if [[ "$1" == "--force" ]] || [[ "$1" == "-f" ]]; then
    print_banner
    check_gcloud
    delete_cloud_run
    delete_images
    cleanup_local
    print_summary
else
    main "$@"
fi
