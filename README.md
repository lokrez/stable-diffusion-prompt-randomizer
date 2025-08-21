Stable Diffusion Prompt Generator

A local web application that generates creative and randomized prompts for Stable Diffusion. It combines user-provided keywords with predefined styles and settings to produce unique and detailed prompts.
Features

    Intelligent Prompt Generation: This application leverages the powerful Gemini API to take your simple, concise keywords and transform them into rich, descriptive prompts that are ready for use in Stable Diffusion. This feature adds a layer of creativity and detail that would be time-consuming to write manually.

    Predefined Styles: The app includes a curated list of artistic styles, from Analog Film to Cyberpunk, as a starting point. By selecting a style from the dropdown menu, you can ensure your generated prompts are consistent with a specific aesthetic. This provides a powerful way to guide the AI's output without complex manual adjustments.

    Randomized Settings: To add variety to your image generations, the app automatically selects a random sampling method and scheduler from a pre-defined list. This helps you discover new and interesting combinations that you might not have chosen manually.

    API Key Management: This is a key security feature. The app securely handles your Gemini API key by storing it in a local, hidden file (key/gemini.key). On the first run, the script will prompt you to enter your key and then save it for future use. This prevents you from hardcoding your key or accidentally uploading it to a public repository. The server also keeps a count of consecutive API failures and will prompt you to replace the key after three failed attempts, making the app more reliable.

    Portable Output: The final output—including the positive prompt, negative prompt, sampling method, and scheduler—is formatted into a single, compact, and importable string. This makes it easy to copy and paste the entire configuration directly into other Stable Diffusion applications like Automatic1111.

Getting Started

To run this application, you will need to have Python 3 installed on your system, along with a Gemini API key.
Prerequisites

    Python 3

    pip (Python's package installer, usually included with Python 3)

    curl (A command-line tool for making network requests)

    A Gemini API Key

Installation

    Clone the repository:
    Begin by cloning the project from GitHub and navigating into the directory:

    git clone https://github.com/lokrez/stable-diffusion-prompt-randomizer.git
    cd stable-diffusion-prompt-randomizer


    Install Python dependencies:
    Run the following command to install the necessary Python libraries:

    pip install requests


    This command installs the requests library, which the server uses to make HTTP requests to the Gemini API.

    Run the application:
    Start the application by running the main bash script:

    ./start_server.sh


On the first run, the script will:

    Check for all required dependencies.

    Prompt you to enter your Gemini API key, explaining why it is needed.

    Offer to save the key to a local, hidden directory (key/) to make future runs easier and more secure.

How to Use

The application will automatically open in your default web browser after the server has started.

    Enter Keywords: Use the input fields to provide your creative direction. The "Positive Keywords" field is for what you want to see in the image, while the "Negative Keywords" field is for what you want to exclude.

    Select a Style (Optional): Use the dropdown menu to choose from a variety of predefined artistic styles. If you select a style, your keywords will be intelligently combined with the style's prompts. If you leave this blank, the AI will generate a unique style for you.

    Generate Prompts: Click the "Generate Prompts" button or press Enter in either of the keyword fields. The application will then display the generated prompts and settings.

    Copy and Go: Below the generated prompts, you will find dedicated buttons to copy the positive and negative prompts individually, or the entire output as a single, easily pasteable string for use in other applications.

Project Structure

    start_server.sh: The main bash script that automates the entire startup process, including dependency checks, port management, and API key handling.

    server.py: The core Python web server. It handles client requests, communicates with the Gemini API, and provides a list of predefined styles.

    index.html.template: The HTML file that defines the user interface of the web app. It is a template that gets a port number dynamically inserted by the start_server.sh script.

    styles.xml: An XML file containing all the predefined styles and their associated prompts, which the server.py file reads on startup.

    key/: A hidden directory created at runtime to securely store your API key. This directory is automatically added to .gitignore.

    .gitignore: A file that prevents sensitive data like logs and the key/ directory from being committed to the repository.

Troubleshooting

    "Address already in use" Error: The script is designed to handle this automatically by finding the next available port.

    "API Key Missing" Error: The script will prompt you for your key on the first run. If you are still seeing this error, ensure your key is correctly saved in key/gemini.key or set as a system-wide environment variable.

    "Bad Request" Error: This typically indicates a problem with the API key itself. The server will now automatically detect a consistently failing key and prompt you for a new one.

License

This project is licensed under the MIT License.
