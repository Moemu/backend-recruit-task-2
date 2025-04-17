import asyncio
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Literal, Optional, Sequence, Union, overload

import aiosqlite
from aiosqlite import Row

from config import server_config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        self.DB_PATH = Path(server_config.db_path)

        asyncio.run(self.init_db())
        logger.info(f"数据库路径: {self.DB_PATH}")

    async def init_db(self) -> None:
        """
        初始化数据库，检查数据库是否存在，不存在则创建
        """
        if not os.path.isfile(self.DB_PATH) or self.DB_PATH.stat().st_size == 0:
            logger.info("数据库不存在，正在创建...")
            await self.__create_database()

    def __connect(self) -> aiosqlite.Connection:
        return aiosqlite.connect(self.DB_PATH)

    async def __create_database(self) -> None:
        """
        创建三个表，分别存放字符串类型，双向链表类型，哈希类型表
        """
        await self.execute(
            """CREATE TABLE STRING(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            KEY TEXT NOT NULL UNIQUE,
            VALUE TEXT NOT NULL);"""
        )
        await self.execute(
            """CREATE TABLE DLIST (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            KEY TEXT NOT NULL,
            VALUE TEXT NOT NULL,
            PREV_ID INTEGER,
            NEXT_ID INTEGER,
            FOREIGN KEY (PREV_ID) REFERENCES DLIST(ID),
            FOREIGN KEY (NEXT_ID) REFERENCES DLIST(ID));"""
        )
        await self.execute(
            """CREATE TABLE HASHMAP (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            KEY TEXT NOT NULL,
            FIELD TEXT NOT NULL,
            VALUE TEXT NOT NULL);"""
        )

    @overload
    async def execute(
        self,
        query: str,
        params: Sequence[Any] = (),
        fetchone: Literal[True] = True,
        fetchall: Literal[False] = False,
    ) -> Optional[Row]:
        """执行选择查询并返回单个结果"""
        ...

    @overload
    async def execute(
        self,
        query: str,
        params: Sequence[Any] = (),
        fetchone: Literal[False] = False,
        fetchall: Literal[True] = True,
    ) -> Optional[Iterable[Row]]:
        """执行选择查询并返回所有结果"""
        ...

    @overload
    async def execute(
        self,
        query: str,
        params: Sequence[Any] = (),
        fetchone: Literal[False] = False,
        fetchall: Literal[False] = False,
    ) -> str:
        """执行一般查询而不返回结果"""
        ...

    async def execute(
        self,
        query: str,
        params: Sequence[Any] = (),
        fetchone: Literal[True, False] = False,
        fetchall: Literal[True, False] = False,
    ) -> Union[str, Optional[Row], Optional[Iterable[Row]]]:
        """
        异步执行SQL查询

        :param query: 要执行的SQL查询语句
        :param params: 传递给查询的参数
        :param fetchone: 是否获取单个结果
        :param fetchall: 是否获取所有结果
        """
        async with self.__connect() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.cursor()

            try:
                await cursor.execute(query, params)
            except aiosqlite.IntegrityError:
                msg = "违反唯一性或外键约束！"
                logger.error(msg)
                return msg
            except (aiosqlite.OperationalError, sqlite3.OperationalError) as e:
                msg = f"操作错误: {e}"
                logger.error(msg, exc_info=True)
                return msg
            except Exception as e:
                msg = f"其他错误: {e}"
                logger.error(e, exc_info=True)
                return msg

            if fetchone:
                return await cursor.fetchone()
            if fetchall:
                return await cursor.fetchall()

            await conn.commit()

        return "1"  # Succeed.


database = Database()
