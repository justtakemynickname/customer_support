from transformers import pipeline

# Initialize the NLP model
nlp_model = pipeline("text-generation", model="gpt2")

def handle_text_query(text):
    response = nlp_model(text, max_length=50, num_return_sequences=1)
    return response[0]['generated_text']
