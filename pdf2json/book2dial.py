# final version

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env')

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

def generate_prompt1(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation):
    prompt = ( "Task: You are a student preparing to ask questions about a textbook subsection to a teacher. "
    "Your goal is to uncover the key information from this subsection. Based on the teacher's responses, "
    "you'll further inquire to get a comprehensive understanding. Make sure to ask specific questions about "
    "the subsection's content and avoid repeating queries from prior discussions.\n\n"
    "Information Provided:\n"
    f"1. **Section Title:** {chapter_title}\n"
    f"2. **Subsection Title:** {section_title}\n"

    "Previous Conversation:\n"
    f"{previous_conversation}\n\n"
    "*Note:* Frame your questions considering the information above and ensure they're relevant to the content. Do not ask question about information you already have. Only ask one question at a time.\n\n"
    "Expected Output: Please phrase your question as a string.")
    
    return prompt
def generate_prompt2(chapter_title, section_title,context, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation,question):
    prompt = ("Task: You are a teacher preparing to answer a student's question about a subsection of a textbook. "
    f"The student's question is: {question}. Provide a concise, specific response, ensuring it's not a summary and "
    f"distinct from any previous answers you've given.\n\n"
    f"Information Provided:\n"
    f"1. **Section Title:** {chapter_title}\n"
    f"2. **Subsection Title:** {section_title}\n"
    f"3. **Subsection Content:** {context}\n"
    f"4. **Section Summary:** {chapter_summary}\n"
    f"5. **Bold Terms in Section:** {bold_terms}\n"
    f"6. **Learning Objectives:** {learning_objectives}\n"
    f"7. **Concepts in Section:** {concepts}\n"
    f"8. **Section Introduction:** {introduction}\n\n"
    f"Previous Conversation:\n"
    f"{previous_conversation}\n\n"
    f"*Note:* When crafting your response, consider all the information above. Be sure your answer directly "
    f"addresses the student's question and is not a repetition of prior information.\n\n"
    f"Expected Output: Please phrase your answer as a string.")
    
    return prompt

def generate_response0(prompt, model):
    while True:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
             )
            return completion
        except:
            print("Error occurred while generating response. Retrying in 2 seconds...")
            time.sleep(2)

def generate_question(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model):
    prompt = generate_prompt1(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation)
    completion = generate_response0(prompt, model)
    question = completion.choices[0].message.content
    # escaped_content = question.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    return question
def generate_answer(question, context, chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model):
    if not question:
        print('Empty question was given as input.')
        return None
    prompt = generate_prompt2(chapter_title, section_title, context, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation,question)
    completion = generate_response0(prompt, model)
    answer = completion.choices[0].message.content
    # escaped_content = answer_data.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    return answer

# Can use different models to do this task, for example: gpt-4o
model_name = "gpt-4o-mini"

def make_json_friendly(s):
    # Escape backslashes
    s = s.replace("\\", "\\\\")
    # Escape double quotes
    s = s.replace('"', '\\"')
    return s

def generate_dialog_for_section(section, model_name, turns=12):
    chapter_title = section.get("title", "")
    paragraphs = section.get("paragraphs", [])
    context = paragraphs[0]["context"] if paragraphs else ""
    
    # Safely access 'bold_terms' and handle case where it's missing
    bold_terms = ', '.join(term.strip() for term in section.get('bold_terms', []))
    
    section_title = section.get("section_title", "")
    chapter_summary = section.get('chapter_summary', "")
    
    # Safely access other potentially missing keys
    learning_objectives = ', '.join(objective.strip() for objective in section.get('chapter_learning_objectives', []))
    
    # Handle potential missing 'chapter_concept' key
    if 'chapter_concept' in section and section['chapter_concept']:
        concepts = ', '.join(concept['name'].strip() for concept in section['chapter_concept'])
    else:
        concepts = ""
    
    introduction = section.get('chapter_introduction', "")
    previous_conversation = ""
    
    
    dialogs = []
    for _ in range(turns // 2):
        question = generate_question(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model_name)
        # print('question:',question)
        
        answer = generate_answer(question, context, chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model_name)
        # print('answer:',answer)

        
        dialogs.append({
            "question": question,
            "answer": answer
        })
        previous_conversation += f"\nStudent: {question}\nTeacher: {answer}"
    
    return dialogs

def append_to_jsonl(dialog, filename):
    with open(filename, "a") as outfile:
        outfile.write(json.dumps(dialog))
        outfile.write("\n")

def check_current_progress(filename):
    """
    Check the current progress by counting how many subsections have been completed.
    Return the index of the next subsection to process.
    """
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            completed_sections = len(lines)
        return completed_sections
    except FileNotFoundError:
        return 0

def generate_and_save_dialogs(data, model_name, filename, turns=12):
    # Check current progress
    all_dialogs = []
    start_section = check_current_progress(filename)
    print('start_section',start_section)
    for idx, section in enumerate(data["data"][start_section:], start=start_section):
        print(f"Generating dialogs for subsection {idx + 1}/{len(data['data'])}")
        dialogs = generate_dialog_for_section(section, model_name, turns)
        dialog_data = {
            "title": section["title"],
            "context":section["paragraphs"][0]['context'],
            "dialogs": dialogs
            
        }
        append_to_jsonl(dialog_data, filename)
        all_dialogs.append(dialog_data)

    print(f"Generation finished, dialogs saved to {filename}")
    return all_dialogs

# Function to process JSON data directly without file reading
def process_json_data(json_data, output_filename="test_science_low_info.jsonl", turns=12):
    """
    Process JSON data directly without reading from a file.
    
    Args:
        json_data (dict): The JSON data to process
        output_filename (str, optional): Filename to save dialogs. If None, returns the dialogs without saving.
        turns (int, optional): Number of dialog turns to generate. Defaults to 12.
        
    Returns:
        If output_filename is provided, saves dialogs to file and returns None.
        If output_filename is None, returns a list of dialog data.
    """
    # Make sure output_filename is an absolute path
    if not os.path.isabs(output_filename):
        # Save in the pdf2json/output directory
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, output_filename)
        
    print(f"Will save dialogs to: {output_filename}")
    
    # Generate and save dialogs to file
    all_dialogs = generate_and_save_dialogs(json_data, model_name, output_filename, turns)
    return all_dialogs
