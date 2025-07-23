#!/bin/bash

# 統一デプロイスクリプト - MFG Drone System (Node.js MCP中心)
# Phase F: 監視・運用設定の統合

set -euo pipefail

# =============================================================================
# 設定
# =============================================================================

# プロジェクト設定
PROJECT_NAME="mfg-drone-unified"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION="phase-f-$(date +%Y%m%d-%H%M%S)"

# 環境設定
ENVIRONMENT="${ENVIRONMENT:-production}"
NODE_ENV="${NODE_ENV:-production}"
DEPLOY_MODE="${DEPLOY_MODE:-full}"  # full, nodejs-only, backend-only

# ファイルパス
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups"
LOG_DIR="./logs"
MONITORING_DIR="./monitoring"

# デプロイログ
DEPLOY_LOG="$LOG_DIR/deploy_$(date +%Y%m%d_%H%M%S).log"
MAX_RETRIES=3
HEALTH_CHECK_TIMEOUT=300

# Node.js MCP Server設定（最優先）
MCP_NODEJS_PORT="${MCP_NODEJS_PORT:-3001}"
MCP_NODEJS_SERVICE="mcp-server-nodejs"
MCP_NODEJS_IMAGE="mfg-drone-mcp-nodejs:$VERSION"

# =============================================================================
# カラーとロギング
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    local level=$1
    local color=$2
    shift 2
    echo -e "${color}[$(date +'%Y-%m-%d %H:%M:%S')] [$level]${NC} $*" | tee -a "$DEPLOY_LOG"
}

info() { log "INFO" "$BLUE" "$*"; }
warn() { log "WARN" "$YELLOW" "$*"; }
error() { log "ERROR" "$RED" "$*"; }
success() { log "SUCCESS" "$GREEN" "$*"; }
debug() { log "DEBUG" "$PURPLE" "$*"; }

# =============================================================================
# エラーハンドリング
# =============================================================================

cleanup_on_error() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        error "デプロイに失敗しました（終了コード: $exit_code）"
        error "ログファイル: $DEPLOY_LOG"
        
        # ロールバック確認
        if [[ -f "$BACKUP_DIR/latest_backup.txt" ]]; then
            warn "最新のバックアップからロールバックしますか？ (y/N)"
            read -p "選択: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                perform_rollback
            fi
        fi
    fi
}
trap cleanup_on_error EXIT

# =============================================================================
# 前提条件チェック
# =============================================================================

check_prerequisites() {
    info "前提条件をチェック中..."
    
    # 必要なコマンドの確認
    local required_commands=("docker" "node" "npm" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "必要なコマンドが見つかりません: $cmd"
            exit 1
        fi
    done
    
    # Docker Compose の確認
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        error "Docker Compose が見つかりません"
        exit 1
    fi
    
    # Docker デーモンの確認
    if ! docker info &> /dev/null; then
        error "Docker デーモンが起動していません"
        exit 1
    fi
    
    # ディスク容量の確認（最低10GB）
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then  # 10GB in KB
        error "ディスク容量が不足しています（最低10GB必要）"
        exit 1
    fi
    
    # 環境ファイルの確認
    if [[ ! -f "$PROJECT_ROOT/$ENV_FILE" ]]; then
        error "環境設定ファイルが見つかりません: $ENV_FILE"
        error "テンプレートから$ENV_FILEを作成し、設定してください"
        exit 1
    fi
    
    # Node.js バージョンの確認
    local node_version=$(node --version | sed 's/v//')
    local required_node_version="18.0.0"
    if ! compare_versions "$node_version" "$required_node_version"; then
        error "Node.js バージョンが不足しています（必要: $required_node_version 以上, 現在: $node_version）"
        exit 1
    fi
    
    success "前提条件チェック完了"
}

# バージョン比較関数
compare_versions() {
    local version1=$1
    local version2=$2
    printf '%s\n%s\n' "$version1" "$version2" | sort -V -C
}

# =============================================================================
# 統一監視設定の適用
# =============================================================================

apply_unified_monitoring() {
    info "統一監視設定を適用中..."
    
    # 統一Prometheus設定の適用
    if [[ -f "$MONITORING_DIR/unified_prometheus.yml" ]]; then
        cp "$MONITORING_DIR/unified_prometheus.yml" "$MONITORING_DIR/prometheus.yml"
        success "統一Prometheus設定を適用しました"
    else
        warn "統一Prometheus設定ファイルが見つかりません"
    fi
    
    # 統一アラート設定の適用
    if [[ -f "$MONITORING_DIR/unified_alerts.yml" ]]; then
        cp "$MONITORING_DIR/unified_alerts.yml" "$MONITORING_DIR/alerts.yml"
        success "統一アラート設定を適用しました"
    else
        warn "統一アラート設定ファイルが見つかりません"
    fi
    
    # ログ設定ディレクトリの作成
    mkdir -p "$LOG_DIR"/{mcp-nodejs,backend,frontend,mcp-python,access,error,security,performance,audit}
    success "ログディレクトリを作成しました"
}

# =============================================================================
# Node.js MCP Server構築（最優先）
# =============================================================================

build_mcp_nodejs() {
    info "Node.js MCP Server を構築中..."
    
    cd "$PROJECT_ROOT/mcp-server-nodejs"
    
    # 依存関係のインストール
    info "Node.js依存関係をインストール中..."
    npm ci --production=false
    
    # TypeScriptビルド
    info "TypeScriptコードをビルド中..."
    npm run build
    
    # テスト実行（Node.js MCP Server）
    info "Node.js MCP Server テストを実行中..."
    npm test -- --passWithNoTests
    
    # Docker イメージ構築
    info "Node.js MCP Server Docker イメージを構築中..."
    docker build -t "$MCP_NODEJS_IMAGE" .
    
    success "Node.js MCP Server 構築完了"
    cd "$PROJECT_ROOT"
}

# =============================================================================
# その他のサービス構築
# =============================================================================

build_other_services() {
    if [[ "$DEPLOY_MODE" == "nodejs-only" ]]; then
        info "Node.js専用デプロイのため、他のサービスの構築をスキップします"
        return 0
    fi
    
    info "その他のサービスを構築中..."
    
    # Backend API
    if [[ -d "$PROJECT_ROOT/backend" ]]; then
        info "Backend API を構築中..."
        cd "$PROJECT_ROOT/backend"
        docker build -t "mfg-drone-backend:$VERSION" .
        cd "$PROJECT_ROOT"
    fi
    
    # Frontend
    if [[ -d "$PROJECT_ROOT/frontend" ]]; then
        info "Frontend を構築中..."
        cd "$PROJECT_ROOT/frontend"
        docker build --target production -t "mfg-drone-frontend:$VERSION" .
        cd "$PROJECT_ROOT"
    fi
    
    success "その他のサービス構築完了"
}

# =============================================================================
# バックアップ
# =============================================================================

create_backup() {
    info "現在のデプロイのバックアップを作成中..."
    
    mkdir -p "$BACKUP_DIR"
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    mkdir -p "$backup_path"
    
    # 設定ファイルのバックアップ
    cp -r "$MONITORING_DIR" "$backup_path/" 2>/dev/null || warn "監視設定のバックアップに失敗"
    cp "$ENV_FILE" "$backup_path/" 2>/dev/null || warn "環境設定のバックアップに失敗"
    
    # データベースバックアップ（実行中の場合）
    if $DOCKER_COMPOSE -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        info "PostgreSQLデータベースをバックアップ中..."
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" exec -T -e PGPASSWORD="$DB_PASSWORD" postgres pg_dump -U mfg_user mfg_drone_db > "$backup_path/database.sql" || warn "データベースバックアップに失敗"
    fi
    
    # Dockerボリュームのバックアップ
    local volumes=("postgres_data" "redis_data" "grafana_data" "prometheus_data")
    for volume in "${volumes[@]}"; do
        local volume_name="${PROJECT_NAME}_${volume}"
        if docker volume ls | grep -q "$volume_name"; then
            docker run --rm -v "$volume_name:/source" -v "$(pwd)/$backup_path:/backup" alpine tar czf "/backup/${volume}.tar.gz" -C /source . || warn "$volume のバックアップに失敗"
        fi
    done
    
    echo "$backup_path" > "$BACKUP_DIR/latest_backup.txt"
    success "バックアップを作成しました: $backup_path"
}

# =============================================================================
# デプロイ実行
# =============================================================================

deploy_services() {
    info "サービスをデプロイ中..."
    
    # 統一監視設定の適用
    apply_unified_monitoring
    
    # Docker ネットワークの作成
    docker network create mfg-drone-network 2>/dev/null || true
    
    # 環境変数の設定
    export MCP_NODEJS_IMAGE
    export VERSION
    export NODE_ENV
    
    # Node.js MCP Server優先デプロイ
    info "Node.js MCP Server を最優先でデプロイ中..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d $MCP_NODEJS_SERVICE
    
    # Node.js MCP Server のヘルスチェック
    wait_for_service "$MCP_NODEJS_SERVICE" "$MCP_NODEJS_PORT" "/health"
    
    # その他のサービスのデプロイ
    if [[ "$DEPLOY_MODE" != "nodejs-only" ]]; then
        info "その他のサービスをデプロイ中..."
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d --remove-orphans
    fi
    
    success "サービスデプロイ完了"
}

# =============================================================================
# ヘルスチェック
# =============================================================================

wait_for_service() {
    local service_name=$1
    local port=$2
    local health_path=${3:-"/health"}
    local timeout=${4:-$HEALTH_CHECK_TIMEOUT}
    
    info "$service_name のヘルスチェック待機中（ポート: $port）..."
    
    local elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        if curl -f "http://localhost:$port$health_path" &>/dev/null; then
            success "$service_name は正常に起動しました"
            return 0
        fi
        
        if [[ $((elapsed % 30)) -eq 0 ]]; then
            info "$service_name 起動待機中... ($elapsed/$timeout 秒経過)"
        fi
        
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    error "$service_name のヘルスチェックがタイムアウトしました"
    return 1
}

verify_deployment() {
    info "デプロイを検証中..."
    
    # Node.js MCP Server検証（最重要）
    if ! curl -f "http://localhost:$MCP_NODEJS_PORT/health" &>/dev/null; then
        error "Node.js MCP Server のヘルスチェックに失敗"
        return 1
    fi
    
    if ! curl -f "http://localhost:$MCP_NODEJS_PORT/metrics" &>/dev/null; then
        error "Node.js MCP Server のメトリクス取得に失敗"
        return 1
    fi
    
    # その他のサービス検証
    if [[ "$DEPLOY_MODE" != "nodejs-only" ]]; then
        # Frontend
        if ! curl -f "http://localhost/health" &>/dev/null; then
            warn "Frontend のヘルスチェックに失敗"
        fi
        
        # Backend API
        if ! curl -f "http://localhost:8000/health" &>/dev/null; then
            warn "Backend API のヘルスチェックに失敗"
        fi
        
        # Prometheus
        if ! curl -f "http://localhost:9090/-/healthy" &>/dev/null; then
            warn "Prometheus のヘルスチェックに失敗"
        fi
        
        # Grafana
        if ! curl -f "http://localhost:3000/api/health" &>/dev/null; then
            warn "Grafana のヘルスチェックに失敗"
        fi
    fi
    
    success "デプロイ検証完了"
}

# =============================================================================
# ロールバック
# =============================================================================

perform_rollback() {
    error "ロールバックを実行中..."
    
    if [[ ! -f "$BACKUP_DIR/latest_backup.txt" ]]; then
        error "バックアップ情報が見つかりません"
        return 1
    fi
    
    local backup_path=$(cat "$BACKUP_DIR/latest_backup.txt")
    
    if [[ ! -d "$backup_path" ]]; then
        error "バックアップディレクトリが見つかりません: $backup_path"
        return 1
    fi
    
    info "バックアップから復元中: $backup_path"
    
    # サービス停止
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
    
    # 設定ファイル復元
    if [[ -d "$backup_path/monitoring" ]]; then
        cp -r "$backup_path/monitoring/"* "$MONITORING_DIR/"
    fi
    
    if [[ -f "$backup_path/$ENV_FILE" ]]; then
        cp "$backup_path/$ENV_FILE" "$ENV_FILE"
    fi
    
    # サービス再起動
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d
    
    success "ロールバック完了"
}

# =============================================================================
# クリーンアップ
# =============================================================================

cleanup_old_resources() {
    info "古いリソースをクリーンアップ中..."
    
    # 未使用Dockerイメージの削除
    docker image prune -f
    
    # 古いバックアップの削除（7日以上）
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -type d -name "backup_*" -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
    fi
    
    # 古いログファイルの削除（30日以上）
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    fi
    
    success "クリーンアップ完了"
}

# =============================================================================
# メイン処理
# =============================================================================

show_usage() {
    cat << EOF
使用方法: $0 [OPTIONS] [COMMAND]

コマンド:
    deploy          フルデプロイ（デフォルト）
    nodejs-only     Node.js MCP Server のみデプロイ
    backend-only    Backend API のみデプロイ
    rollback        最新バックアップからロールバック
    status          サービス状態確認
    logs            サービスログ表示
    cleanup         古いリソースのクリーンアップ
    test            デプロイテスト実行

オプション:
    -e, --environment ENV    環境設定 (production, staging, development)
    -m, --mode MODE         デプロイモード (full, nodejs-only, backend-only)
    -v, --verbose           詳細ログ出力
    -h, --help              ヘルプ表示

例:
    $0 deploy -e production
    $0 nodejs-only -v
    $0 rollback
    $0 status

EOF
}

main() {
    # ログディレクトリ作成
    mkdir -p "$(dirname "$DEPLOY_LOG")"
    
    # 引数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -m|--mode)
                DEPLOY_MODE="$2"
                shift 2
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            deploy|nodejs-only|backend-only|rollback|status|logs|cleanup|test)
                COMMAND="$1"
                if [[ "$1" == "nodejs-only" ]]; then
                    DEPLOY_MODE="nodejs-only"
                elif [[ "$1" == "backend-only" ]]; then
                    DEPLOY_MODE="backend-only"
                fi
                shift
                ;;
            *)
                error "不明なオプション: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # デフォルトコマンド
    COMMAND=${COMMAND:-deploy}
    
    info "MFG Drone 統一デプロイシステム開始"
    info "環境: $ENVIRONMENT, モード: $DEPLOY_MODE, コマンド: $COMMAND"
    
    # コマンド実行
    case "$COMMAND" in
        deploy)
            check_prerequisites
            create_backup
            build_mcp_nodejs
            build_other_services
            deploy_services
            verify_deployment
            cleanup_old_resources
            
            success "デプロイが正常に完了しました！"
            info "サービス情報:"
            info "  - Node.js MCP Server: http://localhost:$MCP_NODEJS_PORT"
            if [[ "$DEPLOY_MODE" != "nodejs-only" ]]; then
                info "  - Frontend: http://localhost"
                info "  - Backend API: http://localhost:8000"
                info "  - Prometheus: http://localhost:9090"
                info "  - Grafana: http://localhost:3000"
            fi
            ;;
        rollback)
            perform_rollback
            ;;
        status)
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" ps
            ;;
        logs)
            $DOCKER_COMPOSE -f "$COMPOSE_FILE" logs -f "${2:-$MCP_NODEJS_SERVICE}"
            ;;
        cleanup)
            cleanup_old_resources
            ;;
        test)
            verify_deployment
            ;;
        *)
            error "不明なコマンド: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"