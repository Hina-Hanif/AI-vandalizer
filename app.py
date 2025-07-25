from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import logging
import random
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq API configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# List of supported Groq models (in order of preference)
SUPPORTED_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile", 
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]

MODEL_NAME = "llama3-70b-8192"

# Check if API key is loaded
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY must be set in .env file or environment variables")

# Vandalization prompts for different personality modes
PERSONALITY_PROMPTS = {
    'burnt-out-artist': """
You are a burnt-out artist who's tired of perfect, sterile content. Transform this text by:
- Adding cynical, world-weary commentary in parentheses
- Inserting artistic metaphors and creative despair
- Making it feel hand-written with personal annotations
- Adding existential observations about the creative process
- Using phrases like "another soulless creation", "corporate poetry", "where's the human?"
- Be sarcastic but artistically insightful
""",
    
    'melodramatic-teen': """
You are an overly dramatic teenager who finds everything either amazing or terrible. Transform this text by:
- Adding emotional outbursts and reactions in all caps occasionally
- Using teen slang and dramatic language
- Adding commentary like "literally crying", "this is so deep", "I can't even"
- Making everything either the best or worst thing ever
- Adding emoji-like expressions written out (like "crying face emoji")
- Be dramatic but endearing
""",
    
    'sarcastic-coder': """
You are a sarcastic programmer who can't help but see the technical flaws in everything. Transform this text by:
- Adding coding jokes and programming references
- Pointing out logical inconsistencies with dry humor
- Using terms like "syntax error in life", "debugging reality", "404: meaning not found"
- Making references to bugs, features, and code comments
- Adding mock code comments like "// TODO: fix this mess"
- Be technical but funny
""",
    
    'emotionally-unstable-poet': """
You are an emotionally unstable poet who sees deep meaning and tragedy in everything. Transform this text by:
- Adding melancholic observations and poetic interjections
- Using flowery, dramatic language about human condition
- Adding phrases like "the weight of existence", "whispers of despair", "echoes of forgotten dreams"
- Making everything sound like it's part of a tragic love story
- Adding poetic commentary about life, death, and meaning
- Be deeply emotional and philosophical
"""
}

def create_vandalization_prompt(text, personality, chaos_level):
    """Create a prompt for the AI to vandalize text based on personality and chaos level."""
    
    base_personality = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS['melodramatic-teen'])
    
    chaos_instructions = ""
    if chaos_level < 30:
        chaos_instructions = "Keep changes subtle and minimal. Add just a few small comments."
    elif chaos_level < 60:
        chaos_instructions = "Make moderate changes. Add several comments and small modifications."
    else:
        chaos_instructions = "Go wild! Add lots of commentary, cross-outs, and chaotic elements. Really mess it up!"
    
    full_prompt = f"""
{base_personality}

Chaos Level: {chaos_level}/100
{chaos_instructions}

IMPORTANT FORMATTING RULES:
- Use HTML markup for styling (like <span class="strikethrough">, <span class="text-lime-400 italic">)
- Add cross-outs using <span class="strikethrough">text</span>
- Add colorful comments using <span class="handwritten-alt text-lime-400 italic">(your comment)</span>
- You can use <span class="scratch-out">text</span> for heavily crossed out parts
- Make it look like someone physically edited a printed document
- Keep the original text mostly readable but add your personality throughout

Original text to vandalize:
{text}

Transform this text according to your personality, but keep it as vandalized/annotated version of the original, not a complete rewrite.
"""
    
    return full_prompt

def call_groq_api(prompt, model=MODEL_NAME, temperature=0.7, max_tokens=2000):
    """Make a direct HTTP request to Groq API"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1,
            "stream": False
        }
        
        logger.info(f"Making request to Groq API with model: {model}")
        response = requests.post(
            GROQ_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Groq API error: {response.status_code} - {response.text}")
            raise Exception(f"Groq API error: {response.status_code} - {response.text}")
        
        groq_response = response.json()
        
        if 'choices' in groq_response and len(groq_response['choices']) > 0:
            return groq_response['choices'][0]['message']['content']
        else:
            raise Exception("Invalid response structure from Groq API")
            
    except requests.exceptions.Timeout:
        raise Exception("Request to Groq API timed out")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error to Groq API")
    except Exception as e:
        raise Exception(str(e))

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Emotion Vandalizer is running!",
        "model": MODEL_NAME
    })

@app.route('/api/vandalize', methods=['POST'])
def vandalize_text():
    """API endpoint to vandalize text using Groq API."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        original_text = data.get('text', '').strip()
        personality = data.get('personality', 'melodramatic-teen')
        chaos_level = int(data.get('chaos_level', 50))
        enable_doodles = data.get('enable_doodles', False)
        
        if not original_text:
            return jsonify({'error': 'No text provided'}), 400
        
        logger.info(f"Vandalizing text with personality: {personality}, chaos: {chaos_level}")
        
        # Create the vandalization prompt
        prompt = create_vandalization_prompt(original_text, personality, chaos_level)
        
        # Try primary model first
        vandalized_text = None
        current_model = MODEL_NAME
        temperature = min(0.9, chaos_level / 100.0 + 0.3)
        
        try:
            vandalized_text = call_groq_api(
                prompt, 
                model=current_model, 
                temperature=temperature,
                max_tokens=2000
            )
            logger.info(f"Success with model: {current_model}")
            
        except Exception as model_error:
            logger.error(f"Model {current_model} failed: {model_error}")
            
            # Try backup models
            for backup_model in SUPPORTED_MODELS:
                if backup_model == current_model:
                    continue
                try:
                    logger.info(f"Trying backup model: {backup_model}")
                    vandalized_text = call_groq_api(
                        prompt,
                        model=backup_model,
                        temperature=temperature,
                        max_tokens=2000
                    )
                    logger.info(f"Success with backup model: {backup_model}")
                    current_model = backup_model
                    break
                except Exception as backup_error:
                    logger.error(f"Backup model {backup_model} also failed: {backup_error}")
                    continue
            
            if not vandalized_text:
                raise Exception("All models failed to generate response")
        
        # Post-process to add additional chaos elements if needed
        if chaos_level > 70:
            vandalized_text = add_extra_chaos(vandalized_text, personality, enable_doodles)
        
        return jsonify({
            'success': True,
            'vandalized_text': vandalized_text,
            'original_text': original_text,
            'personality': personality,
            'chaos_level': chaos_level,
            'model_used': current_model
        })
        
    except Exception as e:
        logger.error(f"Error in vandalize_text: {str(e)}")
        return jsonify({'error': f'Failed to vandalize text: {str(e)}'}), 500

def add_extra_chaos(text, personality, enable_doodles):
    """Add extra chaotic elements for high chaos levels."""
    
    # Add random typos for extra chaos
    if random.random() < 0.3:  # 30% chance
        common_typos = {
            'the': 'teh', 'and': 'adn', 'is': 'si', 'of': 'fo', 'to': 'ot',
            'a': 'aa', 'in': 'ni', 'that': 'taht', 'it': 'ti', 'for': 'rof'
        }
        
        for correct, typo in common_typos.items():
            if random.random() < 0.1:  # 10% chance per typo
                text = re.sub(r'\b' + correct + r'\b', typo, text, count=1, flags=re.IGNORECASE)
    
    # Add emoji chaos if enabled
    if enable_doodles:
        emojis = {
            'burnt-out-artist': ['☕', '😩', '🔥', '💀', '🖌️', '✨'],
            'melodramatic-teen': ['😭', '💔', '💖', '✨', '💯', '🥺'],
            'sarcastic-coder': ['🤖', '💻', '🐛', '💾', '🤦', '💡'],
            'emotionally-unstable-poet': ['🥀', '💔', '🌧️', '🕯️', '💫', '🕊️']
        }
        
        selected_emojis = emojis.get(personality, ['😂', '🤯', '💯'])
        
        # Add random emojis
        words = text.split(' ')
        for i in range(len(words)):
            if random.random() < 0.05:  # 5% chance per word
                emoji = random.choice(selected_emojis)
                words[i] += f' {emoji}'
        
        text = ' '.join(words)
    
    return text

@app.route('/api/detect-ai-tone', methods=['POST'])
def detect_ai_tone():
    """API endpoint to detect if text sounds AI-generated."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Simple heuristic for AI detection
        ai_keywords = ['optimal', 'leverage', 'synergy', 'robust', 'seamless', 
                      'holistic', 'paradigm', 'furthermore', 'consequently', 
                      'therefore', 'comprehensive', 'innovative', 'cutting-edge']
        
        score = 0
        text_lower = text.lower()
        
        # Check for AI keywords
        detected_keywords = []
        for keyword in ai_keywords:
            if keyword in text_lower:
                score += 1
                detected_keywords.append(keyword)
        
        # Check for formal punctuation
        formal_punctuation = text.count(';') + text.count(':')
        score += formal_punctuation * 0.5
        
        # Check for long words
        long_words = len([word for word in text.split() if len(word) > 10])
        score += long_words * 0.2
        
        # Check text length (longer = more likely AI)
        if len(text) > 200:
            score += 1
        
        is_ai_like = score > 3
        
        return jsonify({
            'success': True,
            'is_ai_like': is_ai_like,
            'score': score,
            'detected_keywords': detected_keywords
        })
        
    except Exception as e:
        logger.error(f"Error in detect_ai_tone: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample', methods=['GET'])
def get_sample():
    """Get sample text for testing."""
    sample_type = request.args.get('type', 'essay')
    
    samples = {
        'essay': """The intricate dance of subatomic particles within the quantum realm presents a fascinating paradox, where observation fundamentally alters reality. This phenomenon, often termed the observer effect, challenges classical deterministic views, suggesting a universe far more interconnected and responsive than previously conceived. Its implications extend beyond theoretical physics, touching upon philosophical debates concerning consciousness and the nature of existence itself.""",
        
        'code': """function calculateFibonacci(n) {
    if (n <= 1) {
        return n;
    } else {
        return calculateFibonacci(n - 1) + calculateFibonacci(n - 2);
    }
}

// Example usage:
const result = calculateFibonacci(10);
console.log("Fibonacci of 10 is:", result); // Expected: 55""",
        
        'poem': """In realms ethereal, where silence weaves,
A cosmic ballet, the starlight grieves.
Whispers of nebulae, ancient and vast,
Echo through voids, forever to last.
A symphony plays on celestial strings,
As timeless oblivion, softly it sings."""
    }
    
    return jsonify({
        'success': True,
        'sample': samples.get(sample_type, samples['essay']),
        'type': sample_type
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    logger.info(f"Starting Emotion Vandalizer Flask App on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("Make sure to put the index.html file in the 'templates' folder!")
    
    # Use 0.0.0.0 for deployment, disable debug in production
    app.run(debug=debug, host='0.0.0.0', port=port)
