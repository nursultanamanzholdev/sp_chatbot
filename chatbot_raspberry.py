import time
import json
import torch
import torchaudio
import os
import pyaudio
import numpy as np
import whisper
from piper.voice import PiperVoice
import sounddevice as sd
from openai import OpenAI
import random
import requests


client = OpenAI(
    api_key= "",
)

url = "http://localhost:11434/api/generate"
headers = {
    "Content-Type": "application/json"
}


def llm_response(prompt):
    data = {
        "model": "cas/llama-3.2-1b-instruct",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        rez = response.text
        data = json.loads(rez)
        val = data['response']
        return val
    else:
        print("Error", response.status_code, response.text)
        return "Error generating response"

print('starting model loading')
model = whisper.load_model("base.en")  
print('finished model loading')

voicedir = os.path.expanduser('/home/user/Desktop/sp_chatbot/')  
model11 = os.path.join(voicedir, "en_US-kathleen-low.onnx")  
voice = PiperVoice.load(model11)

chunk = 1024
sample_format = pyaudio.paInt16  
channels = 2  
fs = 44100 


def load_language_learning_content(parent_prompt):
    try:
        language_levels = ["Beginner", "Elementary"]
        
        selected_level = random.choice(language_levels)
        
        system_prompt = f"You are an expert English language curriculum designer. Create an engaging conversational English lesson appropriate for a non-English speaker on the topic of {parent_prompt}."
        user_prompt = f"Create a short English conversation practice lesson for {selected_level} level students. The lesson should focus on practical, everyday English conversation skills. Format the response as a JSON object with the following structure:\n\n{{\"title\": \"Lesson title\", \"level\": \"{selected_level}\", \"conversations\": [{{\"prompt\": \"Question or instruction for student\", \"expected_responses\": [\"possible response 1\", \"possible response 2\"], \"follow_up\": \"Encouraging feedback and additional information\"}}]}}"
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = llm_response(full_prompt)
        
        try:
            lesson_data = json.loads(response)
            return [lesson_data]
        except json.JSONDecodeError:
            print("Failed to parse JSON response from Ollama. Using fallback content.")
            return [{
                "title": "Basic English Greetings",
                "level": "Beginner",
                "conversations": [
                    {
                        "prompt": "Let's practice saying hello. How would you greet someone in the morning?",
                        "expected_responses": ["Good morning", "Hello", "Hi"],
                        "follow_up": "Great! 'Good morning' is a perfect greeting for the morning. Can you also say 'Hello' or 'Hi'?"
                    },
                    {
                        "prompt": "Now let's practice introducing yourself. Say: 'My name is...' and add your name.",
                        "expected_responses": ["My name is", "I am", "I'm"],
                        "follow_up": "Excellent! That's how we introduce ourselves in English."
                    },
                    {
                        "prompt": "How would you ask someone their name?",
                        "expected_responses": ["What is your name", "What's your name"],
                        "follow_up": "Perfect! 'What is your name?' or 'What's your name?' is how we ask someone's name."
                    },
                    {
                        "prompt": "Let's practice saying goodbye. How would you say goodbye to someone?",
                        "expected_responses": ["Goodbye", "Bye", "See you later", "See you soon"],
                        "follow_up": "Excellent! Those are all great ways to say goodbye in English."
                    }
                ]
            }]
    except Exception as e:
        print(f"Error generating language learning content: {e}")
        return [{
            "title": "Basic English Greetings",
            "level": "Beginner",
            "conversations": [
                {
                    "prompt": "Let's practice saying hello. How would you greet someone in the morning?",
                    "expected_responses": ["Good morning", "Hello", "Hi"],
                    "follow_up": "Great! 'Good morning' is a perfect greeting for the morning. Can you also say 'Hello' or 'Hi'?"
                },
                {
                    "prompt": "Now let's practice introducing yourself. Say: 'My name is...' and add your name.",
                    "expected_responses": ["My name is", "I am", "I'm"],
                    "follow_up": "Excellent! That's how we introduce ourselves in English."
                },
                {
                    "prompt": "How would you ask someone their name?",
                    "expected_responses": ["What is your name", "What's your name"],
                    "follow_up": "Perfect! 'What is your name?' or 'What's your name?' is how we ask someone's name."
                },
                {
                    "prompt": "Let's practice saying goodbye. How would you say goodbye to someone?",
                    "expected_responses": ["Goodbye", "Bye", "See you later", "See you soon"],
                    "follow_up": "Excellent! Those are all great ways to say goodbye in English."
                }
            ]
        }]

def get_system_prompt(context):
    return f"""You are an educational assistant for children. You're teaching concepts from textbooks.
Your goal is to help kids learn and understand new concepts. 
Keep explanations simple, engaging, and at a level appropriate for a 7-10 year old child.
The following is the context from the textbook that you should use as reference:
{context}"""

def get_language_learning_prompt():
    return """You are an English language tutor for children who are learning English as a second language.
Your goal is to help them practice speaking English through natural, adaptive conversation.
Adapt your language complexity, pace, and teaching style based on how the child responds:
- If they use simple words and short sentences, match that level and gradually introduce new vocabulary.
- If they make grammar mistakes, gently model the correct form without explicitly correcting them.
- If they show confidence, introduce slightly more complex language constructs.
Notice their interests based on their responses and incorporate those topics when possible.
Always be encouraging, patient, and responsive to their unique communication style.
Remember that learning should be fun and engaging for children."""

def evaluate_answer(student_answer, correct_answer, question):
    prompt = f"You are an educational assessment assistant. Your task is to evaluate if a student's answer is correct, partially correct, or incorrect compared to the expected answer. Return 'correct', 'partially_correct', or 'incorrect'.\n\nQuestion: {question}\nExpected answer: {correct_answer}\nStudent answer: {student_answer}\n\nEvaluate if the student's answer is correct, partially correct, or incorrect."
    
    try:
        evaluation = llm_response(prompt).lower()
        
        if "correct" in evaluation and "incorrect" not in evaluation:
            return "correct"
        elif "partially" in evaluation or "partial" in evaluation:
            return "partially_correct"
        else:
            return "incorrect"
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return "error"

def evaluate_language_response(student_response, expected_responses, previous_responses=None):
    prompt = f"""You are an English language assessment assistant for children. 
Your task is to evaluate if a child's response shows understanding of the question and contains appropriate vocabulary, 
even if it doesn't exactly match expected phrases. Consider their language development level.
Return a JSON with:
{{
  "evaluation": "correct" or "partially_correct" or "incorrect",
  "language_level": "beginner" or "elementary" or "intermediate",
  "interests": ["topic1", "topic2"],
  "feedback_focus": "vocabulary" or "grammar" or "pronunciation" or "confidence"
}}

Expected content: {expected_responses}
Student response: {student_response}
Previous responses: {previous_responses if previous_responses else 'None'}

Evaluate if the student's response shows understanding and provide language assessment details."""
    
    try:
        result = llm_response(prompt)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print(f"Error parsing JSON from Ollama response: {result}")
            return {"evaluation": "error", "language_level": "beginner", "interests": [], "feedback_focus": "vocabulary"}
    except Exception as e:
        print(f"Error evaluating language response: {e}")
        return {"evaluation": "error", "language_level": "beginner", "interests": [], "feedback_focus": "vocabulary"}

def generate_explanation(context, question, correct_answer, student_answer=None, is_initial=True):
    if is_initial:
        prompt = f"You are an educational assistant for children. Your task is to explain a concept from a textbook before asking a question. Make the explanation engaging, interactive, and appropriate for a 7-10 year old.\n\nContext from textbook: {context}\n\nI'm about to ask this question: {question}\n\nProvide a very brief, engaging explanation (2-3 sentences max) that will help a child understand just the key concept needed to answer this question. Keep it simple, conversational, and interactive - like you're talking directly to the child. End your explanation with the question."
    else:
        prompt = f"You are an educational assistant for children. Your task is to provide a short, helpful hint when a student gives an incorrect answer. Make the explanation engaging, interactive, and appropriate for a 7-10 year old.\n\nContext from textbook: {context}\n\nQuestion: {question}\nCorrect answer: {correct_answer}\nStudent's answer: {student_answer}\n\nProvide a very brief hint (1-2 sentences) to guide the student toward the correct answer. Be encouraging and interactive. End your hint by asking the question again."
    
    try:
        return llm_response(prompt)
    except Exception as e:
        print(f"Error generating explanation: {e}")
        return "I'm having trouble explaining this concept. Let's try again later."

def generate_language_feedback(prompt, expected_responses, student_response=None, is_initial=True, student_profile=None):
    if is_initial:
        llm_prompt = f"You are an English language tutor for children. Present a conversational prompt in a way that's friendly and matches the child's current language level.\n\nPresent this prompt to the student: {prompt}\n\nStudent profile (if available): {student_profile if student_profile else 'New student'}"
    else:
        llm_prompt = f"""You are an English language tutor for children. Provide personalized feedback that:
1. Adapts to their language level (simpler explanations for beginners)
2. Incorporates their interests when possible 
3. Focuses on the specific area they need help with (vocabulary, grammar, etc.)
4. Uses encouragement and positive reinforcement
5. Models correct language naturally rather than just correcting
Be warm, engaging, and make learning fun!

Prompt given: {prompt}
Expected responses: {expected_responses}
Student's response: {student_response}

Student profile: {student_profile if student_profile else 'New student'}

Provide personalized, adaptive feedback that helps them improve while maintaining their confidence."""
    
    try:
        return llm_response(llm_prompt)
    except Exception as e:
        print(f"Error generating language feedback: {e}")
        return "I'm having trouble providing feedback. Let's try again."

def tts(text):
    stream = sd.OutputStream(
        samplerate=voice.config.sample_rate,
        channels=1,
        dtype='int16',
        blocksize=512,
        latency='low'
    )   
    stream.start()
    for audio_bytes in voice.synthesize_stream_raw(text):
        int_data = np.frombuffer(audio_bytes, dtype=np.int16)
        block_size = stream.blocksize
        if block_size is not None:
            remainder = len(int_data) % block_size
            if remainder != 0:
                padding = block_size - remainder
                int_data = np.pad(int_data, (0, padding), mode='constant')
        stream.write(int_data)
    stream.stop()
    stream.close()

def recording():
    p = pyaudio.PyAudio() 

    print("Recording")

    stream = p.open(
        format=sample_format,
        channels=channels,
        rate=fs,
        frames_per_buffer=chunk,
        input=True,
    )

    frames = [] 

    silence_threshold = 5.0

    print(f"Using fixed silence threshold: {silence_threshold}")

    silence_duration_limit = 2 
    max_silence_frames = int(silence_duration_limit * fs / chunk)
    silence_frames = 0
    
    max_recording_duration = 10  
    max_recording_frames = int(max_recording_duration * fs / chunk)
    total_frames = 0

    print("Please start speaking...")

    while True:
        data = stream.read(chunk)
        frames.append(data)
        total_frames += 1

        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)
        audio_energy = np.sqrt(np.mean(audio_data**2))

        if audio_energy < silence_threshold:
            silence_frames += 1
        else:
            silence_frames = 0 

        if silence_frames > max_silence_frames:
            print("Silence detected, stopping recording")
            break
            
        if total_frames > max_recording_frames:
            print("Maximum recording duration reached")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Finished recording")

    audio_data = b"".join(frames)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    audio_array = np.reshape(audio_array, (-1, channels))
    audio_array = audio_array.mean(axis=1) 
    audio_array = audio_array.astype(np.float32) / 32768.0 

    audio_tensor = torch.from_numpy(audio_array)

    resampler = torchaudio.transforms.Resample(orig_freq=fs, new_freq=16000)
    audio_tensor_resampled = resampler(audio_tensor)

    audio_array_resampled = audio_tensor_resampled.numpy()

    return audio_array_resampled

def educational_mode(json_data):
    print("Starting educational chatbot...")
    print("Say 'stop chat please' to exit")
    
    educational_data = json_data
    if not educational_data:
        print("No educational content found. Exiting.")
        return
    
    current_lesson = educational_data
    context = current_lesson["context"]
    dialogs = current_lesson["dialogs"]
    
    print(f"Loaded lesson: {current_lesson['title']}")
    
    welcome_message = "Hi there! I'm your learning buddy. Today we're going to learn about physics. Lets start the lesson?"
    print(f"Assistant: {welcome_message}")
    tts(welcome_message)
    
    current_dialog_index = 0
    max_attempts = 2
    
    while current_dialog_index < len(dialogs):
        try:
            current_dialog = dialogs[current_dialog_index]
            question = current_dialog["question"]
            correct_answer = current_dialog["answer"]
            
            explanation = generate_explanation(context, question, correct_answer)
            print(f"Assistant: {explanation}")
            tts(explanation)
            
            attempts = 0
            answered_correctly = False
            
            while attempts < max_attempts and not answered_correctly:
                print("\nWaiting for your answer...")
                audio_array = recording()
                student_answer = model.transcribe(audio_array, fp16=False)["text"].strip()
                
                temp = student_answer.lower().strip('.').split()
                if 'stop' in temp and 'chat' in temp and 'please' in temp:
                    print("Stop word detected, ending conversation")
                    goodbye_message = "Thanks for learning with me today! Goodbye!"
                    tts(goodbye_message)
                    return
                
                if student_answer == '':
                    print("Nothing detected, please try again")
                    tts("I didn't hear your answer. Could you please try again?")
                    continue
                
                print(f"Student: {student_answer}")
                
                evaluation = evaluate_answer(student_answer, correct_answer, question)
                
                if evaluation == "correct":
                    answered_correctly = True
                    response = f"Great job! That's correct. {correct_answer}"
                    print(f"Assistant: {response}")
                    tts(response)
                elif evaluation == "partially_correct" and attempts >= max_attempts - 1:
                    answered_correctly = True
                    response = f"That's partly right! The complete answer is: {correct_answer}"
                    print(f"Assistant: {response}")
                    tts(response)
                else:
                    feedback = generate_explanation(context, question, correct_answer, student_answer, is_initial=False)
                    print(f"Assistant: {feedback}")
                    tts(feedback)
                    attempts += 1
            
            current_dialog_index += 1
            
            if current_dialog_index >= len(dialogs):
                completion_message = "Congratulations! You've completed all the questions for this lesson. You did a great job learning about physics!"
                print(f"Assistant: {completion_message}")
                tts(completion_message)
            else:
                transition = "Let's move to the next question!"
                print(f"Assistant: {transition}")
                tts(transition)
                time.sleep(1)
            
        except Exception as e:
            print(f"Error occurred: {e}")
            error_message = "I'm having some trouble. Let's try again."
            print(f"Assistant: {error_message}")
            tts(error_message)
            time.sleep(1)
            continue

def language_learning_mode(parent_prompt):
    print("Starting English language learning chatbot...")
    print("Say 'stop chat please' to exit")
    
    language_data = load_language_learning_content(parent_prompt)
    if not language_data:
        print("No language learning content found. Using sample data.")
    
    current_lesson = language_data[0]
    conversations = current_lesson["conversations"]
    
    print(f"Loaded lesson: {current_lesson['title']} (Level: {current_lesson['level']})")
    
    welcome_message = "Hello! I'm your English practice buddy. We'll have fun conversations together to help you learn. Let's start!"
    print(f"Assistant: {welcome_message}")
    tts(welcome_message)
    
    student_profile = {
        "language_level": current_lesson["level"].lower(),
        "interests": [],
        "feedback_focus": "vocabulary",
        "previous_responses": []
    }
    
    current_conversation_index = 0
    max_attempts = 3
    
    while current_conversation_index < len(conversations):
        try:
            current_conversation = conversations[current_conversation_index]
            prompt = current_conversation["prompt"]
            expected_responses = current_conversation["expected_responses"]
            follow_up = current_conversation["follow_up"]
            
            initial_prompt = generate_language_feedback(prompt, expected_responses, student_profile=student_profile)
            print(f"Assistant: {initial_prompt}")
            tts(initial_prompt)
            
            attempts = 0
            answered_correctly = False
            
            while attempts < max_attempts and not answered_correctly:
                print("\nWaiting for your response...")
                audio_array = recording()
                student_response = model.transcribe(audio_array, fp16=False)["text"].strip()
                
                temp = student_response.lower().strip('.').split()
                if 'stop' in temp and 'chat' in temp and 'please' in temp:
                    print("Stop word detected, ending conversation")
                    goodbye_message = "Thanks for practicing English with me today! Goodbye!"
                    tts(goodbye_message)
                    return
                
                if student_response == '':
                    print("Nothing detected, please try again")
                    tts("I didn't hear you. Could you please try again?")
                    continue
                
                print(f"Student: {student_response}")
                
                student_profile["previous_responses"].append(student_response)
                
                evaluation_result = evaluate_language_response(student_response, expected_responses, student_profile["previous_responses"])
                
                if isinstance(evaluation_result, dict):
                    student_profile["language_level"] = evaluation_result.get("language_level", student_profile["language_level"])
                    if evaluation_result.get("interests"):
                        for interest in evaluation_result["interests"]:
                            if interest not in student_profile["interests"]:
                                student_profile["interests"].append(interest)
                    student_profile["feedback_focus"] = evaluation_result.get("feedback_focus", student_profile["feedback_focus"])
                    evaluation = evaluation_result.get("evaluation", "incorrect")
                else:
                    evaluation = evaluation_result
                
                if evaluation == "correct":
                    answered_correctly = True
                    adaptive_followup = generate_language_feedback(follow_up, expected_responses, 
                                                               student_response, is_initial=False, 
                                                               student_profile=student_profile)
                    print(f"Assistant: {adaptive_followup}")
                    tts(adaptive_followup)
                elif evaluation == "partially_correct" or attempts >= max_attempts - 1:
                    answered_correctly = True
                    adaptive_followup = generate_language_feedback(follow_up, expected_responses, 
                                                              student_response, is_initial=False, 
                                                              student_profile=student_profile)
                    print(f"Assistant: {adaptive_followup}")
                    tts(adaptive_followup)
                else:
                    feedback = generate_language_feedback(prompt, expected_responses, 
                                                     student_response, is_initial=False, 
                                                     student_profile=student_profile)
                    print(f"Assistant: {feedback}")
                    tts(feedback)
                    attempts += 1
            
            current_conversation_index += 1
            
            if current_conversation_index >= len(conversations):
                completion_message = f"Great job today! I noticed you're interested in {', '.join(student_profile['interests'][:2]) if student_profile['interests'] else 'learning English'}. Your {student_profile['feedback_focus']} is getting better! Would you like to practice again soon?"
                print(f"Assistant: {completion_message}")
                tts(completion_message)
            else:
                transition = "Let's try something new now!"
                print(f"Assistant: {transition}")
                tts(transition)
                time.sleep(1)
            
        except Exception as e:
            print(f"Error occurred: {e}")
            error_message = "I'm having some trouble. Let's try again."
            print(f"Assistant: {error_message}")
            tts(error_message)
            time.sleep(1)
            continue

def main():
    try:
        response = requests.get("https://chatbot-backend-iskc.onrender.com/api/get-json-dialogs")
        dialogs_data = response.json()
        print("Successfully fetched JSON data from endpoint")
    except Exception as e:
        print(f"Error fetching JSON data: {e}")
        dialogs_data = {}
    
    print("Welcome to the Learning Assistant!")
    print(f"Mode is {dialogs_data['dialogs'][0]['prompt']['mode']}")
    if dialogs_data['dialogs'][0]['prompt']['mode'] == 'lecture':
        educational_mode(dialogs_data['dialogs'][0]['pdf_book']['dialogs']['sections'][0])
    elif dialogs_data['dialogs'][0]['prompt']['mode'] == 'chat':
        language_learning_mode(dialogs_data['dialogs'][0]['prompt']['text'])
    else:
        print("Invalid mode. Please try again.")

if __name__ == "__main__":
    main() 
