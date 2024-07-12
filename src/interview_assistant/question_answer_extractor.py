import json
import random
import uuid
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from src.interview_assistant.config import openai_key
from src.interview_assistant.pdf_text_extractor import process_pdf

load_dotenv(find_dotenv())

client = OpenAI(
    api_key=openai_key
)

def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0
    )
    return chat_completion.choices[0].message.content

def extract_ques_ans(file_path, query):
    pdf_content = process_pdf(file_path)
    delimiter = "####"
    delimiter1 = "****"
    system_message = f"""
    Assistant will be given a text content extracted from a pdf. \
    The text content will be delimited with {delimiter1} characters. \
    The user input query will be delimited with {delimiter} characters. \
    The query will be a question already written in the text content given \
    to the assistant. The assistant will be asked to provide an answer to \
    the question based on the context of the text content. Provide exact \
    answer to the question asked in the query. Do not add any extra \
    information. If the question asked in the query is not found in the given \
    text content, then answer with "This question is not available in the \
    provided pdf file, please try another question." \n\n
    """

    user_message_for_model = f"""User message, \
    remember that your response to the user \
    must be from the context of the given text. \
    context : {delimiter1}{pdf_content}{delimiter1}
    query : {delimiter}{query}{delimiter}
    """

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message_for_model},
    ]
    response = get_completion_from_messages(messages)
    return {"message": "File uploaded and processed successfully", "answer": response}
