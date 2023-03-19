import requests
from config import *


def text_answer_request(text):
    ### openAI API url
    url = 'https://api.openai.com/v1/chat/completions'


    ### headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_key}',
    }

    ### requested data
    data = {
        "model": f"{model}",
        "messages": [{"role": "user", "content": f"{add_request_text}"
                                                 f"{text}"}],
        "temperature": temperature
    }

    ### get response
    response = requests.post(url, headers=headers, json=data)
    data = response.json()


    return data['choices'][0]['message']['content']

