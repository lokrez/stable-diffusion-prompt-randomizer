#!/bin/bash

# This script starts a Python web server and opens the web app in your browser.
# It requires Python 3 and the 'requests' library to be installed.

# --- Configuration ---
PORT=8000
SERVER_FILE="server.py"
HTML_FILE="index.html"
TEMPLATE_FILE="index.html.template"
SCRIPT_LOG="startup.log"
KEY_DIR="key"
KEY_FILE="${KEY_DIR}/gemini.key"
FAILURE_COUNT_FILE="${KEY_DIR}/api_failure_count.txt"
GITIGNORE_FILE=".gitignore"

# --- Logging Setup ---
# Redirect all subsequent stdout and stderr to the log file,
# while also piping it to the terminal for real-time viewing.
exec > >(tee -a "$SCRIPT_LOG") 2>&1
echo "--- $(date) - Script started ---"

# Function to get the API key
get_api_key() {
    local key_is_found=false
    local user_key=""

    # Check for the key file first
    if [ -f "$KEY_FILE" ]; then
        user_key=$(cat "$KEY_FILE" | sed '1s/^\xef\xbb\xbf//' | tr -d '[:space:]')
        if [ -n "$user_key" ]; then
            GEMINI_API_KEY="$user_key"
            echo "Using API key from '${KEY_FILE}'."
            key_is_found=true
        fi
    fi
    
    # If the key was not found in the file, check environment variable
    if [ "$key_is_found" == false ] && [ -n "$GEMINI_API_KEY" ]; then
        echo "Using API key from environment variable."
        key_is_found=true
    fi

    # If key is still not found, prompt the user
    if [ "$key_is_found" == false ]; then
        while true; do
            echo "--------------------------------------------------------"
            read -p "Please enter your Gemini API key: " user_key
            echo "--------------------------------------------------------"
            
            # Check if the key is empty or the placeholder
            if [ -z "$user_key" ] || [ "$user_key" == "YOUR_API_KEY_HERE" ]; then
                echo "❌ Invalid key. Please provide a valid Gemini API key."
                echo ""
                echo "💡 Why do I need a key? 💡"
                echo "This application uses the Gemini large language model to generate creative prompts."
                echo "Your API key is a unique token that authenticates your request to Google's servers."
                echo "It tells the API that you have permission to use the service."
                echo ""
                echo "➡️ How do I get a key? ➡️"
                echo "1. Go to Google AI Studio: https://aistudio.google.com/"
                echo "2. Sign in with your Google account."
                echo "3. Click on 'Get API key' in the sidebar."
                echo "4. Click 'Create API key in a new project'."
                echo ""
            else
                GEMINI_API_KEY="$user_key"
                echo "Would you like to save this key for future runs? [y/n]:"
                read -r save_key_choice
                if [[ "$save_key_choice" =~ ^[Yy]$ ]]; then
                    mkdir -p "$KEY_DIR"
                    echo -n "$GEMINI_API_KEY" > "$KEY_FILE"
                    chmod 600 "$KEY_FILE"
                    echo "✅ Key saved to '${KEY_FILE}'. Permissions set to 600 for security."
                fi
                break
            fi
        done
    fi
}

# --- Main Script Execution ---

# Check if Python 3 is installed
echo "Checking for Python 3..."
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 could not be found. Please install it to run this script."
    exit 1
fi
echo "Python 3 found. Proceeding."

# Check if the 'requests' library is installed for the API call
echo "Checking for Python 'requests' library..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "Error: The 'requests' library is not installed."
    echo "Please install it with: pip install requests"
    exit 1
fi
echo "'requests' library found. Proceeding."

# Ensure a .gitignore file exists and is configured to ignore sensitive files
if [ ! -f "$GITIGNORE_FILE" ]; then
    echo "Creating .gitignore to prevent accidental commits..."
    cat <<EOF >"$GITIGNORE_FILE"
# Log files
*.log

# Dynamically created HTML file
index.html

# API key directory
key/
EOF
    echo ".gitignore created successfully."
fi

# Prompt for the API key
get_api_key

# Start the server and capture its output
echo "Starting the Python server..."
GEMINI_API_KEY="$GEMINI_API_KEY" python3 -u "$SERVER_FILE" "$PORT" > server.log 2>&1 &
SERVER_PID=$!
echo "Server process ID: $SERVER_PID"

# Wait for the server to confirm it is listening and get the final port number
ACTUAL_PORT=""
echo "Waiting for server to start..."
MAX_WAIT_TIME=10
start_time=$(date +%s)
while [ -z "$ACTUAL_PORT" ]; do
    current_time=$(date +%s)
    if (( current_time - start_time > MAX_WAIT_TIME )); then
        echo "❌ Server failed to start in under $MAX_WAIT_TIME seconds. Exiting."
        kill $SERVER_PID
        exit 1
    fi
    ACTUAL_PORT=$(grep -oP '(?<=Serving at port )\d+' server.log)
    sleep 1
done

echo "Server is running on port $ACTUAL_PORT."
echo "Access the app at http://localhost:$ACTUAL_PORT"

# Check the server logs for the specific error code indicating too many failures.
if grep -q "API_KEY_FAILED_TOO_MANY_TIMES" server.log; then
    echo "⚠️ Too many API key failures detected. The key is likely invalid or revoked."
    echo "Deleting the key file and failure counter."
    rm -f "$KEY_FILE"
    rm -f "$FAILURE_COUNT_FILE"
    echo "Please restart the script and enter a new key."
    kill $SERVER_PID
    exit 1
fi

# Add a 2-second delay to ensure the server is fully ready before the browser attempts to connect.
echo "Waiting for the server to be fully ready..."
sleep 2

# Dynamically update the HTML file with the correct port.
echo "Updating HTML template with the correct port..."
# Create a new index.html file with the correct port.
awk -v port="$ACTUAL_PORT" '{gsub(/\{\{SERVER_PORT\}\}/, port)}1' "$TEMPLATE_FILE" > "$HTML_FILE"

# Open the web app in the default browser
echo "Attempting to open the web app in your default browser..."
# Note: The command for opening a browser varies by OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:$ACTUAL_PORT"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:$ACTUAL_PORT"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" ]]; then
    start "http://localhost:$ACTUAL_PORT"
else
    echo "Could not automatically open a browser. Please navigate to http://localhost:$ACTUAL_PORT"
fi

# Trap Ctrl+C to gracefully shut down the server process and remove the log file.
trap "echo 'Shutting down server...'; rm -f server.log $SCRIPT_LOG; kill $SERVER_PID; wait $SERVER_PID; exit" INT

# Wait for the background process to finish (which it won't until you kill it)
wait $SERVER_PID

