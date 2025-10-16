#!/bin/bash

# This script helps to install and run the CWT project.
# It aims to be versatile across Linux and macOS, guiding users through Docker or native setup.
# For Windows, it provides instructions.

set -e

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")

echo "===================================================="
echo "  CWT - Crypto & NFT Withdrawal Tool Installation  "
echo "===================================================="

# --- Check if running in project root ---
if [ ! -f "${PROJECT_ROOT}/CWT_CLI/main.py" ]; then
    echo "Error: This script must be run from the CWT project root directory."
    echo "Please navigate to the directory containing CWT_CLI/main.py and run the script again."
    exit 1
fi

# --- Check for Git ---
if ! command -v git &> /dev/null
then
    echo "Git is not installed. Please install Git first:"
    echo "  - macOS: brew install git"
    echo "  - Debian/Ubuntu: sudo apt-get install git"
    echo "  - Fedora: sudo dnf install git"
    echo "  - Windows: Download from git-scm.com"
    exit 1
fi

# --- Detect OS ---
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Linux*)
        PLATFORM="Linux"
        ;;
    Darwin*)
        PLATFORM="macOS"
        ;;
    CYGWIN*|MINGW32*|MSYS*)
        PLATFORM="Windows"
        ;;
    *)
        PLATFORM="UNKNOWN"
        ;;
esac

if [ "${PLATFORM}" == "Windows" ]; then
    echo "Detected Windows. Please follow the manual instructions below:"
    echo ""
    echo "--- Windows Installation Instructions ---"
    echo "1.  **Install Git:** Download and install Git from https://git-scm.com/download/win."
    echo "2.  **Install Python 3.8+:** Download and install Python from https://www.python.org/downloads/windows/ (ensure 'Add Python to PATH' is checked during installation)."
    echo "3.  **Install Docker Desktop (Optional, Recommended):** Download and install Docker Desktop from https://www.docker.com/products/docker-desktop."
    echo "4.  **Clone the repository:** Open Git Bash or PowerShell and run:"
    echo "    git clone https://github.com/your-username/CWT.git"
    echo "    cd CWT"
    echo "5.  **Configure:** Create a .env file and edit CWT_CLI/config.ini as described in README.md."
    echo "6.  **Run via Docker (Recommended):** Open PowerShell or Command Prompt in the project root and run:"
    echo "    docker build -t cwt-tool ."
    echo "    docker run --rm -it --env-file ./.env cwt-tool"
    echo "7.  **Run Natively (Requires Chrome):** Open PowerShell or Command Prompt in the project root and run:"
    echo "    pip install -r requirements.txt"
    echo "    python CWT_CLI/main.py"
    echo "    (Ensure Google Chrome is installed and its WebDriver is accessible in PATH, or specify chrome_binary_location in config.ini)"
    echo ""
    echo "===================================================="
    echo "  CWT Installation Script Finished                 "
    echo "===================================================="
    exit 0
fi

# --- Interactive choice for Linux/macOS ---
INSTALL_METHOD=""
while true; do
    read -p "Do you want to install CWT using Docker (recommended) or Natively? (docker/native): " choice
    case "$choice" in
        docker ) INSTALL_METHOD="docker"; break;; 
        native ) INSTALL_METHOD="native"; break;; 
        * ) echo "Invalid choice. Please enter 'docker' or 'native'.";;
    esac
done

if [ "${INSTALL_METHOD}" == "docker" ]; then
    echo ""
    echo "--- Docker Installation Path ---"
    if ! command -v docker &> /dev/null
    then
        echo "Docker is not installed. Please install Docker first:"
        echo "  - ${PLATFORM}: Follow instructions at https://docs.docker.com/engine/install/"
        exit 1
    fi
    echo "Docker found. Proceeding with Docker setup."
    echo ""
    echo "To build and run the CWT Docker image, navigate to the project root and run:"
    echo "  ./run.sh"
    echo ""
    echo "Before running, ensure you have created a .env file in the project root with:"
    echo "  CWT_MAIN_WITHDRAWAL_ADDRESS=\"your_main_crypto_address_here\""
    echo "And configured CWT_CLI/config.ini with your exchange/wallet details."
    echo ""
    echo "For multi-architecture Docker images, refer to the GitHub Actions workflow."
elif [ "${INSTALL_METHOD}" == "native" ]; then
    echo ""
    echo "--- Native Python Installation Path ---"
    echo "CWT requires Python 3.8+."

    # --- Check for Python ---
    if command -v python3 &> /dev/null
    then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        echo "Python 3 found (version: ${PYTHON_VERSION})."
        if (( $(echo "${PYTHON_VERSION} < 3.8" | bc -l) )); then
            echo "Warning: Python version ${PYTHON_VERSION} is less than 3.8. Please upgrade for full compatibility."
        fi
    else
        echo "Python 3 not found. Please install Python 3.8+ from python.org or your system's package manager."
        exit 1
    fi

    echo ""
    echo "Installing Python dependencies..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r "${PROJECT_ROOT}/requirements.txt"
    echo "Python dependencies installed."

    echo ""
    echo "--- Browser Setup for Native Run ---"
    echo "CWT uses undetected-chromedriver, which requires Google Chrome to be installed."
    echo "Please ensure Google Chrome is installed on your system."
    echo ""
    echo "--- Configuration for Native Run ---"
    echo "Before running, ensure you have created a .env file in the project root with:"
    echo "  CWT_MAIN_WITHDRAWAL_ADDRESS=\"your_main_crypto_address_here\""
    echo "And configured CWT_CLI/config.ini with your exchange/wallet details."
    echo ""
    echo "--- To Run Natively ---"
    echo "Navigate to the project root and run:"
    echo "  python3 CWT_CLI/main.py"
fi

echo "===================================================="
echo "  CWT Installation Script Finished                 "
echo "===================================================="