import paramiko
import cv2
import requests
import json
import RPi.GPIO as GPIO
import dht11
import time
import datetime


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin=2)
standard = float(30)

#写真をとってサーバーにアップロードする
def photo():
    # 実行されると写真を撮影し、images/photo.jpgに保存
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    cv2.imwrite("photo.jpg", frame)

    cap.release()
    cv2.destroyAllWindows()

    # SFTP接続準備
    config = {
        "host": "your host",
        "port": 00,
        "username": "name",
        "password": "password"
    }

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(config['host'],
                port=config['port'],
                username=config['username'],
                password=config['password'])

    # SFTPセッション開始
    sftp_con = client.open_sftp()

    # PUTの場合
    sftp_con.put("photo.jpg", "public_html/photo.jpg")

    # クローズ
    client.close()
    
def temp_res():
        result = instance.read()
        temp = result.temperature
            
        if(temp != 0):
            if(temp < standard):
                print(temp)
                temp = None
            else:
                return temp
        time.sleep(3)
    
#gasに値を送信
def postData(data):
    photo()
    temp_res()
    if(data is None):
        print("params is empty")
        return False

    payload = {
        "data": data
    }
    url = "https://script.google.com/macros/s/AKfycbzydLibLCbN0_AbKmLIZafdyvHh3LX4DmfowAbeR4kGHh9xPabty2zcmYVGc2UiuPiIRQ/exec"
    
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if(response.status_code == 200 and response.text == "success"):
        print("post success!")
        return True
    print(response.text)
    return False

while True:
    t = temp_res()
    if t is not None:
        tem = float(t)
        if t > standard:
            postData(t)

#データをこの関数で送る
#postData(temp_res())
