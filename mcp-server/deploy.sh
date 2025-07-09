#!/bin/bash

# MCP Server Phase 6-3 Deployment Script
# Production-ready deployment automation

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$SCRIPT_DIR/.env"
DOCKER_COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
KUBE_MANIFESTS_DIR="$SCRIPT_DIR/k8s"
HELM_CHART_DIR="$SCRIPT_DIR/helm"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND

Commands:
    docker          Deploy using Docker Compose
    kubernetes      Deploy using Kubernetes manifests
    helm            Deploy using Helm chart
    test            Run deployment tests
    cleanup         Clean up deployment resources
    status          Check deployment status
    logs            View deployment logs
    help            Show this help message

Options:
    -e, --environment ENV    Environment (development, staging, production)
    -n, --namespace NS       Kubernetes namespace
    -c, --config FILE        Configuration file
    -v, --verbose            Verbose output
    -h, --help               Show help

Examples:
    $0 docker -e production
    $0 kubernetes -n mcp-server-prod
    $0 helm -e staging
    $0 test -e production
    $0 cleanup -n mcp-server-staging

EOF
}

# Function to validate environment
validate_environment() {
    local env_file="$1"
    
    log_info "Validating environment configuration..."
    
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        log_info "Please copy .env.example to .env and configure it"
        return 1
    fi
    
    # Source environment file
    source "$env_file"
    
    # Check required variables
    local required_vars=(
        "JWT_SECRET"
        "ADMIN_USERNAME"
        "ADMIN_PASSWORD"
        "BACKEND_API_URL"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "Required environment variable $var is not set"
            return 1
        fi
    done
    
    # Validate JWT secret strength
    if [[ ${#JWT_SECRET} -lt 32 ]]; then
        log_error "JWT_SECRET must be at least 32 characters long"
        return 1
    fi
    
    log_success "Environment validation passed"
    return 0
}

# Function to check prerequisites
check_prerequisites() {
    local deployment_type="$1"
    
    log_info "Checking prerequisites for $deployment_type deployment..."
    
    case "$deployment_type" in
        docker)
            if ! command -v docker &> /dev/null; then
                log_error "Docker is not installed"
                return 1
            fi
            if ! command -v docker-compose &> /dev/null; then
                log_error "Docker Compose is not installed"
                return 1
            fi
            ;;
        kubernetes)
            if ! command -v kubectl &> /dev/null; then
                log_error "kubectl is not installed"
                return 1
            fi
            if ! kubectl cluster-info &> /dev/null; then
                log_error "kubectl is not configured or cluster is not accessible"
                return 1
            fi
            ;;
        helm)
            if ! command -v helm &> /dev/null; then
                log_error "Helm is not installed"
                return 1
            fi
            if ! command -v kubectl &> /dev/null; then
                log_error "kubectl is not installed"
                return 1
            fi
            if ! kubectl cluster-info &> /dev/null; then
                log_error "kubectl is not configured or cluster is not accessible"
                return 1
            fi
            ;;
    esac
    
    log_success "Prerequisites check passed"
    return 0
}

# Function to build Docker image
build_docker_image() {
    local tag="$1"
    
    log_info "Building Docker image with tag: $tag"
    
    cd "$SCRIPT_DIR"
    docker build -t "$tag" -f Dockerfile .
    
    if [[ $? -eq 0 ]]; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        return 1
    fi
}

# Function to deploy with Docker Compose
deploy_docker() {
    local environment="$1"
    
    log_info "Deploying with Docker Compose (environment: $environment)"
    
    # Validate environment
    if ! validate_environment "$ENV_FILE"; then
        return 1
    fi
    
    # Check prerequisites
    if ! check_prerequisites "docker"; then
        return 1
    fi
    
    # Build image
    local image_tag="mcp-server:phase6-3-$environment"
    build_docker_image "$image_tag"
    
    # Deploy with Docker Compose
    cd "$SCRIPT_DIR"
    docker-compose --env-file "$ENV_FILE" up -d
    
    if [[ $? -eq 0 ]]; then
        log_success "Docker deployment completed successfully"
        
        # Wait for services to be ready
        log_info "Waiting for services to be ready..."
        sleep 30
        
        # Run health checks
        run_health_checks "docker"
    else
        log_error "Docker deployment failed"
        return 1
    fi
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    local namespace="$1"
    local environment="$2"
    
    log_info "Deploying with Kubernetes (namespace: $namespace, environment: $environment)"
    
    # Check prerequisites
    if ! check_prerequisites "kubernetes"; then
        return 1
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply manifests
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f "$KUBE_MANIFESTS_DIR/namespace.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/rbac.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/configmap.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/secret.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/pvc.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/deployment.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/service.yaml"
    kubectl apply -f "$KUBE_MANIFESTS_DIR/ingress.yaml"
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available deployment/mcp-server -n "$namespace" --timeout=300s
    
    if [[ $? -eq 0 ]]; then
        log_success "Kubernetes deployment completed successfully"
        
        # Run health checks
        run_health_checks "kubernetes" "$namespace"
    else
        log_error "Kubernetes deployment failed"
        return 1
    fi
}

# Function to deploy with Helm
deploy_helm() {
    local namespace="$1"
    local environment="$2"
    
    log_info "Deploying with Helm (namespace: $namespace, environment: $environment)"
    
    # Check prerequisites
    if ! check_prerequisites "helm"; then
        return 1
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy with Helm
    cd "$HELM_CHART_DIR"
    helm upgrade --install mcp-server . \
        --namespace "$namespace" \
        --set global.environment="$environment" \
        --set mcpServer.image.tag="phase6-3-$environment" \
        --wait --timeout=10m
    
    if [[ $? -eq 0 ]]; then
        log_success "Helm deployment completed successfully"
        
        # Run health checks
        run_health_checks "helm" "$namespace"
    else
        log_error "Helm deployment failed"
        return 1
    fi
}

# Function to run health checks
run_health_checks() {
    local deployment_type="$1"
    local namespace="$2"
    
    log_info "Running health checks for $deployment_type deployment..."
    
    case "$deployment_type" in
        docker)
            # Check Docker container health
            if docker ps --filter "name=mcp-server" --filter "status=running" | grep -q mcp-server; then
                log_success "MCP Server container is running"
            else
                log_error "MCP Server container is not running"
                return 1
            fi
            
            # Check health endpoint
            if curl -f http://localhost:8003/mcp/system/health &> /dev/null; then
                log_success "Health endpoint is responding"
            else
                log_error "Health endpoint is not responding"
                return 1
            fi
            ;;
        kubernetes|helm)
            # Check pod status
            if kubectl get pods -n "$namespace" -l app=mcp-server | grep -q Running; then
                log_success "MCP Server pods are running"
            else
                log_error "MCP Server pods are not running"
                return 1
            fi
            
            # Check service
            if kubectl get service mcp-server-service -n "$namespace" &> /dev/null; then
                log_success "MCP Server service is available"
            else
                log_error "MCP Server service is not available"
                return 1
            fi
            ;;
    esac
    
    log_success "Health checks passed"
}

# Function to run tests
run_tests() {
    local environment="$1"
    
    log_info "Running deployment tests for $environment environment..."
    
    # API tests
    log_info "Running API tests..."
    
    # Test health endpoint
    if curl -f http://localhost:8003/mcp/system/health &> /dev/null; then
        log_success "Health endpoint test passed"
    else
        log_error "Health endpoint test failed"
        return 1
    fi
    
    # Test metrics endpoint
    if curl -f http://localhost:8003/metrics &> /dev/null; then
        log_success "Metrics endpoint test passed"
    else
        log_error "Metrics endpoint test failed"
        return 1
    fi
    
    # Test authentication
    local auth_response=$(curl -s -X POST http://localhost:8003/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "'"$ADMIN_PASSWORD"'"}')
    
    if echo "$auth_response" | grep -q "access_token"; then
        log_success "Authentication test passed"
    else
        log_error "Authentication test failed"
        return 1
    fi
    
    log_success "All tests passed"
}

# Function to clean up resources
cleanup() {
    local deployment_type="$1"
    local namespace="$2"
    
    log_info "Cleaning up $deployment_type deployment..."
    
    case "$deployment_type" in
        docker)
            docker-compose down -v
            docker image prune -f
            ;;
        kubernetes)
            kubectl delete namespace "$namespace" --ignore-not-found=true
            ;;
        helm)
            helm uninstall mcp-server -n "$namespace"
            kubectl delete namespace "$namespace" --ignore-not-found=true
            ;;
    esac
    
    log_success "Cleanup completed"
}

# Function to show deployment status
show_status() {
    local deployment_type="$1"
    local namespace="$2"
    
    log_info "Showing deployment status for $deployment_type..."
    
    case "$deployment_type" in
        docker)
            echo "=== Docker Containers ==="
            docker ps --filter "name=mcp-server"
            echo
            echo "=== Docker Images ==="
            docker images | grep mcp-server
            ;;
        kubernetes|helm)
            echo "=== Pods ==="
            kubectl get pods -n "$namespace" -l app=mcp-server
            echo
            echo "=== Services ==="
            kubectl get services -n "$namespace"
            echo
            echo "=== Ingress ==="
            kubectl get ingress -n "$namespace"
            ;;
    esac
}

# Function to show logs
show_logs() {
    local deployment_type="$1"
    local namespace="$2"
    
    log_info "Showing logs for $deployment_type deployment..."
    
    case "$deployment_type" in
        docker)
            docker-compose logs -f mcp-server
            ;;
        kubernetes|helm)
            kubectl logs -f -l app=mcp-server -n "$namespace"
            ;;
    esac
}

# Main function
main() {
    local command=""
    local environment="development"
    local namespace="mcp-server"
    local config_file="$ENV_FILE"
    local verbose=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                environment="$2"
                shift 2
                ;;
            -n|--namespace)
                namespace="$2"
                shift 2
                ;;
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            docker|kubernetes|helm|test|cleanup|status|logs|help)
                command="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Validate command
    if [[ -z "$command" ]]; then
        log_error "No command specified"
        show_usage
        exit 1
    fi
    
    # Set verbose mode
    if [[ "$verbose" == true ]]; then
        set -x
    fi
    
    # Execute command
    case "$command" in
        docker)
            deploy_docker "$environment"
            ;;
        kubernetes)
            deploy_kubernetes "$namespace" "$environment"
            ;;
        helm)
            deploy_helm "$namespace" "$environment"
            ;;
        test)
            run_tests "$environment"
            ;;
        cleanup)
            cleanup "docker" "$namespace"
            cleanup "kubernetes" "$namespace"
            cleanup "helm" "$namespace"
            ;;
        status)
            show_status "docker" "$namespace"
            show_status "kubernetes" "$namespace"
            ;;
        logs)
            show_logs "docker" "$namespace"
            ;;
        help)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"