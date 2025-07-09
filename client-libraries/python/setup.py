from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcp-drone-client",
    version="1.0.0",
    author="MFG Drone Team",
    author_email="team@mfg-drone.com",
    description="Python SDK for MCP Drone Control Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coolerking/mfg_drone_by_claudecode",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "aioresponses>=0.7.0",
        ],
    },
    keywords="mcp, drone, control, api, sdk, robotics",
    project_urls={
        "Bug Reports": "https://github.com/coolerking/mfg_drone_by_claudecode/issues",
        "Source": "https://github.com/coolerking/mfg_drone_by_claudecode",
        "Documentation": "https://mcp-drone-client.readthedocs.io/",
    },
)