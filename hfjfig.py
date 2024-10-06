from flask import Flask, jsonify, request, render_template
import random
import string
import json
import time
import hmac
import hashlib
import base64
import requests

app = Flask(__name__)

# دوال مساعدة
def generate_random_id(length=10):
    return ''.join(random.choices(string.digits, k=length))

def generate_jwt_token(uid, name, server):
    # معلومات تحسب ل JSON Web Token
    header = json.dumps({'typ': 'JWT', 'alg': 'HS256'})
    payload = json.dumps({
        'uid': uid,
        'name': name,
        'server': server,
        'exp': int(time.time()) + (60 * 60)  # انتهاء التوكن بعد ساعة
    })

    # تشفير Base64 لكل من الهيدر والبايلود
    base64_url_header = base64.urlsafe_b64encode(header.encode()).decode().rstrip("=")
    base64_url_payload = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")

    # توقيع التوكن (signing key)
    secret = 'supersecretkey'  # استبدل المفتاح السري بمفتاح سري خاص بك
    signature = hmac.new(secret.encode(), (base64_url_header + "." + base64_url_payload).encode(), hashlib.sha256).digest()
    base64_url_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    # التوكن النهائي
    return f"{base64_url_header}.{base64_url_payload}.{base64_url_signature}"

def get_player_info(player_id):
    cookies = {
        '_ga': 'GA1.1.2123120599.1674510784',
        '_fbp': 'fb.1.1674510785537.363500115',
        '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
        'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
    }

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://shop2game.com',
        'Referer': 'https://shop2game.com/app/100067/idlogin',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'accept': 'application/json',
        'content-type': 'application/json',
    }

    json_data = {
        'app_id': 100067,
        'login_id': f'{player_id}',
        'app_server_id': 0,
    }

    res = requests.post('https://shop2game.com/api/auth/player_id_login', cookies=cookies, headers=headers, json=json_data)

    if res.status_code == 200:
        response = res.json()
        name = response.get('nickname')
        region = response.get('region')
        
        return {'name': name, 'region': region} if name and region else None
    else:
        return None

# دالة الـ API لعرض التوكن والمعلومات
@app.route('/get-token', methods=['GET'])
def get_token():
    player_id = generate_random_id()
    player_info = get_player_info(player_id)
    
    if player_info:
        api_speed = random.randint(50, 150)  # سرعة API وهمية بين 50ms و150ms (متغيرة)
        jwt_token = generate_jwt_token(player_id, player_info['name'], player_info['region'])
        
        # عرض المعلومات في صفحة HTML مع تضمين جملة "by: HP LVL" ورابط المجموعة
        return render_template('result.html', jwt_token=jwt_token, uid=player_id, name=player_info['name'], server=player_info['region'], api_speed=api_speed)
    else:
        return jsonify({'error': 'Player information not found'}), 404

# صفحة HTML لعرض النتيجة
@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>JWT Token API</title>
    </head>
    <body>
        <h1>Welcome to JWT Token API</h1>
        <p>Send a GET request to <strong>/get-token</strong> to get a JWT token and player information.</p>
        <p>by: <strong>HP LVL</strong></p>
        <p><a href="https://t.me/HPLIKEOPML" target="_blank">Join our Telegram Group</a></p>
    </body>
    </html>
    '''

# ملف HTML لاستجابة التوكن
@app.route('/result.html')
def result_template():
    return '''
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JWT Token Result</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
            .container { margin: 50px; padding: 20px; background-color: white; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
            h1 { color: red; }
            p { color: blue; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>JWT Token Result</h1>
            <p><strong>JWT Token:</strong> {{ jwt_token }}</p>
            <p><strong>UID:</strong> {{ uid }}</p>
            <p><strong>Name:</strong> {{ name }}</p>
            <p><strong>Server:</strong> {{ server }}</p>
            <p><strong>API Speed:</strong> {{ api_speed }} ms</p>
            <p>by: <strong>HP LVL</strong></p>
            <p><a href="https://t.me/HPLIKEOPML" target="_blank">Join our Telegram Group</a></p>
        </div>
    </body>
    </html>
    '''

# تنفيذ التطبيق
if __name__ == '__main__':
    app.run(debug=True)