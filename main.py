"""
SPACY BASICS - MINIMAL EXAMPLE
================================

The absolute simplest spaCy script to get started.
Copy and modify this to learn.

Run: python spacy_minimal.py
"""

import spacy

# Step 1: Load spaCy model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_trf")
print("Done!\n")

# Step 2: Load your text file
print("Loading text file...")
with open("sample_book.txt", "r", encoding="utf-8") as f:
    text = f.read()
print(f"✅ Loaded {len(text)} characters\n")

# Step 3: Process text with spaCy
print("Processing text with spaCy...")
doc = nlp(text)
print("Done!\n")

# Step 4: Extract people's names
print("=" * 70)
print("PEOPLE FOUND IN TEXT:")
print("=" * 70)

people = []
for entity in doc.ents:
    if entity.label_ == "PERSON":
        people.append(entity.text)
        print(f"  • {entity.text}")

print(f"\nTotal: {len(people)} mentions of people")

# Step 5: Count unique people
from collections import Counter
people_freq = Counter(people)

print(f"\n" + "=" * 70)
print("MOST MENTIONED CHARACTERS:")
print("=" * 70)

for name, count in people_freq.most_common():
    print(f"  {name}: {count} times")

# Step 6: Show all other entity types found
print(f"\n" + "=" * 70)
print("OTHER THINGS FOUND IN TEXT:")
print("=" * 70)

other_entities = {}
for entity in doc.ents:
    if entity.label_ != "PERSON":
        if entity.label_ not in other_entities:
            other_entities[entity.label_] = []
        other_entities[entity.label_].append(entity.text)

for entity_type, values in sorted(other_entities.items()):
    unique_values = list(set(values))
    print(f"\n{entity_type}:")
    for value in unique_values[:5]:  # Show first 5
        print(f"  • {value}")
    if len(unique_values) > 5:
        print(f"  ... and {len(unique_values) - 5} more")

print(f"\n" + "=" * 70)