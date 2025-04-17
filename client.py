import socket
import time

from config import client_config, server_config
from logger import logger

HOST = server_config.host
PORT = server_config.port
RECONNECT_ATTEMPTS = client_config.reconnect_attempts
HEARTBEAT_INTERVAL = client_config.heartbeat_interval

ADDRESS = f"{HOST}:{PORT}"
BUFSIZE = 1024
LOG_FILE = "./logs/client_commands.txt"


def send_command(sock: socket.socket, cmd: str) -> str:
    """
    发送命令

    :param sock: Socket 对象
    :param cmd: 要执行的指令
    :return: 执行结果
    """
    sock.send(cmd.encode())
    return sock.recv(BUFSIZE).decode()


def connect_socket() -> socket.socket:
    """
    获取 Socket 对象
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(HEARTBEAT_INTERVAL)
    s.connect((HOST, PORT))
    logger.info(f"成功连接服务器 {ADDRESS}")
    return s


def log_command(command: str):
    """
    写命令到文件中
    """
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{command}\n")


def run_client():
    """
    客户端主函数
    """
    attempt = 0
    while attempt < RECONNECT_ATTEMPTS or RECONNECT_ATTEMPTS == 0:
        try:
            s = connect_socket()
            attempt = 0

            while True:
                cmd = input(f"{ADDRESS}> ").strip()

                if cmd.lower() in ["exit", "quit"]:
                    s.close()
                    return

                if cmd:
                    result = send_command(s, cmd)
                    print(result)
                    log_command(cmd)

        except (socket.error, socket.timeout) as e:
            logger.error(f"连接错误: {e}")

        except KeyboardInterrupt:
            return

        attempt += 1
        wait = min(10, 2**attempt)
        logger.info(f"等待 {wait} 秒后重试连接...")
        time.sleep(wait)

    logger.error("重连次数达到上限，退出程序")


if __name__ == "__main__":
    run_client()
