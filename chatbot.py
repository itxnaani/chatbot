# -*- coding: utf-8 -*-
"""Chatbot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vB2qzrbXsWnO_Z2gQjGZnaW6-Dg1UVx1
"""

!pip install numpy pandas nltk transformers torch

from google.colab import files
uploaded = files.upload()

import pandas as pd
import re

# Load the movie lines
lines_file = "movie_lines.txt"
# Specify the encoding as 'latin-1'
lines = pd.read_csv(lines_file, sep=" \+\+\+\$\+\+\+ ", header=None, engine="python", names=["lineID", "characterID", "movieID", "character", "text"], encoding='latin-1')
# If 'latin-1' doesn't work, try 'cp1252'
# lines = pd.read_csv(lines_file, sep=" \+\+\+\$\+\+\+ ", header=None, engine="python", names=["lineID", "characterID", "movieID", "character", "text"], encoding='cp1252')

# Load the movie conversations
dialogue_file = "movie_conversations.txt"
conversations = pd.read_csv(dialogue_file, sep=" \+\+\+\$\+\+\+ ", header=None, engine="python", names=["characterID1", "characterID2", "movieID", "utteranceIDs"], encoding='latin-1') # Also apply encoding to this line
# If 'latin-1' doesn't work, try 'cp1252'
# conversations = pd.read_csv(dialogue_file, sep=" \+\+\+\$\+\+\+ ", header=None, engine="python", names=["characterID1", "characterID2", "movieID", "utteranceIDs"], encoding='cp1252') # Also apply encoding to this line

# Convert the utteranceIDs to a list of IDs (as they are stored as strings)
conversations["utteranceIDs"] = conversations["utteranceIDs"].apply(lambda x: re.findall(r'L[0-9]+', x))

# Display first few rows of each file to verify loading
print("Movie Lines Data:")
print(lines.head())

print("\nMovie Conversations Data:")
print(conversations.head())

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import re

# Download NLTK data (only required once)
nltk.download('punkt')

# Load your dataset
dialogue_file = "/content/movie_conversations.txt"
lines_file = "/content/movie_lines.txt"

# Specify the encoding as 'latin-1' when reading the files
conversations = pd.read_csv(dialogue_file, sep=" \+\+\+\$\+\+\+ ", header=None, engine='python', encoding='latin-1')
lines = pd.read_csv(lines_file, sep=" \+\+\+\$\+\+\+ ", header=None, engine='python', encoding='latin-1')  # Apply encoding here

# Display the first few rows to identify the correct dialogue column
print(lines.head())

# Assuming the dialogue text is in column 4 (adjust if necessary)
def preprocess(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower(), flags=re.ASCII)
    return text

# Handle missing values and apply preprocessing
lines[4] = lines[4].fillna('').apply(preprocess)

# Preview the preprocessed data
print(lines[4].head())

import pandas as pd

# Assuming the data was loaded as described earlier
# Verify the structure of the data
print(conversations.head())
print(lines.head())

# Ensure 'lines' DataFrame contains the dialogue column at the expected index
dialogue_column_index = 4  # Adjust if necessary, based on your dataset's structure

# Create a dictionary to map line IDs to dialogue text for faster lookup
lines_dict = {}
for _, row in lines.iterrows():
    line_id = row[0]  # Assuming line ID is in the first column
    dialogue = row[dialogue_column_index]  # Adjust based on the column with dialogue text
    lines_dict[line_id] = dialogue

# Convert conversations from string to list format
try:
    conversations[3] = conversations[3].apply(eval)
except Exception as e:
    print(f"Error in eval conversion: {e}")

# Create pairs of input-response dialogues
pairs = []
for conv in conversations[3]:  # Assuming conversation IDs are in the fourth column
    for i in range(len(conv) - 1):
        input_line = lines_dict.get(conv[i])
        response_line = lines_dict.get(conv[i + 1])
        if input_line and response_line:  # Only add pairs if both lines exist
            pairs.append((input_line, response_line))

# Convert to DataFrame
conversation_df = pd.DataFrame(pairs, columns=['Input', 'Response'])

# Display the resulting DataFrame
print(conversation_df.head())

# Step 1: Import necessary libraries
from transformers import pipeline

# Step 2: Load the zero-shot classification pipeline
# (This may download a model for the first time, so ensure you have an internet connection)
nlu_pipeline = pipeline('zero-shot-classification')

# Step 3: Define possible intents
intents = ["greeting", "goodbye", "thanks", "no answer"]

# Step 4: Create a function to classify intent
def classify_intent(input_text):
    result = nlu_pipeline(input_text, candidate_labels=intents)
    return result['labels'][0]  # Get the top label (intent)

# Example usage:
input_text = "Hello, how are you?"
intent = classify_intent(input_text)
print(f"Detected intent: {intent}")

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load the GPT-2 model and tokenizer
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name, cache_dir='/content/cache')
model = GPT2LMHeadModel.from_pretrained(model_name, cache_dir='/content/cache')

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_response(input_text):
    try:
        # Truncate long inputs
        max_input_length = 512
        tokens = tokenizer.encode(input_text, return_tensors='pt').to(device)
        if tokens.shape[-1] > max_input_length:
            tokens = tokens[:, -max_input_length:]

        # Generate response
        outputs = model.generate(tokens, max_length=100, num_return_sequences=1)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print("Error during response generation:", e)
        return "I'm sorry, I couldn't process your request."

# Test the function
print(generate_response("Hello, how are you?"))

!pip install Flask

import torch
from transformers import BertTokenizer, BertForSequenceClassification, GPT2LMHeadModel, GPT2Tokenizer
from sklearn.preprocessing import LabelEncoder

# Step 1: Intent Classification (Using DistilBERT for simplicity)

# Load the DistilBERT model and tokenizer
intent_model_name = 'distilbert-base-uncased'
intent_tokenizer = BertTokenizer.from_pretrained(intent_model_name)
intent_model = BertForSequenceClassification.from_pretrained(intent_model_name, num_labels=3)  # Modify for your intent categories

# Intent labels
intent_labels = ["greeting", "weather", "goodbye"]
label_encoder = LabelEncoder()
label_encoder.fit(intent_labels)

# Intent Classification Function
def classify_intent(user_input):
    inputs = intent_tokenizer(user_input, return_tensors="pt", padding=True, truncation=True, max_length=64)
    with torch.no_grad():
        outputs = intent_model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
    intent = label_encoder.inverse_transform([predicted_class_id])[0]
    return intent

# Step 2: Response Generation (Using GPT-2)

# Load GPT-2 model and tokenizer
response_model_name = 'gpt2'
response_tokenizer = GPT2Tokenizer.from_pretrained(response_model_name)
response_model = GPT2LMHeadModel.from_pretrained(response_model_name)

# Response Generation Function using GPT-2
def generate_response(user_input):
    # Tokenize and encode the user input
    inputs = response_tokenizer.encode(user_input, return_tensors='pt')

    # Generate a response from GPT-2
    outputs = response_model.generate(inputs, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2, top_k=50, top_p=0.95, temperature=1.5)

    # Decode and return the generated response
    response_text = response_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response_text

# Example Usage:
user_input = "Hello, how's the weather today?"
intent = classify_intent(user_input)
response = generate_response(user_input)

print(f"Intent: {intent}")
print(f"Response: {response}")

!pip install transformers torch scikit-learn

from transformers import BertTokenizer, BertForSequenceClassification
import torch
from sklearn.preprocessing import LabelEncoder

# Load pre-trained DistilBERT model and tokenizer for intent classification
intent_tokenizer = BertTokenizer.from_pretrained("distilbert-base-uncased")
intent_model = BertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

# Dummy labels (you can expand this based on your dataset)
intent_labels = ["greeting", "weather", "goodbye"]

# Label encoder for encoding the labels
label_encoder = LabelEncoder()
label_encoder.fit(intent_labels)

def classify_intent(user_input):
    # Tokenize input
    inputs = intent_tokenizer(user_input, return_tensors="pt", padding=True, truncation=True, max_length=64)

    # Get model predictions
    with torch.no_grad():
        outputs = intent_model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()

    # Convert prediction to label
    intent = label_encoder.inverse_transform([predicted_class_id])[0]
    return intent

from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load GPT-2 model and tokenizer
response_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
response_model = GPT2LMHeadModel.from_pretrained("gpt2")

def generate_response(user_input):
    # Tokenize user input
    inputs = response_tokenizer.encode(user_input, return_tensors="pt")

    # Generate a response
    outputs = response_model.generate(inputs, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2, top_k=50, top_p=0.95)

    # Decode the generated response
    response = response_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

!pip install flask pyngrok

!pip install waitress

!pip install pyngrok

from flask import Flask, request, jsonify
from pyngrok import ngrok, conf
from waitress import serve
from threading import Thread

# Initialize Flask app
app = Flask(__name__)

slack_token = 'xoxb-7999251384164-7996776045890-ELlhGxgYZBPm3CGIK7PBXolt'  # Replace with your actual bot token
slack_channel = 'ChatBot'  # Replace with the channel you want to post to

# Function to send a message to Slack
def send_slack_message(message):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {slack_token}',  # Your bot token
        'Content-Type': 'application/json'
    }
    data = {
        'channel': slack_channel,  # The channel you want to post in
        'text': message
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()  # You can return response to debug if needed

# Dummy function for intent classification
# Replace this with your actual logic for intent classification
def classify_intent(user_input):
    # Simple example, classify intent based on keywords
    if "hello" in user_input.lower():
        return "greeting"
    elif "bye" in user_input.lower():
        return "farewell"
    else:
        return "unknown"

# Dummy function for generating a response
# Replace this with actual logic to generate a meaningful response
def generate_response(intent, user_input):
    if intent == "greeting":
        return "Hello! How can I assist you today?"
    elif intent == "farewell":
        return "Goodbye! Have a great day!"
    else:
        return f"I'm sorry, I don't understand the intent of: {user_input}"

@app.route('/slack', methods=['POST'])
def slack_event():
    data = request.json
    user_input = data.get('text')

    # Slack verification challenge
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Handle messages
    if user_input:
        # Classify the intent based on the user input
        intent = classify_intent(user_input)

        # Generate a response based on the intent
        response = generate_response(intent, user_input)

        return jsonify({"text": response})

    # Handle case where 'text' is not provided
    return jsonify({"error": "No text provided"}), 400

# Function to run Flask in a separate thread
def run_flask():
    serve(app, host="0.0.0.0", port=5003)

# Start Flask in a background thread
thread = Thread(target=run_flask)
thread.start()

# Configure ngrok with your authtoken
# Get your authtoken from your ngrok dashboard: https://dashboard.ngrok.com/auth
conf.get_default().auth_token = "2oqinU2HtTaST4KStouNS3cMWY8_ka1S3RDESo8VWQxnDjAF"  # Replace YOUR_AUTHTOKEN with your actual token

# Disconnect existing tunnels before starting a new one
for tunnel in ngrok.get_tunnels():
    print(f"Disconnecting existing tunnel: {tunnel.public_url}")
    ngrok.disconnect(tunnel.public_url)

# Start ngrok and print public URL
public_url = ngrok.connect(5003)
print("Public URL:", public_url)

!curl -X POST https://4007-34-23-152-29.ngrok-free.app/slack -H "Content-Type: application/json" -d '{"text": "Hello, how are you?"}'

!curl -X POST https://4007-34-23-152-29.ngrok-free.app/slack -H "Content-Type: application/json" -d '{"text": "Bye"}'