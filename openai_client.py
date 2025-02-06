# openai_client.py
import openai
from config import get_api_key

class OpenAIClient:
    def __init__(self, model="text-davinci-003"):
        self.model = model
        self.api_key = get_api_key()
        self.connected = False

    def connect(self):
        """
        Set the API key in the openai package. This is our “connection.”
        """
        if self.api_key:
            openai.api_key = self.api_key
            self.connected = True
        else:
            raise Exception("API Key not found. Set the OPENAI_API_KEY environment variable or configure config.ini.")

    def set_model(self, model):
        """
        Change the model used for summarization.
        """
        self.model = model

    def summarize(self, text, max_tokens=150, temperature=0.5):
        """
        Send the provided text to the API to generate a summary.
        """
        prompt = f"Please provide a concise summary of the following Python code:\n\n{text}\n\nSummary:"
        try:
            response = openai.Completion.create(
                engine=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            summary = response.choices[0].text.strip()
            return summary
        except Exception as e:
            return f"Error: {e}"
