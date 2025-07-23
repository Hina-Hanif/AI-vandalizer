# Emotion Vandalizer - AI-Powered Text Chaos Generator

A Flask web application that uses Groq AI to vandalize "perfect" text with human-like chaos, personality, and emotional flair.

## Features

- 🤖 **AI-Powered Vandalization**: Uses Groq's LLaMA model to intelligently vandalize text
- 🎭 **Multiple Personalities**: Choose from burnt-out artist, melodramatic teen, sarcastic coder, or emotionally unstable poet
- 📊 **Chaos Level Control**: Adjust vandalization intensity from subtle to total meltdown
- 🎨 **Visual Effects**: Strikethroughs, scratch-outs, emoji annotations, and sticky notes
- 🔍 **AI Detection**: Automatically detects overly "perfect" AI-generated text
- 💾 **Export Options**: Download your chaos as text files

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Project Structure

Create the following folder structure:

```
emotion-vandalizer/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── README.md
```

### 3. Add the Files

1. Copy the `app.py` code into your main application file
2. Create a `templates` folder and add the `index.html` file inside it
3. Make sure your Groq API key is correctly set in the `app.py` file
4. Make a .env file and give this
<img width="499" height="68" alt="image" src="https://github.com/user-attachments/assets/5aaed92d-75f1-4a7b-9522-3b8333efa995" />

5. Put your API key after making it from https://console.groq.com 


### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Endpoints

### `GET /`
Serves the main application page

### `POST /api/vandalize`
Vandalizes text using AI
- **Body**: `{ "text": "...", "personality": "...", "chaos_level": 50, "enable_doodles": true }`
- **Response**: `{ "vandalized_text": "...", "original_text": "...", ... }`

### `POST /api/detect-ai-tone`
Detects if text appears AI-generated
- **Body**: `{ "text": "..." }`
- **Response**: `{ "is_ai_like": true, "score": 4.5, "detected_keywords": [...] }`

### `GET /api/sample?type=essay`
Returns sample text for testing
- **Query params**: `type` (essay, code, poem)
- **Response**: `{ "sample": "..." }`

## Personality Modes

- **burnt-out-artist**: Cynical, world-weary commentary with artistic metaphors
- **melodramatic-teen**: Overly dramatic reactions with teen slang and emotional outbursts
- **sarcastic-coder**: Technical jokes, programming references, and dry humor
- **emotionally-unstable-poet**: Melancholic observations and flowery dramatic language

## Chaos Levels

- **0-20**: Subtle changes, minimal comments
- **21-60**: Moderate vandalization with several annotations
- **61-100**: Total chaos with extensive modifications, typos, and effects

## Technologies Used

- **Backend**: Flask (Python)
- **AI**: Groq API with LLaMA-3.1-8B model (with fallback support)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Fonts**: Google Fonts (Patrick Hand, Architects Daughter, Inter)

## Customization

### Adding New Personalities

Edit the `PERSONALITY_PROMPTS` dictionary in `app.py`:

```python
PERSONALITY_PROMPTS['your-personality'] = """
Your custom personality prompt here...
"""
```

### Adjusting AI Model

The app automatically tries multiple models if one fails. You can modify the model priority in `app.py`:

```python
SUPPORTED_MODELS = [
    "llama-3.1-8b-instant",    # Fast, good quality
    "llama3-8b-8192",          # Alternative LLaMA
    "mixtral-8x7b-32768",      # Mixtral model
    "gemma-7b-it"              # Google Gemma
]
```

### Custom Styling

Modify the CSS in `templates/index.html` to change the appearance.

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed
2. **Groq API Error**: Verify your API key is correct and has credits
3. **Templates Not Found**: Ensure `index.html` is in the `templates/` folder
4. **CORS Issues**: The app runs on localhost, so this shouldn't be an issue

### Debug Mode

The app runs in debug mode by default. To disable:

```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Contributing

Feel free to add new personalities, improve the vandalization algorithms, or enhance the UI!

## License

This project is for educational and entertainment purposes. Please use responsibly!
