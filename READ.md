Stable Diffusion Prompt Generator

A local web application that uses the Gemini large language model to generate creative, detailed prompts for Stable Diffusion and other AI image models. It runs entirely on your local machine, ensuring your API key and data remain private and secure.
✨ Features

    Prompt Generation: Generates highly detailed positive and negative prompts from a few keywords.

    Secure API Key Management: Prompts for your Gemini API key on the first run and saves it securely to a local file with restricted permissions.

    Randomized Settings: Automatically selects a random sampling method and scheduler for each prompt, saving you time.

    Clipboard Functionality: One-click buttons to copy the generated prompts and settings string for easy use.

    User-Friendly Interface: A clean, responsive web interface built with Tailwind CSS.

⚙️ Prerequisites

To run this project, you need the following installed on your system:

    Python 3.x

    pip (Python package installer)

    bash (for the start_server.sh script)

➡️ Getting Started

Follow these steps to set up and run the application.
Step 1: Clone the Repository

Clone this repository to your local machine using Git.

git clone https://github.com/lokrez/stable-diffusion-prompt-randomizer.git
cd stable-diffusion-prompt-randomizer


Step 2: Install Dependencies

This project requires the requests Python library. You can install it using the provided requirements.txt file.

pip install -r requirements.txt


Step 3: Run the Application

Execute the start_server.sh script from your terminal.

./start_server.sh


Step 4: Provide Your Gemini API Key

The first time you run the script, you will be prompted to enter your Gemini API key.

    💡 Why do I need a key? This application uses the Gemini large language model to generate prompts. Your API key is a unique token that authenticates your requests to Google's servers.

    ➡️ How do I get a key?

        Go to Google AI Studio: https://aistudio.google.com/

        Sign in with your Google account.

        Click on Get API key in the sidebar.

        Click Create API key in a new project.

The script will save your key to a file in a key/ directory and set the file permissions to 600 for security. The .gitignore file ensures this sensitive information is not accidentally committed to Git.
🚀 Usage

Once the server is running, your default web browser will open to the application page.

    Enter positive keywords (e.g., ancient forest, mossy ruins, glowing mushrooms).

    (Optional) Enter negative keywords (e.g., blurry, bad anatomy).

    Click the ✨ Generate Prompts button.

The application will display the generated positive and negative prompts, along with randomized Stable Diffusion settings. You can then copy these prompts and use them in your preferred AI image generation tool.
📁 File Structure

    start_server.sh: The main script to start the web server and open the application.

    server.py: The backend Python web server that handles prompt generation using the Gemini API.

    index.html.template: The HTML template for the web application's frontend.

    requirements.txt: Specifies the Python dependencies needed to run the project.

    .gitignore: A configuration file that tells Git which files to ignore. This is crucial for security.

🔒 Security

Your API key is handled with the utmost care. It is stored locally on your machine in a file with restricted access (chmod 600), and the .gitignore file ensures it is never committed to the public repository. The communication between the frontend and the backend occurs locally, so your data never leaves your machine.
💡 Future Considerations

    Add a user interface for selecting specific sampling methods and schedulers.

    Implement more detailed prompt customization options, such as art styles or lighting conditions, directly in the UI.

    Expand the API to include more features, like fetching a list of all available settings.

    Enhance server-side input validation to increase robustness.
