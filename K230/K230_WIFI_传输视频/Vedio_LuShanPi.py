import socket
import cv2
import numpy as np
import struct
import time


def receive_video(host, port=8000):
    print(f"正在连接到 {host}:{port}...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(10)  # 10秒连接超时

    try:
        client.connect((host, port))
        print("连接成功")

        # 创建窗口
        cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Stream", 800, 480)  # 设置窗口大小与源大小一致

        # 用于计算FPS
        frame_count = 0
        start_time = time.time()
        fps = 0

        while True:
            try:
                # 接收图像大小
                size_data = client.recv(4)
                if not size_data or len(size_data) < 4:
                    print("连接断开")
                    break

                size = struct.unpack('>I', size_data)[0]
                print(f"接收图像: {size} 字节")

                # 接收图像数据
                data = bytearray()
                while len(data) < size:
                    packet = client.recv(min(4096, size - len(data)))
                    if not packet:
                        raise ConnectionError("连接断开")
                    data.extend(packet)

                # 解码并显示图像
                frame = cv2.imdecode(
                    np.frombuffer(data, np.uint8),
                    cv2.IMREAD_COLOR
                )

                if frame is not None:
                    # 计算显示FPS
                    frame_count += 1
                    current_time = time.time()
                    if current_time - start_time >= 1.0:
                        fps = frame_count / (current_time - start_time)
                        frame_count = 0
                        start_time = current_time

                    # 在图像上显示FPS
                    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    cv2.imshow("Video Stream", frame)
                else:
                    print("图像解码失败")

                # 按ESC键退出
                if cv2.waitKey(1) == 27:
                    print("用户退出")
                    break

            except Exception as e:
                print(f"接收错误: {e}")
                break

    except Exception as e:
        print(f"连接错误: {e}")
    finally:
        client.close()
        cv2.destroyAllWindows()
        print("客户端已关闭")


if __name__ == "__main__":
    # 替换为开发板的IP地址
    BOARD_IP = "192.168.134.225"  # 请替换为开发板实际IP地址
    receive_video(BOARD_IP)