import os
# Add these lines at the very top of the file, before other imports
os.environ['GRPC_ENABLE_FORK_SUPPORT'] = '0'
os.environ['GRPC_POLL_STRATEGY'] = 'poll'

import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext, Label, Button
from PIL import Image, ImageTk
import threading
import random
import time
from apikey import api_data
import os
import json
from datetime import datetime

# Configure API
genai.configure(api_key=api_data)

# Set up safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]


# List models and select one that supports generateContent
#models = list_available_models()
model_name = "gemini-2.5-pro-exp-03-25"  # Default to gemini-pro as it's the most reliable model

# Set up the selected model
model = genai.GenerativeModel(
    model_name=model_name,
    generation_config={
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
)

# Initialize conversation history
conversation_history = []
memory_file = "conversation_memory.json"

# Load previous conversation if exists
if os.path.exists(memory_file):
    with open(memory_file, 'r') as f:
        conversation_history = json.load(f)

# Initialize Text-to-Speech Engine for macOS with better voice settings
# Initialize Text-to-Speech Engine with female voice
try:
    engine = pyttsx3.init('nsss')
    voices = engine.getProperty('voices')
    for voice in voices:
        if any(name in voice.name.lower() for name in ["samantha", "karen", "victoria"]):  # Female voices
            engine.setProperty('voice', voice.id)
            break
    
    # Configure voice properties for natural speech
    engine.setProperty('rate', 165)  # Slightly slower for more natural pace
    engine.setProperty('volume', 0.9)  # Slightly softer volume
    
except Exception as e:
    print(f"Speech engine initialization error: {e}")
    engine = pyttsx3.init()
engine.setProperty('pitch', 1.0)  # Natural pitch

def speak(text):
    """Convert text to speech with optimized timing"""
    try:
        # Optimize pauses for faster response while maintaining naturalness
        text = text.replace('...', ' ')  # Remove long pauses
        sentences = text.split('. ')
        
        for sentence in sentences:
            if sentence.strip():
                if ',' in sentence:
                    sub_parts = sentence.split(',')
                    for sub_part in sub_parts:
                        if sub_part.strip():
                            engine.say(sub_part.strip())
                            engine.runAndWait()
                            time.sleep(0.1)  # Shorter pause after comma
                else:
                    engine.say(sentence.strip())
                    engine.runAndWait()
            
            time.sleep(0.2)  # Shorter pause between sentences
            
    except Exception as e:
        print(f"Speech error: {e}")
        engine.say(text)
        engine.runAndWait()

# Add some personality traits
niaa_personality = [
    "I'm always happy to help!",
    "Let me think about that for a moment...",
    "That's an interesting question!",
    "I love learning new things!",
    "Did you know I'm powered by Gemini AI?",
]

# At the top of the file, add a speech manager class
# Remove all existing speak functions and engine initializations
# Keep only the SpeechManager class and its implementation

# Remove all previous speech-related code and replace with this single implementation
class SpeechManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechManager, cls).__new__(cls)
            cls._instance.speech_lock = threading.Lock()
            cls._instance.init_engine()
        return cls._instance

    def init_engine(self):
        try:
            self.engine = pyttsx3.init('nsss')  # Use macOS native speech
            voices = self.engine.getProperty('voices')
            
            # Priority list of natural-sounding female voices
            preferred_voices = [
                "com.apple.speech.synthesis.voice.samantha",  # US English
                "com.apple.speech.synthesis.voice.victoria",  # US English
                "com.apple.speech.synthesis.voice.karen",     # Australian English
                "com.apple.speech.synthesis.voice.moira",     # Irish English
                "com.apple.speech.synthesis.voice.tessa"      # South African English
            ]
            
            # Find the best available voice
            selected_voice = None
            for preferred in preferred_voices:
                for voice in voices:
                    if preferred in voice.id:
                        selected_voice = voice.id
                        break
                if selected_voice:
                    break
            
            if selected_voice:
                self.engine.setProperty('voice', selected_voice)
            
            # Optimize voice properties for natural speech
            self.engine.setProperty('rate', 175)     # Slightly faster for natural pace
            self.engine.setProperty('volume', 0.85)  # Comfortable volume level
            
        except Exception as e:
            print(f"Speech engine initialization error: {e}")
            self.engine = pyttsx3.init()

    def speak(self, text):
        """Thread-safe speaking function with natural pauses and intonation"""
        with self.speech_lock:
            try:
                if not text.strip():
                    return
                
                # Clean and prepare text with natural breaks
                text = text.replace('...', ' — ')  # Convert ellipsis to pause
                text = text.replace('!', '! ').replace('?', '? ')  # Add slight pauses after punctuation
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                
                for sentence in sentences:
                    if sentence:
                        # Add breathing space between sentences
                        self.engine.say(sentence)
                        self.engine.runAndWait()
                        time.sleep(0.3)  # Natural pause between sentences
                        
            except Exception as e:
                print(f"Speech error: {e}")
                self.init_engine()  # Reinitialize engine on error

# Example greetings with natural speech patterns
greetings = [
    "Hi Hemant! *small pause* How are you doing today?",
    "Hey there! *warm tone* What can I help you with?",
    "Hello! *enthusiastic* It's great to see you again!",
    "*gentle voice* Good to have you back, Hemant.",
    "*friendly tone* Hey! What's on your mind?"
]

# Create single speech manager instance
speech_manager = SpeechManager()

# Single global speak function
def speak(text):
    """Global speak function using speech manager"""
    speech_manager.speak(text)

# Remove all other speak functions and engine initializations
def speak(text):
    """Convert text to speech with thread-safe handling"""
    try:
        # Create a new engine instance for each speech request
        local_engine = pyttsx3.init('nsss')
        local_engine.setProperty('rate', 165)
        local_engine.setProperty('volume', 0.9)
        
        # Get available voices and set female voice
        voices = local_engine.getProperty('voices')
        for voice in voices:
            if any(name in voice.name.lower() for name in ["samantha", "karen", "victoria"]):
                local_engine.setProperty('voice', voice.id)
                break
        
        # Process text with natural pauses
        sentences = text.split('. ')
        for sentence in sentences:
            if sentence.strip():
                local_engine.say(sentence.strip())
                local_engine.runAndWait()
                time.sleep(0.2)  # Brief pause between sentences
                
    except Exception as e:
        print(f"Speech error: {e}")
        # Fallback to simple speech if error occurs
        try:
            fallback_engine = pyttsx3.init()
            fallback_engine.say(text)
            fallback_engine.runAndWait()
        except:
            print("Critical speech error")

# Move generate_response and IMAGES_PATH to the top, before the class definition
IMAGES_PATH = os.path.join(os.path.dirname(__file__))

# Update personality traits for more natural responses
niaa_personality = [
    "By the way, I really enjoy our conversations.",
    "You know, that's quite fascinating.",
    "Let me think about this for a moment.",
    "I find that really interesting.",
    "You always ask such thoughtful questions.",
    "That reminds me of something interesting.",
    "I'm learning so much from our chats.",
    "That's a fascinating point.",
    "I really appreciate you sharing that with me.",
    "That's actually a great observation."
]

def generate_response(prompt):
    """Generate response using Gemini API with conversation history"""
    try:
        # Enhanced prompt for more natural conversation without emojis
        enhanced_prompt = f"""
        You are Niaa, a friendly and empathetic AI assistant with a warm personality.
        Important rules:
        - Never use emojis or emoticons in responses
        - Keep responses professional yet warm
        - Use proper punctuation instead of symbols
        - Use casual, conversational language
        - Some funny and engaging responses
        - Give short, concise answers
        _ Reply like a friend
        - Sounds like Alexa,Grok,Siri
        
        Conversation guidelines:
        - Use casual, conversational language
        - Show empathy through words, not symbols and emojies
        - Use short, concise sentences
        - Use active voice
        - Use contractions
        - Include occasional verbal fillers like "hmm", "well", "you know"
        - React to user's emotions with appropriate words
        - Use short, natural sentences
        - Ask follow-up questions occasionally
        - Reference previous parts of the conversation naturally
        
        You're talking to Hemant, who you know well. Be friendly and professional.
        Current time: {datetime.now().strftime("%H:%M")}
        
        Previous context:
        {conversation_history[-5:] if conversation_history else "No previous context"}
        
        Respond naturally to: {prompt}
        """
        
        # Generate response using the correct method
        response = model.generate_content(enhanced_prompt, stream=False)
        response_text = response.text
        
        # Clean any potential emojis from response
        response_text = ''.join(char for char in response_text if not (0x1F300 <= ord(char) <= 0x1F9FF))
        
        # Add to conversation history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Save conversation to memory
        with open(memory_file, 'w') as f:
            json.dump(conversation_history, f)
            
        return response_text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm having trouble processing that right now. Could you try again?"

class NiaaAssistant:
    def __init__(self):
        self.current_state = "idle"
        self.conversation_active = False
        self.recognizer = sr.Recognizer()
        self.setup_gui()
        self.setup_threads()

    def setup_robot_image(self):
        """Setup the robot image display"""
        try:
            default_path = os.path.join(IMAGES_PATH, "robot-girl.png")
            if os.path.exists(default_path):
                self.default_img = Image.open(default_path).resize((150, 150), Image.Resampling.LANCZOS)
                self.robot_img = ImageTk.PhotoImage(self.default_img)
                self.image_label = Label(self.header_frame, image=self.robot_img, bg="#f0f0f0")
                self.image_label.pack()
            else:
                raise FileNotFoundError(f"Default image not found: {default_path}")
        except Exception as e:
            print(f"Error loading robot image: {e}")
            self.image_label = Label(self.header_frame, text="Niaa", bg="#f0f0f0", font=("Arial", 16))
            self.image_label.pack()

    def setup_threads(self):
        """Initialize and start the background threads"""
        self.wake_thread = threading.Thread(target=self.wake_up_loop, daemon=True)
        self.conversation_thread = threading.Thread(target=self.conversation_loop, daemon=True)
        
        # Start the threads
        self.wake_thread.start()
        self.conversation_thread.start()

    def setup_gui(self):
        """Initialize the GUI components"""
        self.root = tk.Tk()
        self.root.title("Niaa - AI Assistant")
        self.root.geometry("500x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.configure(bg="#f0f0f0")
        
        # Create frames
        self.header_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.header_frame.pack(pady=10)
        
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.footer_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.footer_frame.pack(pady=10)
        
        # Setup robot image
        self.setup_robot_image()
        
        # Setup conversation area
        self.conversation_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=("Arial", 12),
            bg="white",
            padx=10,
            pady=10
        )
        self.conversation_area.pack(fill=tk.BOTH, expand=True)
        
        # Setup status and button
        self.status_label = Label(
            self.footer_frame,
            text="Ready",
            fg="green",
            bg="#f0f0f0",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.activate_btn = Button(
            self.footer_frame,
            text="Activate Niaa",
            command=self.manual_activate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        )
        self.activate_btn.pack(side=tk.RIGHT)

    def conversation_loop(self):
        while True:
            try:
                if self.current_state == "listening":
                    with sr.Microphone() as source:
                        # Reduce ambient noise adjustment duration
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                        self.update_status("Listening...", "blue")
                        print("Listening for command...")
                        
                        try:
                            # Increased timeout and phrase_time_limit
                            audio = self.recognizer.listen(
                                source,
                                timeout=10,  # Increased from 5 to 10 seconds
                                phrase_time_limit=15  # Increased from 10 to 15 seconds
                            )
                            
                            query = self.recognizer.recognize_google(audio, language='en-in').lower()
                            if query and query.strip():
                                print(f"Heard: {query}")
                                self.root.after(0, lambda q=query: self.process_query(q))
                            
                        except sr.WaitTimeoutError:
                            # Handle timeout more gracefully
                            print("Listening timeout - resetting...")
                            self.update_status("Ready", "green")
                            continue
                        except sr.UnknownValueError:
                            # Speech wasn't understood
                            print("Didn't catch that...")
                            continue
                        except sr.RequestError as e:
                            print(f"Could not request results: {e}")
                            self.update_status("Network error, retrying...", "red")
                            time.sleep(1)
                            
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                self.update_status("Error occurred, recovering...", "red")
                time.sleep(1)

    def process_query(self, query):
        """Process query in the main thread"""
        self.update_conversation_area(f"You: {query}\n", "user")
        self.handle_query(query)

    def wake_up_loop(self):
        while True:
            try:
                if self.current_state == "idle":
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        self.update_status("Waiting for wake word...", "blue")
                        audio = self.recognizer.listen(source, timeout=None)
                        command = self.recognizer.recognize_google(audio, language='en-in').lower()
                        
                        if any(wake_word in command for wake_word in ["hello nia", "hello niya", "hello niaa", "hey niaa", "wake up", "hell niaa","hello Niaa","hello neha"]):
                            self.root.after(0, self.activate_assistant)
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                time.sleep(1)
            time.sleep(0.1)

    # Remove listen_to_command method as it's no longer needed

    def handle_query(self, query):
        if any(cmd in query.lower() for cmd in ["stop niaa", "goodbye", "exit", "quit"]):
            self.deactivate_assistant()
            return True
            
        self.animate_robot("think")
        self.update_status("Thinking...", "orange")
        
        # Generate response in a separate thread for faster UI response
        def generate_and_speak():
            response = generate_response(query)
            if random.random() > 0.8:  # Reduce frequency of personality traits
                response += " " + random.choice(niaa_personality)
            
            # Use root.after to ensure thread safety
            def update_ui():
                self.update_conversation_area(f"Niaa: {response}\n", "assistant")
                self.update_status("Ready", "green")
                self.animate_robot("talk")
                speak(response)  # Single speak call
            
            self.root.after(0, update_ui)
            
        threading.Thread(target=generate_and_speak, daemon=True).start()
        return False

    def activate_assistant(self):
        self.current_state = "listening"
        self.conversation_active = True
        greetings = [
            "Hey Hemant! Great to see you! What's on your mind?",
            "Hi there! How can I help you today?",
            "Oh, hey Hemant! I was just thinking about our last chat. What's up?",
            "Hello! I'm all ears - what would you like to talk about?",
            "Hey! Perfect timing - I was just getting ready to help. What do you need?"
        ]
        response = random.choice(greetings)
        self.update_conversation_area(f"Niaa: {response}\n", "assistant")
        self.animate_robot("wake")
        speak(response)

    def deactivate_assistant(self):
        farewells = [
            "Take care, Hemant! It was great chatting with you!",
            "Time to go already? Well, I'll be here when you need me!",
            "Thanks for the chat! Don't be a stranger!",
            "Catch you later! Come back soon!",
            "Bye for now! Looking forward to our next conversation!"
        ]
        response = random.choice(farewells)
        self.update_conversation_area(f"Niaa: {response}\n", "assistant")
        speak(response)
        self.animate_robot("wave")
        self.current_state = "idle"
        self.conversation_active = False

    def manual_activate(self):
        if self.current_state == "idle":
            self.activate_assistant()

    def on_close(self):
        self.current_state = "closing"
        speak("Goodbye Hemant! I'll be here when you need me.")
        try:
            with open(memory_file, 'w') as f:
                json.dump(conversation_history, f)
        except Exception as e:
            print(f"Error saving conversation history: {e}")
        self.root.destroy()

    def update_status(self, text, color):
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))

    def update_conversation_area(self, text, sender):
        def update():
            tag = sender + str(len(self.conversation_area.get("1.0", tk.END)))
            self.conversation_area.insert(tk.END, text, tag)
            self.conversation_area.tag_config(tag, 
                foreground="blue" if sender == "user" else "green")
            self.conversation_area.see(tk.END)
        self.root.after(0, update)

    def animate_robot(self, action):
        def do_animate():
            try:
                image_mapping = {
                    "talk": "robot-talk.png",
                    "think": "robot-think.png",
                    "wave": "robot-wave.png",
                    "wake": "robot-wake.png"
                }
                
                if action in image_mapping:
                    img_path = os.path.join(IMAGES_PATH, image_mapping[action])
                    if os.path.exists(img_path):
                        img = Image.open(img_path).resize((150, 150), Image.Resampling.LANCZOS)
                        self.robot_img = ImageTk.PhotoImage(img)
                        self.image_label.config(image=self.robot_img)
                        if action == "talk":
                            self.root.after(1000, self.reset_robot_image)
            except Exception as e:
                print(f"Animation error: {e}")
                self.reset_robot_image()
        self.root.after(0, do_animate)

    def reset_robot_image(self):
        def do_reset():
            try:
                default_path = os.path.join(IMAGES_PATH, "robot-girl.png")
                if os.path.exists(default_path):
                    img = Image.open(default_path).resize((150, 150), Image.Resampling.LANCZOS)
                    self.robot_img = ImageTk.PhotoImage(img)
                    self.image_label.config(image=self.robot_img)
            except Exception as e:
                print(f"Error resetting image: {e}")
                self.image_label.config(text="Niaa")
        self.root.after(0, do_reset)

    def run(self):
        if not conversation_history:
            self.update_conversation_area(
                "Niaa: Hello Hemant! I'm Niaa, your AI assistant. Say 'Hello Niaa' or click the button to start.\n",
                "assistant"
            )
        self.root.mainloop()

# Create and run the assistant
if __name__ == "__main__":
    assistant = NiaaAssistant()
    assistant.run()