import yaml as yaml_
from pydantic import BaseModel

CONFIG_PATH = "./config.yaml"


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    """本地回环地址(IP地址)"""
    port: int = 6000
    """服务器服务端口"""
    backlog: int = 5
    """服务器最大连接数量"""

    db_path: str = "./database.db"
    """数据库文件路径"""


class ClientConfig(BaseModel):
    reconnect_attempts: int = 3
    """最大重连次数"""
    heartbeat_interval: int = 10
    """心跳包发送间隔"""


with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    yaml_config = yaml_.safe_load(f)

server_config = ServerConfig(**yaml_config.get("server", {}))
client_config = ClientConfig(**yaml_config.get("client", {}))
