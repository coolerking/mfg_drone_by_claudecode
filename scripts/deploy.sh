#!/bin/bash

# MFG Drone System - Production Deployment Script
# This script automates the deployment process for the MFG Drone System

set -euo pipefail

# Configuration
PROJECT_NAME="mfg-drone"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy_$(date +%Y%m%d_%H%M%S).log"
MAX_RETRIES=3
HEALTH_CHECK_TIMEOUT=300

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    echo -e "${level}[$(date +'%Y-%m-%d %H:%M:%S')] $*${NC}" | tee -a "$LOG_FILE"
}

info() { log "$BLUE" "INFO: $*"; }
warn() { log "$YELLOW" "WARN: $*"; }
error() { log "$RED" "ERROR: $*"; }
success() { log "$GREEN" "SUCCESS: $*"; }

# Error handling
cleanup() {
    if [[ $? -ne 0 ]]; then
        error "Deployment failed! Check logs at $LOG_FILE"
        error "You may need to restore from backup or manually fix issues"
    fi
}
trap cleanup EXIT

# Pre-deployment checks
check_requirements() {
    info "Checking system requirements..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Set Docker Compose command
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    # Check available disk space (minimum 5GB)
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 5242880 ]]; then # 5GB in KB
        error "Insufficient disk space. At least 5GB required"
        exit 1
    fi
    
    # Check if environment file exists
    if [[ ! -f ".env.production" ]]; then
        error ".env.production file not found"
        error "Please copy and configure .env.production from the template"
        exit 1
    fi
    
    # Check for required environment variables
    source .env.production
    required_vars=(
        "DB_PASSWORD"
        "JWT_SECRET"
        "GRAFANA_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    success "Requirements check passed"
}

# Backup current deployment
backup_current_deployment() {
    info "Creating backup of current deployment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup database if running
    if $DOCKER_COMPOSE -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        info "Backing up PostgreSQL database..."
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" exec -T postgres pg_dump -U mfg_user mfg_drone_db > "$backup_path/database.sql" || warn "Database backup failed"
    fi
    
    # Backup volumes
    info "Backing up Docker volumes..."
    for volume in postgres_data redis_data grafana_data prometheus_data; do
        if docker volume ls | grep -q "${PROJECT_NAME}_${volume}"; then
            docker run --rm -v "${PROJECT_NAME}_${volume}:/source" -v "$(pwd)/$backup_path:/backup" alpine tar czf "/backup/${volume}.tar.gz" -C /source . || warn "Volume backup failed for $volume"
        fi
    done
    
    # Backup configuration files
    info "Backing up configuration files..."
    cp -r monitoring "$backup_path/" 2>/dev/null || warn "Monitoring config backup failed"
    cp .env.production "$backup_path/" 2>/dev/null || warn "Environment file backup failed"
    
    success "Backup created at $backup_path"
    echo "$backup_path" > "$BACKUP_DIR/latest_backup.txt"
}

# Pull latest images
pull_images() {
    info "Pulling latest Docker images..."
    
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" pull
    
    success "Images pulled successfully"
}

# Build custom images
build_images() {
    info "Building custom Docker images..."
    
    # Build frontend
    cd frontend
    info "Building frontend image..."
    docker build --target production -t mfg-drone-frontend:latest .
    cd ..
    
    # Build backend
    cd backend
    info "Building backend image..."
    docker build -t mfg-drone-backend:latest .
    cd ..
    
    success "Custom images built successfully"
}

# Deploy services
deploy_services() {
    info "Deploying services..."
    
    # Create external networks if they don't exist
    docker network create mfg-drone-network 2>/dev/null || true
    
    # Start services with zero-downtime deployment
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d --remove-orphans
    
    success "Services deployed"
}

# Health checks
wait_for_services() {
    info "Waiting for services to become healthy..."
    
    local services=("frontend" "backend" "postgres" "redis")
    local timeout=$HEALTH_CHECK_TIMEOUT
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        local all_healthy=true
        
        for service in "${services[@]}"; do
            local status=$($DOCKER_COMPOSE -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.Status}}" | grep "$service" | awk '{print $2}' || echo "")
            
            if [[ "$status" != "healthy" ]] && [[ "$status" != "Up" ]]; then
                all_healthy=false
                break
            fi
        done
        
        if $all_healthy; then
            success "All services are healthy"
            return 0
        fi
        
        info "Services still starting... ($elapsed/$timeout seconds)"
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    error "Services failed to become healthy within $timeout seconds"
    return 1
}

# Verify deployment
verify_deployment() {
    info "Verifying deployment..."
    
    # Check frontend
    if ! curl -f http://localhost/health &>/dev/null; then
        error "Frontend health check failed"
        return 1
    fi
    
    # Check backend
    if ! curl -f http://localhost:8000/health &>/dev/null; then
        error "Backend health check failed"
        return 1
    fi
    
    # Check metrics endpoints
    if ! curl -f http://localhost:9090 &>/dev/null; then
        warn "Prometheus not accessible"
    fi
    
    if ! curl -f http://localhost:3001 &>/dev/null; then
        warn "Grafana not accessible"
    fi
    
    success "Deployment verification passed"
}

# Cleanup old resources
cleanup_old_resources() {
    info "Cleaning up old resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    # Remove old backups (keep last 7 days)
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -type d -name "backup_*" -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
    fi
    
    success "Cleanup completed"
}

# Rollback function
rollback() {
    error "Rolling back to previous deployment..."
    
    if [[ -f "$BACKUP_DIR/latest_backup.txt" ]]; then
        local backup_path=$(cat "$BACKUP_DIR/latest_backup.txt")
        
        if [[ -d "$backup_path" ]]; then
            info "Restoring from backup: $backup_path"
            
            # Stop current services
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
            
            # Restore database
            if [[ -f "$backup_path/database.sql" ]]; then
                info "Restoring database..."
                $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d postgres
                sleep 10
                cat "$backup_path/database.sql" | $DOCKER_COMPOSE -f "$COMPOSE_FILE" exec -T postgres psql -U mfg_user -d mfg_drone_db
            fi
            
            # Restore volumes
            for volume_backup in "$backup_path"/*.tar.gz; do
                if [[ -f "$volume_backup" ]]; then
                    local volume_name=$(basename "$volume_backup" .tar.gz)
                    info "Restoring volume: $volume_name"
                    docker run --rm -v "${PROJECT_NAME}_${volume_name}:/target" -v "$backup_path:/backup" alpine tar xzf "/backup/${volume_name}.tar.gz" -C /target
                fi
            done
            
            # Restart services
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d
            
            success "Rollback completed"
        else
            error "Backup directory not found: $backup_path"
        fi
    else
        error "No backup information found"
    fi
}

# Main deployment function
main_deploy() {
    info "Starting deployment of MFG Drone System..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    check_requirements
    backup_current_deployment
    pull_images
    build_images
    deploy_services
    
    if wait_for_services; then
        verify_deployment
        cleanup_old_resources
        success "Deployment completed successfully!"
        
        info "Services available at:"
        info "  - Frontend: http://localhost"
        info "  - Backend API: http://localhost:8000"
        info "  - Prometheus: http://localhost:9090"
        info "  - Grafana: http://localhost:3001 (admin/[GRAFANA_PASSWORD])"
        
    else
        error "Deployment failed during health checks"
        
        # Ask for rollback
        read -p "Do you want to rollback? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rollback
        fi
        exit 1
    fi
}

# Script entry point
case "${1:-deploy}" in
    deploy)
        main_deploy
        ;;
    rollback)
        rollback
        ;;
    backup)
        check_requirements
        backup_current_deployment
        ;;
    verify)
        verify_deployment
        ;;
    logs)
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" logs -f
        ;;
    status)
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" ps
        ;;
    stop)
        info "Stopping services..."
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
        success "Services stopped"
        ;;
    restart)
        info "Restarting services..."
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" restart
        success "Services restarted"
        ;;
    cleanup)
        cleanup_old_resources
        ;;
    help)
        echo "Usage: $0 [command]"
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  rollback - Rollback to previous version"
        echo "  backup   - Create backup only"
        echo "  verify   - Verify current deployment"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  cleanup  - Cleanup old resources"
        echo "  help     - Show this help"
        ;;
    *)
        error "Unknown command: $1"
        $0 help
        exit 1
        ;;
esac