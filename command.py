from typing import Any

from arclet.alconna import Alconna, Args, CommandMeta, command_manager

from database import HashMap, LinkedList, String
from logger import logger

string_set = Alconna(
    "set",
    Args["key", str],
    Args["value", str],
    meta=CommandMeta(description="存储 key-value 类型数据"),
)

string_get = Alconna(
    "get", Args["key", str], meta=CommandMeta(description="获取 key 对应的 value")
)

string_del = Alconna(
    "del", Args["key", str], meta=CommandMeta(description="删除 key 对应的 value")
)

linkedlist_lpush = Alconna(
    "lpush",
    Args["key", str],
    Args["value", str],
    meta=CommandMeta(description="可直接放一个数据在左端"),
)

linkedlist_rpush = Alconna(
    "rpush",
    Args["key", str],
    Args["value", str],
    meta=CommandMeta(description="可直接放一个数据在右端"),
)

linkedlist_range = Alconna(
    "range",
    Args["key", str],
    Args["start", int],
    Args["end", int],
    meta=CommandMeta(description="将key 对应 start 到 end 位置的数据全部返回"),
)

linkedlist_len = Alconna(
    "len", Args["key", str], meta=CommandMeta(description="获取 key 存储数据的个数")
)

linkedlist_lpop = Alconna(
    "lpop", Args["key", str], meta=CommandMeta(description="获取key最左端的数据并删除")
)

linkedlist_rpop = Alconna(
    "rpop", Args["key", str], meta=CommandMeta(description="获取key最右端的数据并删除")
)

linkedlist_ldel = Alconna(
    "ldel", Args["key", str], meta=CommandMeta(description="删除key 所有的数据")
)

help = Alconna(
    "help",
    Args["command", str, None],
    meta=CommandMeta(
        description="获取command指令的使用方式，不提供command则获取所有指令"
    ),
)

ping = Alconna("ping", meta=CommandMeta(description="心跳指令，ping响应pong"))

hash_hset = Alconna(
    "hset",
    Args["key", str],
    Args["field", str],
    Args["value", str],
    meta=CommandMeta(description="存储key对应的键值对数据"),
)

hash_hget = Alconna(
    "hget",
    Args["key", str],
    Args["field", str],
    meta=CommandMeta(description="获取key中field字段的value值"),
)

hash_hdel = Alconna(
    "hdel",
    Args["key", str],
    Args["field", str, None],
    meta=CommandMeta(description="删除key中field字段及其value值"),
)


async def handle_set(args):
    return await String.set(args["key"], args["value"])


async def handle_get(args):
    return await String.get(args["key"])


async def handle_delete(args):
    return await String.delete(args["key"])


async def handle_lpush(args):
    return await LinkedList.lpush(args["key"], args["value"])


async def handle_rpush(args):
    return await LinkedList.rpush(args["key"], args["value"])


async def handle_range(args):
    return await LinkedList.range(args["key"], args["start"], args["end"])


async def handle_len(args):
    return await LinkedList.len(args["key"])


async def handle_rpop(args):
    return await LinkedList.rpop(args["key"])


async def handle_lpop(args):
    return await LinkedList.lpop(args["key"])


async def handle_ldel(args):
    return await LinkedList.ldel(args["key"])


async def handle_hset(args):
    return await HashMap.hset(args["key"], args["field"], args["value"])


async def handle_hget(args):
    return await HashMap.hget(args["key"], args["field"])


async def handle_hdel(args):
    return await HashMap.hdel(args["key"], args["field"])


async def handle_ping(args) -> str:
    """
    心跳指令
    """
    return "pong"


async def handle_help_command(args) -> str:
    """
    显示帮助
    """
    command = args["command"]

    if command is None:
        return command_manager.all_command_help()
    if command not in command_handlers:
        return f"未知的指令: {command}"

    help_info = command_manager.command_help(command)
    return help_info or "帮助信息不存在!"


command_handlers: dict[str, tuple[Alconna, Any]] = {
    "set": (string_set, handle_set),
    "get": (string_get, handle_get),
    "del": (string_del, handle_delete),
    "lpush": (linkedlist_lpush, handle_lpush),
    "rpush": (linkedlist_rpush, handle_rpush),
    "range": (linkedlist_range, handle_range),
    "ldel": (linkedlist_ldel, handle_ldel),
    "len": (linkedlist_len, handle_len),
    "lpop": (linkedlist_lpop, handle_lpop),
    "rpop": (linkedlist_rpop, handle_rpop),
    "help": (help, handle_help_command),
    "ping": (ping, handle_ping),
    "hset": (hash_hset, handle_hset),
    "hget": (hash_hget, handle_hget),
    "hdel": (hash_hdel, handle_hdel),
}


async def parse_command_string(command_str: str) -> str:
    """
    解析指令字符串并返回执行结果
    """
    # 提取指令名和参数
    parts = command_str.split(maxsplit=1)
    if not parts:
        msg = "无效的指令!"
        logger.error(msg)
        return msg

    command_name = parts[0]
    # raw_command_arg = parts[1]

    # 使用 Alconna 解析器解析命令和参数
    command_handler = command_handlers.get(command_name)
    if command_handler is None:
        msg = f"未知的指令: {command_name}"
        logger.error(msg)
        return msg

    alconna_class = command_handler[0]
    handler = command_handler[1]

    args = alconna_class.parse(command_str)

    if len(parts) > 1 and parts[1] in ["-h", "--help"]:
        help_info = command_manager.command_help(command_name)
        return help_info or "帮助信息不存在!"

    if not args.matched:
        msg = "命令参数有误!"
        logger.warning(msg)
        return msg

    return await handler(args)
