import http.server
import socketserver
import json
import sys
import random
import requests
import os

# --- Configuration ---
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
MAX_PORT_ATTEMPTS = 10

# === API Configuration ===
# Read the API key from the environment variable set by the bash script
API_KEY = os.environ.get("GEMINI_API_KEY", "")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key="
FAILURE_COUNT_FILE = "key/api_failure_count.txt"
MAX_FAILURES = 3

# Define common Stable Diffusion settings for randomization
SAMPLING_METHODS = [
    'DPM++ 2M', 'DPM++ SDE', 'DPM++ 2M SDE', 'DPM++ 2M SDE Heun',
    'DPM++ 2S a', 'DPM++ 3M SDE', 'Euler a', 'Euler', 'LMS', 'Heun',
    'DPM2', 'DPM2 a', 'DPM fast', 'DPM adaptive', 'Restart', 'DDIM',
    'DDIM CFG++', 'PLMS', 'UniPC'
]

SCHEDULERS = [
    'Automatic', 'Uniform', 'Karras', 'Exponential', 'Polyexponential',
    'SGM Uniform', 'KL Optimal', 'Align Your Steps', 'Simple',
    'Normal', 'DDIM', 'Beta'
]

def increment_failure_count():
    """Reads the failure count file, increments the count, and writes it back."""
    try:
        if not os.path.exists(os.path.dirname(FAILURE_COUNT_FILE)):
            os.makedirs(os.path.dirname(FAILURE_COUNT_FILE))
            
        with open(FAILURE_COUNT_FILE, 'r') as f:
            count = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        count = 0
    
    with open(FAILURE_COUNT_FILE, 'w') as f:
        f.write(str(count + 1))
    return count + 1

def reset_failure_count():
    """Resets the failure count to zero."""
    try:
        if os.path.exists(FAILURE_COUNT_FILE):
            os.remove(FAILURE_COUNT_FILE)
    except OSError as e:
        print(f"Error removing failure count file: {e}", file=sys.stderr, flush=True)

class PromptGeneratorHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Handle API requests from the web app
        if self.path == '/api/generate':
            # Check if the API key is present before proceeding
            if not API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "API key is missing.", "code": "API_KEY_MISSING"}).encode('utf-8'))
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            keywords = data.get('keywords', '')
            negative_keywords = data.get('negativeKeywords', '')

            # Randomly select a sampling method and scheduler
            sampling_method = random.choice(SAMPLING_METHODS)
            scheduler = random.choice(SCHEDULERS)
            
            # Construct the prompt for the Gemini API
            prompt_text = f"""
Create a highly detailed, creative, and artistic stable diffusion prompt based on the following keywords: "{keywords}".
The prompt should be structured to include a main subject, a descriptive background, a specific art style, lighting conditions, and a mood or atmosphere.
Make sure to use rich, descriptive adjectives and verbs.
After the main prompt, also generate a list of negative prompt keywords based on the following negative keywords: "{negative_keywords}". These should be common things to avoid in generated images, such as blurriness, artifacts, or bad anatomy.

Example structure:
"A [main subject] in a [descriptive background], [specific art style], [lighting], [mood], cinematic, highly detailed, 4k, digital art. Negative prompt: [negative keywords]."

Return only the generated positive prompt and negative prompt, separated by the string "---NEGATIVE---".
            """
            
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt_text}]}]
            }

            try:
                # Make the API call to Gemini
                response = requests.post(f"{API_URL}{API_KEY}", json=payload)
                response.raise_for_status() # Raise an exception for bad status codes
                
                # If the request is successful, reset the failure count
                reset_failure_count()

                result = response.json()
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Split the generated text into positive and negative parts
                parts = generated_text.split("---NEGATIVE---")
                positive_prompt = parts[0].strip()
                negative_prompt = parts[1].strip() if len(parts) > 1 else ""

                # Build the final response JSON
                response_data = {
                    "positive_prompt": positive_prompt,
                    "negative_prompt": negative_prompt,
                    "sampling_method": sampling_method,
                    "scheduler": scheduler
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
            except requests.exceptions.RequestException as e:
                # If the API request fails with a 400 Client Error, it's likely a bad key
                if e.response and e.response.status_code == 400:
                    failures = increment_failure_count()
                    if failures >= MAX_FAILURES:
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        error_data = {"error": "API key failed too many times. Please provide a new key.", "code": "API_KEY_FAILED_TOO_MANY_TIMES"}
                        self.wfile.write(json.dumps(error_data).encode('utf-8'))
                    else:
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        error_data = {"error": f"API request failed: {e}. Failure count: {failures}/{MAX_FAILURES}", "code": "API_REQUEST_FAILED"}
                        self.wfile.write(json.dumps(error_data).encode('utf-8'))
                else:
                    # For all other request exceptions, return a generic error
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_data = {"error": f"API request failed: {e}", "code": "API_REQUEST_FAILED"}
                    self.wfile.write(json.dumps(error_data).encode('utf-8'))
            except (KeyError, IndexError) as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_data = {"error": f"Failed to parse API response: {e}", "code": "API_RESPONSE_PARSE_ERROR"}
                self.wfile.write(json.dumps(error_data).encode('utf-8'))
            return
        
        # For all other GET requests, serve the requested file (like index.html)
        super().do_GET()

# Server startup logic with port fallback
for i in range(MAX_PORT_ATTEMPTS):
    try:
        with socketserver.TCPServer(("", PORT), PromptGeneratorHandler) as httpd:
            print(f"Serving at port {PORT}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
            break # Exit the loop if the server started successfully
    except OSError as e:
        if e.errno == 98:
            print(f"Port {PORT} is in use, trying next port...")
            PORT += 1
        else:
            raise # Re-raise other errors
else:
    print(f"Could not find an available port after {MAX_PORT_ATTEMPTS} attempts. Please check your network configuration.")
    sys.exit(1)

