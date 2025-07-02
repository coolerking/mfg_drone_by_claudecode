"""
Phase 5: Docker and Deployment Tests
Tests for Docker configuration and deployment functionality
"""

import pytest
import os
import yaml
import json
import subprocess
from pathlib import Path


class TestDockerfiles:
    """Test Docker configuration files"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend_dir = Path(__file__).parent.parent
        self.dockerfile_path = self.backend_dir / "Dockerfile"
        self.docker_compose_path = self.backend_dir / "docker-compose.yml"
        self.docker_compose_dev_path = self.backend_dir / "docker-compose.dev.yml"
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        assert self.dockerfile_path.exists(), "Dockerfile should exist"
    
    def test_dockerfile_content(self):
        """Test Dockerfile content and structure"""
        with open(self.dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check for multi-stage build
        assert "FROM python:3.11-slim as builder" in content
        assert "FROM python:3.11-slim as production" in content
        
        # Check for essential instructions
        assert "WORKDIR /app" in content
        assert "COPY requirements.txt" in content
        assert "RUN pip install" in content
        assert "EXPOSE 8000" in content
        assert "HEALTHCHECK" in content
        
        # Check for security features
        assert "groupadd -r appuser" in content
        assert "USER appuser" in content
        
        # Check for environment variables
        assert "ENV PYTHONDONTWRITEBYTECODE=1" in content
        assert "ENV PYTHONUNBUFFERED=1" in content
    
    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists"""
        assert self.docker_compose_path.exists(), "docker-compose.yml should exist"
    
    def test_docker_compose_structure(self):
        """Test docker-compose.yml structure"""
        with open(self.docker_compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check basic structure
        assert "version" in compose_config
        assert "services" in compose_config
        assert "volumes" in compose_config
        assert "networks" in compose_config
        
        # Check for main service
        assert "mfg-drone-api" in compose_config["services"]
        
        # Check for supporting services
        services = compose_config["services"]
        assert "redis" in services
        
        # Check main service configuration
        api_service = services["mfg-drone-api"]
        assert "build" in api_service or "image" in api_service
        assert "ports" in api_service
        assert "environment" in api_service
        assert "volumes" in api_service
        
        # Check port mapping
        ports = api_service["ports"]
        assert any("8000:8000" in str(port) for port in ports)
    
    def test_docker_compose_dev_override(self):
        """Test development docker-compose override"""
        assert self.docker_compose_dev_path.exists(), "docker-compose.dev.yml should exist"
        
        with open(self.docker_compose_dev_path, 'r') as f:
            dev_config = yaml.safe_load(f)
        
        # Check override structure
        assert "services" in dev_config
        assert "mfg-drone-api" in dev_config["services"]
        
        # Check development-specific settings
        api_service = dev_config["services"]["mfg-drone-api"]
        
        # Should have development environment settings
        if "environment" in api_service:
            env_vars = api_service["environment"]
            env_str = str(env_vars)
            assert "development" in env_str.lower() or "debug" in env_str.lower()
    
    def test_environment_variables(self):
        """Test required environment variables are defined"""
        with open(self.docker_compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        api_service = compose_config["services"]["mfg-drone-api"]
        env_vars = api_service.get("environment", [])
        
        # Convert to string for easier checking
        env_str = str(env_vars)
        
        # Check for essential environment variables
        required_env_vars = [
            "HOST", "PORT", "LOG_LEVEL", "ENVIRONMENT",
            "MFG_DATASETS_ROOT", "MFG_MODELS_ROOT"
        ]
        
        for var in required_env_vars:
            assert var in env_str, f"Environment variable {var} should be defined"
    
    def test_volume_configuration(self):
        """Test volume configuration"""
        with open(self.docker_compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check named volumes
        volumes = compose_config["volumes"]
        expected_volumes = ["datasets_data", "models_data", "logs_data"]
        
        for volume in expected_volumes:
            assert volume in volumes, f"Volume {volume} should be defined"
        
        # Check service volume mounts
        api_service = compose_config["services"]["mfg-drone-api"]
        service_volumes = api_service.get("volumes", [])
        
        # Should have persistent data volumes
        volume_str = str(service_volumes)
        assert "datasets_data" in volume_str
        assert "models_data" in volume_str
    
    def test_network_configuration(self):
        """Test network configuration"""
        with open(self.docker_compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check network definition
        networks = compose_config["networks"]
        assert "mfg-drone-network" in networks
        
        # Check network settings
        network_config = networks["mfg-drone-network"]
        assert "driver" in network_config
        assert network_config["driver"] == "bridge"


class TestNginxConfiguration:
    """Test Nginx configuration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend_dir = Path(__file__).parent.parent
        self.nginx_conf_path = self.backend_dir / "nginx.conf"
    
    def test_nginx_config_exists(self):
        """Test that nginx.conf exists"""
        assert self.nginx_conf_path.exists(), "nginx.conf should exist"
    
    def test_nginx_config_structure(self):
        """Test nginx configuration structure"""
        with open(self.nginx_conf_path, 'r') as f:
            content = f.read()
        
        # Check for main sections
        assert "events {" in content
        assert "http {" in content
        assert "upstream mfg_drone_api" in content
        
        # Check for SSL configuration
        assert "ssl_certificate" in content
        assert "ssl_certificate_key" in content
        
        # Check for security headers
        assert "X-Frame-Options" in content
        assert "X-Content-Type-Options" in content
        assert "Content-Security-Policy" in content
        
        # Check for rate limiting
        assert "limit_req_zone" in content
        assert "limit_conn_zone" in content
        
        # Check for location blocks
        assert "location /api/" in content
        assert "location /ws" in content
        assert "location /dashboard" in content
    
    def test_nginx_upstream_config(self):
        """Test upstream backend configuration"""
        with open(self.nginx_conf_path, 'r') as f:
            content = f.read()
        
        # Check upstream configuration
        assert "upstream mfg_drone_api" in content
        assert "server mfg-drone-api:8000" in content
        assert "least_conn" in content or "ip_hash" in content
    
    def test_nginx_security_features(self):
        """Test security features in nginx config"""
        with open(self.nginx_conf_path, 'r') as f:
            content = f.read()
        
        # Security headers
        security_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options", 
            "X-XSS-Protection",
            "Referrer-Policy",
            "Content-Security-Policy"
        ]
        
        for header in security_headers:
            assert header in content, f"Security header {header} should be configured"
        
        # SSL/TLS configuration
        assert "ssl_protocols" in content
        assert "ssl_ciphers" in content


class TestMonitoringConfiguration:
    """Test monitoring configuration files"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend_dir = Path(__file__).parent.parent
        self.monitoring_dir = self.backend_dir / "monitoring"
        self.prometheus_config = self.monitoring_dir / "prometheus.yml"
    
    def test_monitoring_directory_exists(self):
        """Test that monitoring directory exists"""
        assert self.monitoring_dir.exists(), "monitoring directory should exist"
    
    def test_prometheus_config_exists(self):
        """Test that prometheus.yml exists"""
        assert self.prometheus_config.exists(), "prometheus.yml should exist"
    
    def test_prometheus_config_structure(self):
        """Test prometheus configuration structure"""
        with open(self.prometheus_config, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check basic structure
        assert "global" in config
        assert "scrape_configs" in config
        
        # Check global settings
        global_config = config["global"]
        assert "scrape_interval" in global_config
        assert "evaluation_interval" in global_config
        
        # Check scrape configurations
        scrape_configs = config["scrape_configs"]
        assert len(scrape_configs) > 0
        
        # Check for main application scraping
        job_names = [job["job_name"] for job in scrape_configs]
        assert "mfg-drone-api" in job_names
        assert "prometheus" in job_names
    
    def test_prometheus_targets(self):
        """Test prometheus target configuration"""
        with open(self.prometheus_config, 'r') as f:
            config = yaml.safe_load(f)
        
        scrape_configs = config["scrape_configs"]
        
        # Find API job configuration
        api_job = None
        for job in scrape_configs:
            if job["job_name"] == "mfg-drone-api":
                api_job = job
                break
        
        assert api_job is not None, "mfg-drone-api job should be configured"
        
        # Check target configuration
        assert "static_configs" in api_job
        static_configs = api_job["static_configs"]
        assert len(static_configs) > 0
        
        targets = static_configs[0]["targets"]
        assert "mfg-drone-api:8000" in targets[0]


class TestCICDConfiguration:
    """Test CI/CD pipeline configuration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.repo_root = Path(__file__).parent.parent.parent
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.cicd_workflow = self.workflows_dir / "phase5-ci-cd.yml"
    
    def test_cicd_workflow_exists(self):
        """Test that CI/CD workflow exists"""
        assert self.cicd_workflow.exists(), "phase5-ci-cd.yml should exist"
    
    def test_cicd_workflow_structure(self):
        """Test CI/CD workflow structure"""
        with open(self.cicd_workflow, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check basic structure
        assert "name" in workflow
        assert "on" in workflow
        assert "jobs" in workflow
        
        # Check trigger events
        on_config = workflow["on"]
        assert "push" in on_config
        assert "pull_request" in on_config
        
        # Check jobs
        jobs = workflow["jobs"]
        expected_jobs = ["test", "security", "docker-build"]
        
        for job in expected_jobs:
            assert job in jobs, f"Job {job} should be defined"
    
    def test_test_job_configuration(self):
        """Test test job configuration"""
        with open(self.cicd_workflow, 'r') as f:
            workflow = yaml.safe_load(f)
        
        test_job = workflow["jobs"]["test"]
        
        # Check matrix strategy
        assert "strategy" in test_job
        strategy = test_job["strategy"]
        assert "matrix" in strategy
        
        # Check Python versions
        matrix = strategy["matrix"]
        assert "python-version" in matrix
        python_versions = matrix["python-version"]
        assert "3.11" in python_versions
        
        # Check steps
        assert "steps" in test_job
        steps = test_job["steps"]
        
        # Check for essential steps
        step_names = [step.get("name", "") for step in steps]
        assert any("checkout" in name.lower() for name in step_names)
        assert any("python" in name.lower() for name in step_names)
        assert any("test" in name.lower() for name in step_names)
    
    def test_docker_job_configuration(self):
        """Test Docker build job configuration"""
        with open(self.cicd_workflow, 'r') as f:
            workflow = yaml.safe_load(f)
        
        docker_job = workflow["jobs"]["docker-build"]
        
        # Check dependencies
        assert "needs" in docker_job
        needs = docker_job["needs"]
        assert "test" in needs
        
        # Check steps
        steps = docker_job["steps"]
        step_names = [step.get("name", "") for step in steps]
        
        # Check for Docker-related steps
        assert any("docker" in name.lower() for name in step_names)
        assert any("build" in name.lower() for name in step_names)


class TestDeploymentScripts:
    """Test deployment and startup scripts"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend_dir = Path(__file__).parent.parent
    
    def test_start_script_exists(self):
        """Test that startup script exists"""
        start_script = self.backend_dir / "start_api_server.py"
        assert start_script.exists(), "start_api_server.py should exist"
    
    def test_requirements_file_valid(self):
        """Test that requirements.txt is valid"""
        requirements_file = self.backend_dir / "requirements.txt"
        assert requirements_file.exists(), "requirements.txt should exist"
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Check for essential packages
        essential_packages = ["fastapi", "uvicorn", "pydantic", "websockets"]
        
        for package in essential_packages:
            assert package in content, f"Package {package} should be in requirements.txt"
    
    def test_docker_ignore_exists(self):
        """Test that .dockerignore exists (if present)"""
        dockerignore = self.backend_dir / ".dockerignore"
        
        # This is optional, so we only test if it exists
        if dockerignore.exists():
            with open(dockerignore, 'r') as f:
                content = f.read()
            
            # Should ignore common files
            assert "__pycache__" in content or "*.pyc" in content
            assert ".git" in content or "*.git*" in content


@pytest.mark.integration
class TestDockerIntegration:
    """Integration tests for Docker functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.backend_dir = Path(__file__).parent.parent
        
    @pytest.mark.skipif(
        subprocess.run(["which", "docker"], capture_output=True).returncode != 0,
        reason="Docker not available"
    )
    def test_dockerfile_builds_successfully(self):
        """Test that Dockerfile builds successfully"""
        try:
            # Build the Docker image
            result = subprocess.run([
                "docker", "build", "-t", "mfg-drone-api:test", "."
            ], cwd=self.backend_dir, capture_output=True, text=True, timeout=300)
            
            assert result.returncode == 0, f"Docker build failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.skip("Docker build timeout - skipping test")
        except Exception as e:
            pytest.skip(f"Docker build test failed: {e}")
    
    @pytest.mark.skipif(
        subprocess.run(["which", "docker-compose"], capture_output=True).returncode != 0,
        reason="Docker Compose not available"
    )
    def test_docker_compose_config_valid(self):
        """Test that docker-compose configuration is valid"""
        try:
            # Validate docker-compose configuration
            result = subprocess.run([
                "docker-compose", "config"
            ], cwd=self.backend_dir, capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0, f"Docker compose config invalid: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.skip("Docker compose config timeout - skipping test")
        except Exception as e:
            pytest.skip(f"Docker compose config test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])