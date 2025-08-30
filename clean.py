# Import necessary standard libraries
import os    # Used for interacting with the operating system, like removing files.
import glob  # Used to find all pathnames matching a specified pattern.

def clean_triaged_directory() -> None:
    """
    Removes all files from the 'tickets-triaged' directory.
    This is a utility script to reset the state of the triaged tickets folder.
    """
    # Define the path to the directory to be cleaned.
    triaged_dir = 'tickets-triaged'
    
    # Use glob to find all files within the specified directory.
    # os.path.join ensures the path is constructed correctly for the current OS.
    files = glob.glob(os.path.join(triaged_dir, '*'))
    
    # Loop through the list of files found.
    for f in files:
        # Remove each file.
        os.remove(f)
        
    # Print a confirmation message to the console.
    print("Cleaned the 'tickets-triaged' directory.")

# Standard Python entry point.
# This ensures the clean_triaged_directory function is called only when the script is executed directly.
if __name__ == "__main__":
    clean_triaged_directory()