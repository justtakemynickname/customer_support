# Install necessary libraries
# pip install transformers torch

from transformers import pipeline

# NLP Model for handling customer requests
class TextModule:
    def __init__(self):
        self.chatbot = pipeline("text-generation", model="gpt2")

    def process_request(self, customer_request):
        response = self.chatbot(customer_request, max_length=50, num_return_sequences=1)
        return response[0]["generated_text"]

# Example usage
text_module = TextModule()
print(text_module.process_request("How can I reset my password?"))
