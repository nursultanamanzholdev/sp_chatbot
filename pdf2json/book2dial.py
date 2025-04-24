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
            print(f"[Book2Dial] Sending request to OpenAI API with model: {model}")
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
             )
            print(f"[Book2Dial] Successfully received response from OpenAI API")
            return completion
        except Exception as e:
            print(f"[Book2Dial] Error occurred while generating response: {str(e)}. Retrying in 2 seconds...")
            time.sleep(2)

def generate_question(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model):
    prompt = generate_prompt1(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation)
    completion = generate_response0(prompt, model)
    question = completion.choices[0].message.content
    # escaped_content = question.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    return question
def generate_answer(question, context, chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model):
    if not question:
        print('[Book2Dial] Empty question was given as input.')
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
    print(f"[Book2Dial] Generating dialog for section: {section.get('title', 'Unknown section')}")
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
    for i in range(turns // 2):
        print(f"[Book2Dial] Generating dialog turn {i+1}/{turns//2}")
        question = generate_question(chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model_name)
        print(f"[Book2Dial] Generated question: {question[:50]}...")
        
        answer = generate_answer(question, context, chapter_title, section_title, chapter_summary, bold_terms, learning_objectives, concepts, introduction, previous_conversation, model_name)
        print(f"[Book2Dial] Generated answer: {answer[:50]}...")

        
        dialogs.append({
            "question": question,
            "answer": answer
        })
        previous_conversation += f"\nStudent: {question}\nTeacher: {answer}"
    
    print(f"[Book2Dial] Completed dialog generation with {len(dialogs)} turns")
    return dialogs

# Function to process JSON data directly without file reading
def process_json_data(json_data, turns=12):
    """
    Process JSON data directly to generate dialogs without saving to files.
    
    Args:
        json_data (dict): The JSON data to process
        turns (int, optional): Number of dialog turns to generate. Defaults to 12.
        
    Returns:
        dict: A dictionary containing all generated dialogs with metadata.
    """
    print(f"[Book2Dial] Starting dialog generation from JSON data")
    
    all_dialogs = []
    total_sections = len(json_data.get("data", []))
    
    for idx, section in enumerate(json_data.get("data", [])):
        print(f"[Book2Dial] Processing section {idx + 1}/{total_sections}: {section.get('title', 'Unknown section')}")
        
        try:
            dialogs = generate_dialog_for_section(section, model_name, turns)
            dialog_data = {
                "title": section["title"],
                "context": section["paragraphs"][0]['context'] if section.get("paragraphs") else "",
                "dialogs": dialogs
            }
            all_dialogs.append(dialog_data)
        except Exception as e:
            print(f"[Book2Dial] Error processing section {idx + 1}: {str(e)}")
            # Continue with the next section rather than failing completely
            continue

    print(f"[Book2Dial] Dialog generation complete: {len(all_dialogs)} sections processed")
    
    # Return the results directly without saving to a file
    result = {
        "status": "complete",
        "sections": all_dialogs,
        "total_sections": total_sections,
        "processed_sections": len(all_dialogs)
    }
    
    return result
