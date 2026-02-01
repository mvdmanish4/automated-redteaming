#!/bin/bash
#
# Local Testing Script
# ====================
# Tests the vulnerable application locally using Docker
# before deploying to GCP Cloud Run.
#
# Usage: ./test-local.sh
#

set -e

# Configuration
CONTAINER_NAME="vulnerable-ecommerce-test"
IMAGE_NAME="vulnerable-ecommerce-local"
HOST_PORT=8080
CONTAINER_PORT=8080

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║   🧪 LOCAL TESTING SCRIPT 🧪                                      ║"
    echo "║                                                                   ║"
    echo "║   Test the vulnerable application locally before deployment      ║"
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

# Cleanup function
cleanup() {
    print_step "CLEANUP"
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Stopping and removing container..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        print_success "Container removed"
    else
        print_info "No container to clean up"
    fi
}

# Check prerequisites
check_prerequisites() {
    print_step "CHECKING PREREQUISITES"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed."
        exit 1
    fi
    print_success "Docker found"
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running."
        exit 1
    fi
    print_success "Docker daemon is running"
    
    if ! command -v curl &> /dev/null; then
        print_warning "curl not found - endpoint testing will be skipped"
    else
        print_success "curl found"
    fi
}

# Build the image
build_image() {
    print_step "BUILDING DOCKER IMAGE"
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    APP_DIR="$SCRIPT_DIR/../app"
    
    if [ ! -f "$APP_DIR/Dockerfile" ]; then
        print_error "Dockerfile not found at $APP_DIR/Dockerfile"
        exit 1
    fi
    
    print_info "Building image: $IMAGE_NAME"
    docker build -t "$IMAGE_NAME" "$APP_DIR"
    print_success "Image built successfully"
}

# Run the container
run_container() {
    print_step "STARTING CONTAINER"
    
    # Remove existing container if it exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Removing existing container..."
        docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
    fi
    
    print_info "Starting container on port $HOST_PORT..."
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$HOST_PORT:$CONTAINER_PORT" \
        -e ENVIRONMENT=development \
        "$IMAGE_NAME"
    
    print_success "Container started: $CONTAINER_NAME"
    
    # Wait for container to be ready
    print_info "Waiting for application to start..."
    sleep 3
}

# Test endpoints
test_endpoints() {
    print_step "TESTING ENDPOINTS"
    
    BASE_URL="http://localhost:$HOST_PORT"
    
    # Test home page
    print_info "Testing GET /..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET / returned $HTTP_CODE"
    else
        print_error "GET / returned $HTTP_CODE"
    fi
    
    # Test health endpoint
    print_info "Testing GET /health..."
    RESPONSE=$(curl -s "$BASE_URL/health")
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /health returned $HTTP_CODE"
        echo -e "  Response: ${CYAN}$RESPONSE${NC}"
    else
        print_error "GET /health returned $HTTP_CODE"
    fi
    
    # Test products endpoint
    print_info "Testing GET /products..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/products")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /products returned $HTTP_CODE"
    else
        print_error "GET /products returned $HTTP_CODE"
    fi
    
    # Test search endpoint
    print_info "Testing GET /search?q=coffee..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/search?q=coffee")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /search returned $HTTP_CODE"
    else
        print_error "GET /search returned $HTTP_CODE"
    fi
    
    # Test ping endpoint (normal)
    print_info "Testing GET /ping?host=localhost..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/ping?host=localhost")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /ping returned $HTTP_CODE"
    else
        print_warning "GET /ping returned $HTTP_CODE (may be expected)"
    fi
    
    # Test command injection
    print_step "TESTING VULNERABILITY"
    
    print_warning "Testing command injection vulnerability..."
    
    # URL encode the payload
    PAYLOAD="localhost;whoami"
    ENCODED_PAYLOAD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PAYLOAD'))")
    
    print_info "Payload: $PAYLOAD"
    RESPONSE=$(curl -s "$BASE_URL/ping?host=$ENCODED_PAYLOAD")
    
    if echo "$RESPONSE" | grep -q "appuser\|root\|www-data"; then
        print_success "Command injection successful!"
        echo -e "  ${RED}⚠️ Application is VULNERABLE to command injection${NC}"
    else
        print_warning "Could not confirm vulnerability (check response manually)"
    fi
    echo -e "  Response: ${CYAN}${RESPONSE:0:200}...${NC}"
}

# Print summary
print_summary() {
    print_step "TEST SUMMARY"
    
    echo -e "${GREEN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                   ║"
    echo "║               ✅ LOCAL TESTING COMPLETE ✅                        ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}Local URL:${NC}     ${YELLOW}http://localhost:$HOST_PORT${NC}"
    echo -e "${CYAN}Container:${NC}     $CONTAINER_NAME"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo -e "  1. Test manually: ${YELLOW}curl http://localhost:$HOST_PORT/health${NC}"
    echo -e "  2. Run exploit:   ${YELLOW}python exploit/exploit.py http://localhost:$HOST_PORT${NC}"
    echo -e "  3. View logs:     ${YELLOW}docker logs $CONTAINER_NAME${NC}"
    echo -e "  4. Stop test:     ${YELLOW}docker stop $CONTAINER_NAME${NC}"
    echo ""
    echo -e "${BOLD}To deploy to GCP Cloud Run:${NC}"
    echo -e "  ${YELLOW}./deploy.sh${NC}"
}

# Show usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --cleanup    Only clean up (stop and remove container)"
    echo "  --no-test    Build and run without testing endpoints"
    echo "  --help       Show this help message"
}

# Main execution
main() {
    # Handle trap for cleanup on exit
    trap cleanup EXIT
    
    # Parse arguments
    CLEANUP_ONLY=false
    NO_TEST=false
    
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --cleanup) CLEANUP_ONLY=true ;;
            --no-test) NO_TEST=true ;;
            --help) usage; exit 0 ;;
            *) echo "Unknown option: $1"; usage; exit 1 ;;
        esac
        shift
    done
    
    print_banner
    
    if [ "$CLEANUP_ONLY" = true ]; then
        cleanup
        exit 0
    fi
    
    # Remove trap since we want to keep container running
    trap - EXIT
    
    check_prerequisites
    build_image
    run_container
    
    if [ "$NO_TEST" = false ]; then
        test_endpoints
    fi
    
    print_summary
}

main "$@"
