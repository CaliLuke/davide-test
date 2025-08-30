# Import necessary standard libraries
import os  # Used for interacting with the operating system, like getting environment variables and file paths.
import argparse  # Used for parsing command-line arguments.
import logging  # Used for logging information, warnings, and errors.
import json  # Used for working with JSON data.

# Import third-party libraries
import requests  # Used for making HTTP requests to the Ollama API.
from requests.exceptions import RequestException  # Specific exception for requests library errors.
from dotenv import load_dotenv  # Used to load environment variables from a .env file.
import ollama  # The official Python client for the Ollama API.
from google import genai  # The official Python client for the Google Gemini API.

# --- Configuration ---

# Load environment variables from a .env file into the environment.
# This allows for secure management of API keys and other configuration.
load_dotenv()

# Configure basic logging to display messages with a timestamp, log level, and the message itself.
# This helps in debugging and monitoring the script's execution.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Ollama Model Management ---

def pull_model_with_progress(model_name: str) -> bool:
    """
    Pulls a model from the Ollama Hub with detailed progress feedback.
    This function streams the response from the Ollama API to provide real-time status updates.

    Args:
        model_name: The name of the Ollama model to pull (e.g., "gemma3:12b").

    Returns:
        True if the model was pulled successfully, False otherwise.
    """
    # Define the Ollama API endpoint for pulling models.
    url = "http://localhost:11434/api/pull"
    # The payload specifies the name of the model to be pulled.
    payload = {"name": model_name}
    # Set the content type header for the JSON payload.
    headers = {"Content-Type": "application/json"}

    logging.info(f"Starting to pull model: {model_name}")
    try:
        # Make a POST request with stream=True to handle the streaming response.
        with requests.post(url, data=json.dumps(payload), headers=headers, stream=True) as response:
            # Check for a non-successful HTTP status code.
            if response.status_code != 200:
                logging.error(f"Error: {response.status_code} - {response.text}")
                return False

            # Iterate over the response line by line as it comes in.
            for line in response.iter_lines():
                if line:
                    # Each line is a JSON object with status information.
                    json_response = json.loads(line)
                    # Check if the 'status' key exists in the response.
                    if "status" in json_response:
                        status = json_response["status"]
                        logging.info(f"Status: {status}")
                        # Check for a success message to confirm the pull is complete.
                        if "success" in status.lower() or "finished" in status.lower():
                            logging.info(f"Model '{model_name}' has been successfully pulled.")
                            return True
                    # Provide a percentage-based progress bar for the download.
                    if "total" in json_response and "completed" in json_response:
                        completed = json_response["completed"]
                        total = json_response["total"]
                        percent = (completed / total) * 100
                        # Use carriage return to keep the progress on a single line.
                        print(f"Downloading layer: {percent:.2f}% complete", end='\r')
            # Print a newline after the progress bar is complete.
            print("\nPull process completed.")
            return True
    except RequestException as e:
        # Handle network-related errors during the request.
        logging.error(f"An error occurred: {e}")
        return False

def ensure_ollama_model_available(model_name: str) -> None:
    """
    Checks if a specified Ollama model is available locally. If not, it pulls the model.

    Args:
        model_name: The name of the Ollama model to check for.
    """
    try:
        # Get a list of all models currently available on the local machine.
        local_models = ollama.list()['models']
        # Check if the desired model's name is in the list of local models.
        if not any(model.get('name') == model_name for model in local_models):
            logging.info(f"Ollama model '{model_name}' not found locally. Pulling it now...")
            # If the model is not found, pull it from the Ollama Hub.
            pull_model_with_progress(model_name)
            logging.info(f"Successfully pulled Ollama model '{model_name}'.")
    except Exception as e:
        # Handle any exceptions that occur during the check or pull process.
        logging.error(f"Failed to check or pull Ollama model '{model_name}': {e}")
        raise

# --- Ticket Triage Functions ---

def triage_ticket_ollama(ticket_content: str) -> str:
    """
    Uses a locally running Ollama model to triage an IT support ticket.

    Args:
        ticket_content: The raw text content of the IT ticket.

    Returns:
        A string containing the triage report in markdown format, or an error message.
    """
    # Get the name of the Ollama model from the environment variables.
    ollama_model = os.getenv("OLLAMA_MODEL")
    # Ensure the model is specified.
    if not ollama_model:
        raise ValueError("OLLAMA_MODEL environment variable not set.")
    
    # Define the detailed prompt for the AI model.
    prompt = f"""
    You are an expert IT support ticket triaging system. Your task is to analyze the following IT ticket and provide a structured triage report.

    The triage report must include the following sections:
    - **Urgency**: (e.g., Low, Medium, High, Critical)
    - **Category**: (e.g., Hardware, Software, Network, Account, Other)
    - **Summary**: A brief, one-sentence summary of the issue.
    - **Next Step**: Propose a concrete next action. This should be a numbered list of 1-3 clear, actionable steps.
    - **New Status**: Based on the "Next Step", set the status to one of the following: "unclear" (if more information is needed), "pending next step" (if the user needs to do something), or "closed" (if no action is required).

    Here is the ticket:
    ---
    {ticket_content}
    ---

    Please provide the triage report in markdown format.
    """
    logging.info(f"Sending ticket to Ollama ({ollama_model}) for triage...")
    try:
        # Send the prompt to the Ollama API.
        response = ollama.chat(
            model=ollama_model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        logging.info("Successfully received triage report from Ollama.")
        # Extract and return the content of the AI's response.
        return response['message']['content']
    except Exception as e:
        # Handle any errors that occur during the API call.
        logging.error(f"Error during Ollama triage: {e}")
        return f"Error during Ollama triage: {e}"

def triage_ticket_gemini(ticket_content: str) -> str:
    """
    Uses the Google Gemini API to triage an IT support ticket.

    Args:
        ticket_content: The raw text content of the IT ticket.

    Returns:
        A string containing the triage report in markdown format, or an error message.
    """
    # The prompt is the same as for the Ollama function, ensuring consistent behavior.
    prompt = f"""
    You are an expert IT support ticket triaging system. Your task is to analyze the following IT ticket and provide a structured triage report.

    The triage report must include the following sections:
    - **Urgency**: (e.g., Low, Medium, High, Critical)
    - **Category**: (e.g., Hardware, Software, Network, Account, Other)
    - **Summary**: A brief, one-sentence summary of the issue.
    - **Next Step**: Propose a concrete next action. This should be a numbered list of 1-3 clear, actionable steps.
    - **New Status**: Based on the "Next Step", set the status to one of the following: "unclear" (if more information is needed), "pending next step" (if the user needs to do something), or "closed" (if no action is required).

    Here is the ticket:
    ---
    {ticket_content}
    ---

    Please provide the triage report in markdown format.
    """
    logging.info("Sending ticket to Gemini for triage...")
    try:
        # The genai client automatically finds the GOOGLE_API_KEY environment variable.
        client = genai.Client()
        
        # Send the prompt to the Gemini API.
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Use a specific, recommended model.
            contents=prompt
        )
        logging.info("Successfully received triage report from Gemini.")
        # Handle the case where the API returns an empty response.
        return response.text or "Error: Empty response from Gemini."
    except Exception as e:
        # Handle any errors that occur during the API call.
        logging.error(f"Error during Gemini triage: {e}")
        return f"Error during Gemini triage: {e}"

# --- Main Execution ---

def main() -> None:
    """
    The main function of the script. It parses command-line arguments,
    reads tickets from a directory, triages them using the selected AI model,
    and saves the triaged tickets to a new directory.
    """
    # Set up the command-line argument parser.
    parser = argparse.ArgumentParser(
        description="AI-Powered IT Ticket Triage Workflow.\nThis script processes markdown tickets from the 'tickets-original' directory, triages them using a specified AI model, and saves the results in the 'tickets-triaged' directory.",
        formatter_class=argparse.RawTextHelpFormatter  # Preserve formatting in the help message.
    )
    # Add the --model argument to choose between 'ollama' and 'gemini'.
    parser.add_argument(
        '--model',
        type=str,
        choices=['ollama', 'gemini'],
        default='ollama',
        help="The model to use for triaging tickets.\n"
             "  - ollama: Use the locally running Ollama service. Requires OLLAMA_MODEL in .env.\n"
             "  - gemini: Use the Google Gemini API. Requires GOOGLE_API_KEY in .env."
    )
    # Parse the arguments provided by the user.
    args = parser.parse_args()

    # If using Ollama, ensure the specified model is available locally.
    if args.model == 'ollama':
        ollama_model = os.getenv("OLLAMA_MODEL")
        if not ollama_model:
            raise ValueError("OLLAMA_MODEL environment variable not set for the ollama model.")
        ensure_ollama_model_available(ollama_model)

    # Define the directories for original and triaged tickets.
    original_dir = 'tickets-original'
    triaged_dir = 'tickets-triaged'

    # Create the triaged directory if it doesn't already exist.
    if not os.path.exists(triaged_dir):
        os.makedirs(triaged_dir)

    logging.info(f"Starting ticket triage process using the '{args.model}' model.")

    # Loop through all files in the original tickets directory.
    for filename in os.listdir(original_dir):
        # Process only markdown files.
        if filename.endswith('.md'):
            # Construct the full paths for the original and triaged files.
            original_path = os.path.join(original_dir, filename)
            triaged_path = os.path.join(triaged_dir, filename)

            logging.info(f"Reading ticket: {filename}")
            # Read the content of the original ticket.
            with open(original_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Append a "new" status to the original content.
            ticket_with_status = f"{original_content}\n\n---\n\n**Status:** new"

            # Triage the ticket using the selected model.
            if args.model == 'ollama':
                triage_report = triage_ticket_ollama(original_content)
            else:
                triage_report = triage_ticket_gemini(original_content)

            # Combine the original content, status, and triage report.
            updated_content = f"{ticket_with_status}\n\n---\n\n## Triage\n\n{triage_report}"

            logging.info(f"Writing triaged ticket to: {triaged_path}")
            # Write the updated content to the new triaged file.
            with open(triaged_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

    logging.info("All tickets have been processed.")

# Standard Python entry point.
if __name__ == "__main__":
    main()