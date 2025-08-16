from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

class Groq:
    def __init__(self):
        load_dotenv()
        
        self.llm = ChatGroq(model="gemma2-9b-it")

    def get_llm(self):
        return self.llm


