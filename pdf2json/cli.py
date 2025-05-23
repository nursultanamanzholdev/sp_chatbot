"""
cli.py

This module provides a command line interface for processing PDFs with OpenAI's multimodal models.
"""

import os
from .gpt import process

def main(pdf: str, prompt_file: str = None, openai_key: str = None,
         model="gpt-4.1", verbose: bool = False,
         cleanup: bool = False):
    """
    Main function for the command line interface.

    Parameters:
    pdf (str): Path to the PDF file to process.
    prompt_file (str, optional): Path to a file containing a prompt for the model.
    openai_key (str, optional): OpenAI API key. If not provided, it will be read 
                                from the environment.
    model (str, optional): Model to use. Default is "gpt-4.1".
    verbose (bool, optional): If True, print additional debug information. Default is False.
    cleanup (bool, optional): If True, cleanup temporary files after processing. Default is False.
    """

    if not os.path.exists(pdf):
        print(f"File {pdf} not found")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    
    # If the openai_key parameter is provided, use it instead
    if openai_key:
        api_key = openai_key

    folder = os.path.dirname(pdf)
    filename = os.path.basename(pdf)

    if verbose:
        print(f"PDF to extract {pdf}")
        print(f"Folder {folder}")
        print(f"Filename {filename}")

    user_prompt = None
    if prompt_file and os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as file:
            # Read the prompt from the file
            user_prompt = file.read().strip() + "\n\n"

    process(filename, folder, user_prompt=user_prompt,
            api_key=api_key, model=model, verbose=verbose,
            cleanup=cleanup)