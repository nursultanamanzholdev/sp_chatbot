import json
import os
import re
import mimetypes
import base64
import shutil
import requests
from PIL import Image
import pypdfium2 as pdfium
from split_image import split_image as si


def parse_json_string(json_string, verbose=False):
    def remove_comments(code):
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    try:
        json_string = remove_comments(json_string)
        if "```json" in json_string:
            start = json_string.index("```json") + len("```json")
            end = json_string.index("```", start)
            json_string = json_string[start:end]

        if verbose:
            print(json_string)

        json_data = json.loads(json_string)

        return json_data
    except json.JSONDecodeError as error:
        print(f"Invalid JSON string ({error})")
        return None


def process_image_to_json(image_encoding, prompt, headers, model="gpt-4.1"):
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_encoding
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions', headers=headers,
        timeout=120, data=json.dumps(data))
    
    response_dict = response.json()

    return response_dict


def extract_pages_as_images(pdf_file, tmp_images_folder, filaname_image="image"):
    pdf = pdfium.PdfDocument(pdf_file)
    n_pages = len(pdf)
    for page_number in range(n_pages):
        page = pdf.get_page(page_number)
        image_path = os.path.join(tmp_images_folder, f"{filaname_image}_{page_number+1}.jpg")
        bitmap = page.render(
            scale=1,
            rotation=0,
            crop=(0, 0, 0, 0)
        )

        pil_image = bitmap.to_pil()
        pil_image.save(image_path)

    return os.listdir(tmp_images_folder)


def resize_images(image_files, tmp_images_folder, verbose=False):
    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        with Image.open(image_path) as image:
            width, height = image.size
            if width > 1024:
                if verbose:
                    print(f"Resizing {image_file} from {width}x{height} to 1024x{int(height * (1024 / width))}")
                resized_image = image.resize(
                    (1024, int(height * (1024 / width))))
                
                resized_image.save(image_path)


def split_images(image_files, tmp_images_folder, verbose=False):
    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        if verbose:
            print(f"split to {image_path}")

        with Image.open(image_path) as image:
            _, height = image.size
            if height > 1024:
                num_splits = int(height / 1024)
                if verbose:
                    print(f"Splitting {image_file} into {num_splits} images")

                si(image_path, num_splits, 1, should_square=False,
                   output_dir=tmp_images_folder, should_cleanup=True, should_quiet=not verbose)


def encode_images(image_files, tmp_images_folder, verbose=False):
    image_encodings = []
    for image_file in image_files:
        mime_type, _ = mimetypes.guess_type(image_file)
        with open(os.path.join(tmp_images_folder, image_file), "rb") as image:
            image_data = image.read()
            image_b64 = base64.b64encode(image_data).decode("utf-8")
            image_encoding = f"data:{mime_type};base64,{image_b64}"
            image_encodings.append(image_encoding)
            if verbose:
                print(image_file,  f"data:{mime_type};",
                      f"size: {len(image_data) / 1024:.2f} KB")
    
    return image_encodings


def get_image_files(directory):
    file_list = os.listdir(directory)
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    image_files = [file for file in file_list if any(
        file.endswith(ext) for ext in image_extensions)]

    filtered_image_files = []
    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        if not is_solid_color(image_path):
            filtered_image_files.append(image_file)

    image_files = filtered_image_files
    image_files.sort()

    return image_files


def is_solid_color(image_path):
    with Image.open(image_path) as img:
        first_pixel_color = img.getpixel((0, 0))

        for pixel in img.getdata():
            if pixel != first_pixel_color:
                return False

        return True


def process_text_to_structured_json(prompt, headers, model="gpt-4.1"):
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4096
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions', headers=headers,
        timeout=180, data=json.dumps(data))
    
    return response.json()


def clean_up_tmp_images_folder(tmp_images_folder):
    if not os.path.exists(tmp_images_folder):
        return
    
    shutil.rmtree(tmp_images_folder, ignore_errors=True)