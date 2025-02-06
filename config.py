# config.py
import os
import configparser

def get_api_key():
    """
    Retrieve the API key from an environment variable or a config.ini file.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        config = configparser.ConfigParser()
        config.read("config.ini")
        if "openai" in config and "api_key" in config["openai"]:
            api_key = config["openai"]["api_key"]
    return api_key
