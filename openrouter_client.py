import requests
import base64
import json
from pathlib import Path
from typing import Optional
import os

# Try Streamlit secrets first (for cloud), fallback to .env (for local development)
try:
    import streamlit as st
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3-flash-preview"


def encode_image_to_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Encode image bytes to base64 data URL."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{base64_image}"


def get_correction_schema() -> dict:
    """Return the JSON schema for structured exercise correction output."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "exercise_correction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "exercises": {
                        "type": "array",
                        "description": "List of exercises with their corrections",
                        "items": {
                            "type": "object",
                            "properties": {
                                "exercise_name": {
                                    "type": "string",
                                    "description": "Name or number of the exercise"
                                },
                                "given_data": {
                                    "type": "string",
                                    "description": "Data provided in the exercise"
                                },
                                "questions": {
                                    "type": "array",
                                    "description": "List of questions and their answers",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "question": {
                                                "type": "string",
                                                "description": "The original question text"
                                            },
                                            "answer": {
                                                "type": "string",
                                                "description": "The correct answer with explanation"
                                            }
                                        },
                                        "required": ["question", "answer"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["exercise_name", "given_data", "questions"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["exercises"],
                "additionalProperties": False
            }
        }
    }


def build_system_prompt(output_language: Optional[str] = None, user_preferences: Optional[str] = None) -> str:
    """Build the system prompt based on user settings."""
    base_prompt = """You are an expert teacher and exercise corrector. Your task is to:
1. Analyze the uploaded exercise image(s)
2. Extract all exercises, questions, and given data
3. Provide correct, detailed answers for each question

For each exercise, include:
- The exercise name or number
- Any given data or context
- Each question with its complete correct answer and explanation
"""
    
    if output_language:
        base_prompt += f"\n\nIMPORTANT: Respond in {output_language}."
    else:
        base_prompt += "\n\nIMPORTANT: Respond in the same language as the exercise content."
    
    if user_preferences:
        base_prompt += f"\n\nUser preferences: {user_preferences}"
    
    return base_prompt


def correct_exercises(
    images: list[tuple[bytes, str]],
    output_language: Optional[str] = None,
    user_preferences: Optional[str] = None
) -> dict:
    """
    Send exercise images to OpenRouter for correction.
    
    Args:
        images: List of tuples containing (image_bytes, mime_type)
        output_language: Optional language for the output
        user_preferences: Optional user preferences for correction style
    
    Returns:
        dict: Parsed JSON response with exercise corrections
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build content array with text and images
    content = [
        {
            "type": "text",
            "text": "Please analyze and correct the exercises in the following image(s)."
        }
    ]
    
    # Add all images to the content
    for image_bytes, mime_type in images:
        data_url = encode_image_to_base64(image_bytes, mime_type)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": data_url
            }
        })
    
    # Build messages
    messages = [
        {
            "role": "system",
            "content": build_system_prompt(output_language, user_preferences)
        },
        {
            "role": "user",
            "content": content
        }
    ]
    
    # Build payload with structured output
    payload = {
        "model": MODEL,
        "messages": messages,
        "response_format": get_correction_schema()
    }
    
    # Make request
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    
    # Parse the structured output
    content_str = data["choices"][0]["message"]["content"]
    return json.loads(content_str)


def format_correction_output(correction_data: dict) -> str:
    """Format the correction data into a readable string (language-agnostic)."""
    output = []
    
    for exercise in correction_data.get("exercises", []):
        # Exercise header
        output.append(f"## {exercise.get('exercise_name', '')}")
        output.append("")
        
        # Given data (if present and not empty)
        given_data = exercise.get('given_data', '').strip()
        if given_data and given_data.lower() not in ['none', 'n/a', '-', '']:
            output.append(f"*{given_data}*")
            output.append("")
        
        # Questions and answers
        for i, q in enumerate(exercise.get("questions", []), 1):
            output.append(f"**{i}. {q.get('question', '')}**")
            output.append("")
            output.append(f"{q.get('answer', '')}")
            output.append("")
            output.append("")
        
        output.append("---")
        output.append("")
    
    return "\n".join(output)
