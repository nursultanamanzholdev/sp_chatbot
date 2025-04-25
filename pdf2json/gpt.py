import os
import sys
import json
import shutil
import random
import uuid
from time import sleep
from pprint import pprint
from .util import parse_json_string, process_image_to_json, resize_images, encode_images
from .util import split_images, extract_pages_as_images, clean_up_tmp_images_folder
from .util import get_image_files, process_text_to_structured_json


def process(filename, folder, api_key, user_prompt: str = None,
            model: str = "gpt-4.1", verbose: bool = False, cleanup: bool = True):
    """
    Process the PDF file and extract data from the images using OpenAI's multimodal model.
    Combines all outputs into a single structured JSON object optimized for children's language learning.

    Args:
        filename (str): The name of the PDF file.
        folder (str): The folder path where the PDF file is located.
        api_key (str): The API key for accessing the OpenAI API.
        user_prompt (str, optional): Custom prompt for the model. Defaults to None.
        model (str, optional): The OpenAI model to use. Defaults to "gpt-4.1".
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
        cleanup (bool, optional): Whether to clean up temporary files. Defaults to True.
        
    Returns:
        dict: The combined JSON data structure containing all extracted information.
    """
    os.chdir(folder)
    basename = os.path.basename(filename)
    file_title = os.path.splitext(basename)[0] 

    tmp_images_folder = f"./{basename}_tmp_images"
    shutil.rmtree(tmp_images_folder, ignore_errors=True)
    os.makedirs(tmp_images_folder, exist_ok=True)
    
    if verbose:
        print(f"[PDF Processing] Starting PDF to JSON conversion for '{basename}'")
    
    if verbose:
        print(f"[PDF Processing] Extracting images from PDF file")
    image_encodings, image_files, filaname_image = do_images(
        filename, tmp_images_folder, verbose=verbose)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    default_prompt = """
    You are an expert educator specializing in children's second language acquisition.
    Extract all visible text content from this image, focusing on content that would be 
    valuable for children aged 6-8 who are learning a second language.
    Preserve paragraph structure and format your response as plain text.
    """

    structured_prompt = """
    You are an expert in childhood education with specialization in second language acquisition for young children ages 6-8.
    
    Analyze this textbook page and transform the content into child-appropriate learning material. Your task is to:
    
    1. Identify the key topic on the page (like animals, numbers, science concepts)
    2. Extract or create SIMPLE paragraphs suitable for children age 6-8 learning a second language
    3. Find important vocabulary words and provide very simple definitions
    4. Create engaging fun facts from the content (simplify complex information)
    5. Develop simple comprehension questions about the topic
    6. Identify language patterns that could help with basic grammar
    7. Describe any visual elements mentioned or shown
    
    IMPORTANT: Always simplify the language drastically. Use very basic vocabulary and short sentences.
    Limit sentences to 5-10 words when possible. Focus on concrete concepts rather than abstract ones.
    
    Format your response in this exact JSON structure:
    
    {
      "paragraphs": [
        {
          "context": "Simple paragraph using basic words and short sentences. Focus on one idea only.",
          "id": "unique_id per context as integer"
        }
      ],
      "section_title": "Simple topic name (animals, numbers, etc.)",
      "vocabulary": [
        {
          "word": "simple word",
          "child_friendly_definition": "what this word means using very basic words",
          "example_sentence": "This is a simple sentence."
        }
      ],
      "fun_facts": [
        "Short interesting fact in very simple words."
      ],
      "comprehension_questions": [
        "Simple question about the main idea?"
      ],
      "language_practice": [
        {
          "pattern": "Simple pattern like 'I see a...'",
          "examples": ["I see a dog.", "I see a cat."]
        }
      ],
      "visual_elements": [
        "Simple description of picture or diagram mentioned in text."
      ]
    }
    
    Remember:
    1. ALL text must be appropriate for a 6-8 year old learning a second language
    2. Use ONLY basic vocabulary (words a 6-year-old would know)
    3. Keep sentences very short and simple
    4. Focus on concrete, visual concepts children can easily understand
    5. If the content is too advanced, transform it into something simpler on the same topic
    6. EVERY category must be filled with appropriate content
    """

    prompt = structured_prompt
    if user_prompt:
        prompt = user_prompt
        if verbose:
            print(f"[PDF Processing] Using custom prompt: {prompt}\n")

    all_extracted_data = []
    all_text_content = ""

    try:
        for index, image_encoding in enumerate(image_encodings):
            if verbose:
                print(f"[PDF Processing] Processing image {index + 1} of {len(image_encodings)} - sending request to OpenAI API")

            had_errors = False
            json_file_data = None

            response_dict = process_image_to_json(
                image_encoding, prompt, headers, model)

            if "error" in response_dict.keys():
                if verbose:
                    print(f"[PDF Processing] OpenAI returned error: {response_dict['error']}")
                had_errors = True
            else:
                if verbose:
                    print(f"[PDF Processing] Successfully received response from OpenAI API for image {index + 1}")
                
                text_content = response_dict["choices"][0]["message"]["content"]
                
                json_file_data = parse_json_string(text_content)

                if json_file_data is None:
                    if verbose:
                        print(f"[PDF Processing] Response is not valid JSON, storing as raw text")
                    json_file_data = {"text": text_content, "page": index + 1}
                
                all_extracted_data.append(json_file_data)
                all_text_content += f"\n\n--- PAGE {index + 1} ---\n\n{text_content}"

        if verbose:
            print(f"[PDF Processing] Creating combined structured JSON from {len(all_extracted_data)} processed images")
            
        combined_json = create_combined_json(
            all_extracted_data, file_title, all_text_content, headers, model, verbose=verbose)

        if cleanup:
            if verbose:
                print(f"[PDF Processing] Cleaning up temporary files")
            if os.path.exists(tmp_images_folder):
                shutil.rmtree(tmp_images_folder)
        
        if verbose:
            print(f"[PDF Processing] PDF to JSON conversion complete")
            
        return combined_json
                
    except Exception as e:
        print(f"[PDF Processing] Error during PDF processing: {str(e)}")
        if cleanup and os.path.exists(tmp_images_folder):
            shutil.rmtree(tmp_images_folder)
        raise


def create_combined_json(extracted_data, title, all_text_content, headers, model, verbose=False):
    """
    Creates a combined structured JSON from all extracted data.
    
    Args:
        extracted_data (list): List of all extracted data from individual pages
        title (str): Title for the document
        all_text_content (str): Combined text content from all pages
        headers (dict): API request headers
        model (str): OpenAI model to use
        verbose (bool): Whether to print verbose output
        
    Returns:
        dict: Combined structured JSON
    """
    combined_json = {
        "data": [
            {
                "title": title,
                "paragraphs": [],
                "section_title": "",
                "vocabulary": [],
                "fun_facts": [],
                "comprehension_questions": [],
                "language_practice": [],
                "visual_elements": []
            }
        ]
    }
    
    structured_count = 0
    
    for page_index, item in enumerate(extracted_data):
        # Check if this is empty content
        if isinstance(item, dict) and "context" in item and (not item["context"] or (isinstance(item["context"], list) and len(item["context"]) == 0)):
            continue  # Skip empty content
            
        # Check if this looks like structured data for children's language learning
        if isinstance(item, dict) and any(key in item for key in ["paragraphs", "section_title", "vocabulary", "fun_facts"]):
            structured_count += 1
            
            # Integrate each field into the combined structure
            if "paragraphs" in item and isinstance(item["paragraphs"], list):
                for para in item["paragraphs"]:
                    if isinstance(para, dict) and "context" in para and para["context"]:  # Only add if not empty
                        # Generate ID if missing
                        if "id" not in para:
                            para["id"] = f"C_{random.randint(100000, 999999)}_1"
                        combined_json["data"][0]["paragraphs"].append(para)
            
            # For single text paragraph that isn't in list form
            elif "context" in item and item["context"]:  # Only add if not empty
                paragraph = {
                    "context": item["context"],
                    "id": f"C_{random.randint(100000, 999999)}_default"
                }
                combined_json["data"][0]["paragraphs"].append(paragraph)
                
            # Process section title (use the first non-empty one found if none exists yet)
            if "section_title" in item and item["section_title"] and not combined_json["data"][0]["section_title"]:
                combined_json["data"][0]["section_title"] = item["section_title"]
            
            # Process vocabulary - merge without duplicates
            if "vocabulary" in item and isinstance(item["vocabulary"], list):
                for vocab in item["vocabulary"]:
                    if isinstance(vocab, dict) and "word" in vocab:
                        # Check if this vocabulary word is already in our list
                        existing = False
                        for v in combined_json["data"][0]["vocabulary"]:
                            if v["word"].lower() == vocab["word"].lower():
                                existing = True
                                break
                        
                        if not existing:
                            combined_json["data"][0]["vocabulary"].append(vocab)
            
            # Process fun facts - merge without duplicates
            if "fun_facts" in item and isinstance(item["fun_facts"], list):
                for fact in item["fun_facts"]:
                    if fact and fact not in combined_json["data"][0]["fun_facts"]:
                        combined_json["data"][0]["fun_facts"].append(fact)
                
            # Process comprehension questions - merge without duplicates
            if "comprehension_questions" in item and isinstance(item["comprehension_questions"], list):
                for question in item["comprehension_questions"]:
                    if question and question not in combined_json["data"][0]["comprehension_questions"]:
                        combined_json["data"][0]["comprehension_questions"].append(question)
                        
            # Process language practice - merge without duplicates
            if "language_practice" in item and isinstance(item["language_practice"], list):
                for practice in item["language_practice"]:
                    if isinstance(practice, dict) and "pattern" in practice:
                        # Check if this pattern is already in our list
                        existing = False
                        for p in combined_json["data"][0]["language_practice"]:
                            if p["pattern"].lower() == practice["pattern"].lower():
                                existing = True
                                break
                        
                        if not existing:
                            combined_json["data"][0]["language_practice"].append(practice)
                            
            # Process visual elements - merge without duplicates
            if "visual_elements" in item and isinstance(item["visual_elements"], list):
                for element in item["visual_elements"]:
                    if element and element not in combined_json["data"][0]["visual_elements"]:
                        combined_json["data"][0]["visual_elements"].append(element)
    
    # Method 2: If we don't have structured data from individual pages,
    # send all text to get structured by the model
    if structured_count < len(extracted_data) / 2 and len(all_text_content) > 0:
        if verbose:
            print("Not enough structured data found, processing all text content together...")
            
        # Create a prompt to structure all the text for children's language learning
        structure_prompt = f"""
        You are an expert in childhood education with specialization in second language acquisition for young children ages 6-8.
        
        I'll provide you with textbook content that needs to be transformed into child-appropriate learning material.
        Transform this content according to this exact JSON format:
        
        {{
            "data": [
                {{
                    "title": "{title}",
                    "paragraphs": [
                        {{
                            "context": "Simple paragraph using basic words. Max 10 words per sentence.",
                            "id": "unique_id per context of a paragraph as integer"
                        }}
                    ],
                    "section_title": "Simple topic name like 'animals' or 'numbers'",
                    "vocabulary": [
                        {{
                            "word": "simple word that children would use",
                            "child_friendly_definition": "what this word means using very basic words",
                            "example_sentence": "Very simple sentence using this word."
                        }}
                    ],
                    "fun_facts": [
                        "Short interesting fact using very simple words."
                    ],
                    "comprehension_questions": [
                        "Simple question a child could answer?"
                    ],
                    "language_practice": [
                        {{
                            "pattern": "Basic pattern like 'I see a...'",
                            "examples": ["I see a dog.", "I see a cat."]
                        }}
                    ],
                    "visual_elements": [
                        "Simple description of picture or diagram that might help."
                    ]
                }}
            ]
        }}
        
        Here is the textbook content to transform:
        
        {all_text_content[:15000]}
        
        IMPORTANT:
        1. DRASTICALLY simplify ALL language to be appropriate for a 6-8 year old learning a second language
        2. Focus on concrete concepts children can easily understand and visualize
        3. Use only basic vocabulary a child would know in their first language
        4. Keep sentences very short (5-10 words when possible)
        5. Generate at least 5 vocabulary items, 3 fun facts, 3 questions, and 2 language patterns
        6. If content is too advanced, transform it into something simpler on the same general topic
        7. EVERY category must be filled with appropriate content
        
        Return ONLY valid JSON that matches the format above.
        """
        
        # We might need to truncate the text if it's too long for the model's context
        try:
            response = process_text_to_structured_json(structure_prompt, headers, model)
            
            if "error" not in response:
                structured_json = parse_json_string(response["choices"][0]["message"]["content"])
                if structured_json:
                    return structured_json
                else:
                    if verbose:
                        print("Failed to parse structured JSON from response, using default structure")
        except Exception as e:
            if verbose:
                print(f"Error processing text to structured JSON: {e}")
    
    # Check if any of the required fields are empty and populate with defaults if necessary
    if len(combined_json["data"][0]["paragraphs"]) == 0:
        combined_json["data"][0]["paragraphs"].append({
            "context": f"This is about {title}. We are learning simple words and ideas.",
            "id": f"C_{random.randint(100000, 999999)}_default"
        })
    
    if not combined_json["data"][0]["section_title"]:
        combined_json["data"][0]["section_title"] = title.replace("-", " ").title()
    
    if len(combined_json["data"][0]["vocabulary"]) == 0:
        combined_json["data"][0]["vocabulary"].append({
            "word": "learn",
            "child_friendly_definition": "to get new knowledge or skills",
            "example_sentence": "I like to learn new words."
        })
    
    if len(combined_json["data"][0]["fun_facts"]) == 0:
        combined_json["data"][0]["fun_facts"].append(
            f"Learning new words can be fun!"
        )
    
    if len(combined_json["data"][0]["comprehension_questions"]) == 0:
        combined_json["data"][0]["comprehension_questions"].append(
            "What new word did you learn today?"
        )
    
    if len(combined_json["data"][0]["language_practice"]) == 0:
        combined_json["data"][0]["language_practice"].append({
            "pattern": "I can...",
            "examples": ["I can read.", "I can write."]
        })
    
    if len(combined_json["data"][0]["visual_elements"]) == 0:
        combined_json["data"][0]["visual_elements"].append(
            "Picture showing different learning activities."
        )
    
    return combined_json


def do_images(filename, tmp_images_folder, verbose=False):
    """
    Extracts images from a PDF file and performs various operations on them.

    Args:
        filename (str): The name of the PDF file.
        tmp_images_folder (str): The directory for temporary image storage.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        list: A list of image encodings in base64 format.
    """

    # extract images from the PDF
    if verbose:
        print(f"Extracting images from the PDF '{filename}'...")

    filaname_image = ''.join(e for e in filename if e.isalnum())

    try:
        extract_pages_as_images(filename, tmp_images_folder, filaname_image)

    except Exception as error:
        print(f"An error occurred: {error}")
        print("Failed to covert pages to image for model processing")
        # exit the program on error
        sys.exit()

    file_list = os.listdir(tmp_images_folder)
    if verbose:
        pprint(file_list)

    if len(file_list) == 0:
        print(f"No images found in the directory '{tmp_images_folder}'.")
        sys.exit()

    image_files = get_image_files(tmp_images_folder)

    # Resize images if they are too large
    resize_images(image_files, tmp_images_folder, verbose=verbose)

    # split images if they are too large
    split_images(image_files, tmp_images_folder, verbose=verbose)

    # update the list of images caused by splitting
    image_files = get_image_files(tmp_images_folder)

    # Encode the images to base64
    image_encodings = encode_images(
        image_files, tmp_images_folder, verbose=verbose)

    return image_encodings, image_files, filaname_image