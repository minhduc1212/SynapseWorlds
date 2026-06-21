import os
import sys
import json
import dotenv
from google import genai
from pydantic import BaseModel, Field

# Ensure stdout uses UTF-8 to prevent encoding errors on Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
dotenv.load_dotenv()

# Initialize the Gemini GenAI client
client = genai.Client()

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_dir, "character_relationships.json")
book_path = os.path.join(current_dir, "sample_book.txt")


if not os.path.exists(book_path):
    print(json.dumps({"error": f"sample_book.txt not found at {book_path}"}))
    sys.exit(1)

# Read the novel content
with open(book_path, "r", encoding="utf-8") as f:
    text = f.read()

# Define the structured output schema using Pydantic
class Character(BaseModel):
    name: str = Field(description="The canonical name of the character")
    aliases: list[str] = Field(default_factory=list, description="Other names, nicknames, or titles this character is referred to in the text")
    description: str = Field(description="A brief description of their traits, role, and actions in the text")

class Relationship(BaseModel):
    source: str = Field(description="The name of the source character (must match one of the character names exactly)")
    target: str = Field(description="The name of the target character (must match one of the character names exactly)")
    relationship_type: str = Field(description="The type of relationship (e.g., friend, mentor, sibling, trainer/partner, parent, etc.)")
    description: str = Field(description="Brief explanation of the relationship and how it evolves in the story")

class CharacterRelationships(BaseModel):
    characters: list[Character]
    relationships: list[Relationship]

# Prepare prompt for extraction
prompt = f"""
Analyze the following text. Extract ALL major and minor characters (including humans, named animals/rocs, and mythical entities if relevant to the narrative), along with their mutual or one-way relationships as depicted in the story.

Text:
{text}
"""

try:
    # Generate content using Gemma model with structured JSON schema
    response = client.models.generate_content(
        model="gemma-4-31b-it",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CharacterRelationships,
        }
    )
    
    # Parse output to ensure valid JSON formatting and print
    data = json.loads(response.text)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
except Exception as e:
    error_msg = {"error": f"Failed to extract characters: {str(e)}"}
    print(json.dumps(error_msg, indent=2))