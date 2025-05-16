import time, os, sys, socket, _thread
from media.sensor import *
from media.media import *
import network

# ---------- WiFi连接配置 ----------
SSID = "bing"         # 替换为你的WiFi名称
PASSWORD = "12345678" # 替换为你的WiFi密码

def connect_wifi():
    sta = network.WLAN(network.STA_IF)
    if not sta.active():
        sta.active(True)
    print("WiFi模块激活状态:", sta.active())

    print(f"正在连接 {SSID}...")
    sta.connect(SSID, PASSWORD)

    max_wait = 5
    while max_wait > 0:
        if sta.isconnected():
            break
        max_wait -= 1
        time.sleep(1)
        print("剩余等待次数：", max_wait)

    while sta.ifconfig()[0] == '0.0.0.0':
        pass

    if sta.isconnected():
        ip_info = sta.ifconfig()
        print(f"\n连接成功，IP地址: {ip_info[0]}")
        return ip_info[0]
    else:
        print("WiFi连接失败！")
        return None

# ---------- 摄像头初始化 ----------
def init_camera():
    sensor = Sensor(id=2)
    sensor.reset()
    sensor.set_framesize(Sensor.QVGA, chn=CAM_CHN_ID_0)  # 320x240
    sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)
    sensor.run()
    return sensor

# ---------- MJPEG服务器 ----------
def handle_client(conn, sensor):
    try:
        conn.send(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n"
        )
        while True:
            img = sensor.snapshot(chn=CAM_CHN_ID_0)
            jpeg = img.compress(quality=30)
            conn.send(b"--frame\r\n")
            conn.send(b"Content-Type: image/jpeg\r\n\r\n")
            conn.send(jpeg)
            conn.send(b"\r\n")
            time.sleep(0.1)
    except Exception as e:
        print("客户端断开：", e)
    finally:
        conn.close()

def start_server(sensor, ip):
    port = 8080
    print(f"启动 MJPEG 服务：请在浏览器中打开 http://{ip}:{port}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print("客户端已连接：", addr)
        _thread.start_new_thread(handle_client, (conn, sensor))

# ---------- 主流程 ----------
def main():
    ip = connect_wifi()
    if not ip:
        return
    sensor = init_camera()
    print("gooo")
    start_server(sensor, ip)

main()
