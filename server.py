import os
import openai
import logging
import requests
import hashlib

from flask import Flask, request, jsonify

from PIL import Image
from io import BytesIO

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

def chatgpt_generate_image(prompt, engine):
    result = None

    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}",
            },
            json={
                "model": engine,
                "prompt": prompt,
                "num_images": 1,
                "size": "512x512",
            },
            proxies=proxies
        )

        response_json = response.json()
        result = response_json["data"][0]["url"]

        print(f'prompt : {prompt}, response : {response_json}')
    except Exception as e:
        print(f'exception : {e}')

    return result

def download(url):
    md5 = hashlib.md5()
    md5.update(url.encode('utf-8'))
    
    save_path = os.path.abspath(f'./cache/{md5.hexdigest()}.png')

    try:
        raw_response = requests.get(url, proxies=proxies)
        image = Image.open(BytesIO(raw_response.content))

        if not os.path.exists('./cache'):
            os.mkdir('./cache')
        
        print(f'save to : {save_path}')
        image.save(save_path)
    except Exception as e:
        print(f'exception : {e}')
        save_path = None

    return save_path

@app.route('/question')
def talk_to_chatgpt():    
    max_tokens = int(request.args.get('max_tokens', default=50))
    prompt = request.args.get('prompt')
    engine = request.args.get('engine', 'text-davinci-001')
    if not prompt:
        return '请指定你的问题'

    return jsonify({
        'result_text': chatgpt_request(prompt=prompt, max_tokens=max_tokens, engine=engine)
    })

@app.route('/image')
def generate_image_use_chatgpt():
    prompt = request.args.get('prompt')
    engine = request.args.get('engine', 'image-alpha-001')

    if not prompt or not any(prompt):
        return jsonify({
            'status': 'prompt为空'
        })

    url = chatgpt_generate_image(prompt=prompt, engine=engine)
    if not url or not any(url):
        return jsonify({
            'status': '生成失败'
        })

    save_path = download(url)
    if not save_path or not any(save_path):
        return jsonify({
            'status': '保存失败'
        })

    return jsonify({
        'status': '',
        'path': save_path
    })

if __name__ == '__main__':
    configure_openai()
    app.run()
