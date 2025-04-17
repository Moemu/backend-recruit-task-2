import logging
import os
import time

import colorlog


def _init_logger(console_handler_level: int = logging.INFO) -> logging.Logger:
    """
    初始化一个 logger 以供全局使用

    :param console_handler_level: 控制台日志等级
    (日志文件日志等级为 Debug)
    """
    # 创建logger对象
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_handler_level)

    # 创建文件日志处理器
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = logging.FileHandler(
        f'logs/{time.strftime("%Y-%m-%d", time.localtime())}.log', encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(funcName)s: %(message)s")
    )

    # 定义颜色输出格式
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s] %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    # 将颜色输出格式添加到控制台日志处理器
    console_handler.setFormatter(color_formatter)

    # 移除默认的handler
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.propagate = False

    # 添加处理器对象
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


logger = _init_logger()
