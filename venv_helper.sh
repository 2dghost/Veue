#!/bin/bash

# Helper script for managing the Python virtual environment

# Define colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
show_usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  source venv_helper.sh activate   - Activate the virtual environment"
    echo -e "  source venv_helper.sh deactivate - Deactivate the virtual environment"
    echo -e "  ./venv_helper.sh status          - Check if the virtual environment is active"
    echo -e "  ./venv_helper.sh help            - Show this help message"
    echo
    echo -e "${YELLOW}Note:${NC} You must use 'source' when activating or deactivating the environment."
}

# Function to check if the virtual environment is active
check_venv_status() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo -e "${GREEN}Virtual environment is active:${NC} $VIRTUAL_ENV"
        return 0
    else
        echo -e "${YELLOW}Virtual environment is not active.${NC}"
        return 1
    fi
}

# Main logic based on the command argument
case "$1" in
    activate)
        if [[ -n "$VIRTUAL_ENV" ]]; then
            echo -e "${YELLOW}A virtual environment is already active:${NC} $VIRTUAL_ENV"
            echo -e "Run '${BLUE}source venv_helper.sh deactivate${NC}' first if you want to switch environments."
        else
            if [[ -f "venv/bin/activate" ]]; then
                echo -e "${GREEN}Activating virtual environment...${NC}"
                source venv/bin/activate
                echo -e "${GREEN}Virtual environment activated!${NC}"
                echo -e "Run '${BLUE}source venv_helper.sh deactivate${NC}' when you're done."
            else
                echo -e "${YELLOW}Error:${NC} Virtual environment not found in 'venv' directory."
                echo -e "Make sure you're in the project root directory and the environment is set up."
            fi
        fi
        ;;
    deactivate)
        if [[ -n "$VIRTUAL_ENV" ]]; then
            echo -e "${GREEN}Deactivating virtual environment...${NC}"
            deactivate
            echo -e "${GREEN}Virtual environment deactivated!${NC}"
        else
            echo -e "${YELLOW}No virtual environment is currently active.${NC}"
        fi
        ;;
    status)
        check_venv_status
        ;;
    help|*)
        show_usage
        ;;
esac 