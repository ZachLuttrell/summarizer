# summarizer.py
import os

def get_python_files(directory):
    """
    Return full paths of all .py files in the specified directory.
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.py')]

def read_file_content(file_path):
    """
    Read and return the content of the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

class Summarizer:
    def __init__(self, openai_client):
        self.client = openai_client

    def summarize_file(self, file_path):
        """
        Read a file and return its summary using the OpenAIClient.
        """
        content = read_file_content(file_path)
        if content.startswith("Error"):
            return content
        summary = self.client.summarize(content)
        return summary
