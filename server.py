import os
import openai
import logging

from flask import Flask, request


proxies = {
    "http": "http://127.0.0.1:33210",
    "https": "http://127.0.0.1:33210",
}

app = Flask(__name__)

def configure_openai():
    if 'OPENAI_API_KEY' in os.environ:
        openai.api_key = os.environ['OPENAI_API_KEY']

    if hasattr(openai, 'default_http_client'):
        openai.default_http_client = openai.http_client.new_default_http_client(proxy=proxies)
    else:
        openai.proxy = proxies

def chatgpt_request_with_stream(prompt, max_tokens, engine='davinci'):
    print(f'prompt : {prompt}, max_tokens : {max_tokens}')
    try:
        completions = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0,
            stream=True
        )
        print(f'completion: {completions}')

        response = ''

        while True:
            completion = next(completions, None) 
            if completion is None:
                break

            response += completion.choices[0].text.strip()
    except Exception as e:
        print(f'exception : {e}')
        response = '请求异常'

    return response

def chatgpt_request(prompt, max_tokens, engine='davinci'):
    print(f'prompt : {prompt}, max_tokens : {max_tokens}')
    try:
        completion = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0
        )
        print(f'completion: {completion}')

        response = completion.choices[0].text.strip()
    except Exception as e:
        print(f'exception : {e}')
        response = '请求异常'

    return response

@app.route('/question')
def talk_to_chatgpt():    
    max_tokens = int(request.args.get('max_tokens', default=50))
    prompt = request.args.get('prompt')
    engine = request.args.get('engine', 'text-davinci-001')
    if not prompt:
        return '请指定你的问题'

    return chatgpt_request(prompt=prompt, max_tokens=max_tokens, engine=engine)

if __name__ == '__main__':
    configure_openai()
    app.run()
