import asyncio

from command import parse_command_string
from config import server_config
from logger import logger

HOST = server_config.host
PORT = server_config.port
BACKLOG = server_config.backlog
BUFSIZE = 1024


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    client_address = ":".join(str(x) for x in addr)
    logger.info(f"[{client_address}] 已建立连接")
    try:
        while True:
            data = await reader.read(BUFSIZE)
            if not data:
                break

            message = data.decode().strip()
            logger.info(f"[{client_address}] 收到消息：{message}")

            result = await parse_command_string(message)
            logger.info(f"[{client_address}] 发送消息：{result}")
            writer.write(result.encode())
            await writer.drain()
    except Exception as e:
        logger.error(f"[{client_address}] 连接出错：{e}")
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info(f"[{client_address}] 已断开连接")


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    logger.info(f"服务器已启动：{HOST}:{PORT}")
    logger.info("等待客户端连接...")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
