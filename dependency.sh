#!/bin/bash
# =========================================================
# DarkReaper Dependency Installation Script
# Author: Viraj Kadam (viru the hacker)
# Purpose: Auto-install all dependencies for DarkReaper OSINT Tool
# =========================================================

echo "========================================================="
echo "      DARKREAPER - AUTOMATED DEPENDENCY INSTALLER"
echo "========================================================="

# --- Update System ---
echo "[+] Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

# --- Install Python and Pip if missing ---
echo "[+] Installing Python3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# --- Install Common Utilities ---
echo "[+] Installing basic tools..."
sudo apt install -y git wget curl unzip tor tesseract-ocr

# --- Optional but useful for OSINT ---
echo "[+] Installing additional CLI tools..."
sudo apt install -y whois net-tools nmap jq

# --- Playwright Dependencies ---
echo "[+] Installing Playwright browsers (for automation modules)..."
pip install playwright
playwright install

# --- Setup Virtual Environment (optional) ---
if [ ! -d "venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv venv
fi

# --- Activate Virtual Environment ---
source venv/bin/activate

# --- Install Python Dependencies ---
echo "[+] Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# --- Tor Service Setup ---
echo "[+] Enabling and starting Tor service..."
sudo systemctl enable tor
sudo systemctl start tor

# --- Confirm installations ---
echo "========================================================="
echo "[✓] All dependencies installed successfully!"
echo "[✓] You can now run the tool using:"
echo ""
echo "    source venv/bin/activate"
echo "    python3 darkreaper.py"
echo ""
echo "========================================================="
