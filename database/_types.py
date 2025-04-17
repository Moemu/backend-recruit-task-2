from typing import List, Optional, overload

from ._sqlite import database


class String:
    """
    字符串数据表操作方法
    """

    @staticmethod
    async def set(key: str, value: str) -> str:
        """
        存储 key-value 类型数据
        """
        return await database.execute(
            """INSERT INTO STRING (KEY, VALUE) VALUES (?, ?)""",
            params=(key, value),
            fetchone=False,
            fetchall=False,
        )

    @staticmethod
    async def get(key: str) -> str:
        """
        获取 key 对应的 value
        """
        row = await database.execute(
            """SELECT * FROM STRING WHERE KEY = ?""",
            params=(key,),
            fetchone=True,
            fetchall=False,
        )
        return row[2] if row else f"指定的键 {key} 不存在!"

    @staticmethod
    async def delete(key: str) -> str:
        """
        删除 key 对应的 value
        """
        return await database.execute(
            """DELETE FROM STRING WHERE KEY = ?""",
            params=(key,),
            fetchone=False,
            fetchall=False,
        )


class LinkedList:
    """
    双向链表数据表操作方法
    """

    @staticmethod
    async def rpush(key: str, value: str) -> str:
        """
        放一个数据在左端
        """
        # 获得左(上一个)元素的 id
        last_item = await database.execute(
            """SELECT ID FROM DLIST WHERE KEY = ? AND NEXT_ID IS NULL LIMIT 1""",
            params=(key,),
            fetchone=True,
        )
        last_id = last_item[0] if last_item else None
        # 插入右(新)元素
        await database.execute(
            """INSERT INTO DLIST (KEY, VALUE, PREV_ID) VALUES (?, ?, ?);""",
            params=(key, value, last_id),
        )
        # 获取右(新)元素的 id
        new_item = await database.execute(
            """SELECT ID FROM DLIST WHERE KEY = ? ORDER BY ID DESC LIMIT 1""",
            params=(key,),
            fetchone=True,
        )
        new_id = new_item[0]  # type:ignore
        # 更新左(上一个)一个元素的 next_id
        if last_id is not None:
            await database.execute(
                """UPDATE DLIST SET NEXT_ID = ? WHERE ID = ?""",
                params=(new_id, last_id),
            )
        return "1"

    @staticmethod
    async def lpush(key: str, value: str) -> str:
        """
        放一个数据在右端
        """
        # 获得右(第一个插入)元素的 id
        prev_item = await database.execute(
            """SELECT ID FROM DLIST WHERE KEY = ? AND PREV_ID IS NULL LIMIT 1""",
            params=(key,),
            fetchone=True,
        )
        prev_id = prev_item[0] if prev_item else None
        # 插入新元素
        await database.execute(
            """INSERT INTO DLIST (KEY, VALUE, NEXT_ID) VALUES (?, ?, ?);""",
            params=(key, value, prev_id),
        )
        # 获取新元素的 id
        new_item = await database.execute(
            """SELECT ID FROM DLIST WHERE KEY = ? ORDER BY ID DESC LIMIT 1""",
            params=(key,),
            fetchone=True,
        )
        new_id = new_item[0]  # type:ignore
        # 更新(第一个插入)元素的 next_id
        if prev_id is not None:
            await database.execute(
                """UPDATE DLIST SET PREV_ID = ? WHERE ID = ?""",
                params=(new_id, prev_id),
            )
        return "1"

    @staticmethod
    async def range(key: str, start: int, end: int) -> str:
        """
        将 key 对应 start 到 end 位置的数据全部返回
        """
        if end < start:
            msg = "end 小于 start！"
            return msg

        # 获取链表第一个元素
        first_item = await database.execute(
            """SELECT * FROM DLIST WHERE KEY = ? AND PREV_ID IS NULL""",
            params=(key,),
            fetchone=True,
        )

        if first_item is None:
            msg = f"双向链表 {key} 不存在数据!"
            return msg

        next_id = first_item[0]
        results: List[str] = []

        while next_id:
            query_result = await database.execute(
                """SELECT * FROM DLIST WHERE KEY = ? AND ID = ?""",
                params=(key, next_id),
                fetchone=True,
            )
            results.append(query_result[2])  # type:ignore
            next_id = query_result[4]  # type:ignore

        if end - start - 1 > len(results):
            msg = "超出链表最大长度!"
            return msg

        return " ".join(results[start : end + 1])

    @staticmethod
    async def len(key: str) -> str:
        """
        获取 key 存储数据的个数
        """
        first_item = await database.execute(
            """SELECT ID FROM DLIST WHERE KEY = ? AND PREV_ID is NULL""",
            params=(key,),
            fetchone=True,
        )

        if first_item is None:
            return "0"

        next_id = first_item[0]
        counter = 0

        while next_id:
            query_result = await database.execute(
                """SELECT * FROM DLIST WHERE KEY = ? AND ID = ?""",
                params=(key, next_id),
                fetchone=True,
            )
            next_id = query_result[4]  # type:ignore
            counter += 1

        return str(counter)

    @staticmethod
    async def lpop(key: str) -> str:
        """
        获取key最左端的数据并删除
        """
        first_item = await database.execute(
            """SELECT * FROM DLIST WHERE KEY = ? AND PREV_ID IS NULL""",
            params=(key,),
            fetchone=True,
        )

        if first_item is None:
            msg = f"双向链表 {key} 不存在数据!"
            return msg

        item_id = first_item[0]
        item_next_id = first_item[4]
        if item_next_id is not None:
            await database.execute(
                """UPDATE DLIST SET PREV_ID = NULL WHERE ID = ?""",
                params=(item_next_id,),
            )

        await database.execute("""DELETE FROM DLIST WHERE ID = ?""", params=(item_id,))

        return first_item[2]

    @staticmethod
    async def rpop(key: str) -> str:
        """
        获取key最右端的数据并删除
        """
        last_item = await database.execute(
            """SELECT * FROM DLIST WHERE KEY = ? AND NEXT_ID IS NULL""",
            params=(key,),
            fetchone=True,
        )

        if last_item is None:
            msg = f"双向链表 {key} 不存在数据!"
            return msg

        item_id = last_item[0]
        item_prev_id = last_item[3]
        if item_prev_id is not None:
            await database.execute(
                """UPDATE DLIST SET NEXT_ID = NULL WHERE ID = ?""",
                params=(item_prev_id,),
            )

        await database.execute("""DELETE FROM DLIST WHERE ID = ?""", params=(item_id,))

        return last_item[2]

    @staticmethod
    async def ldel(key: str) -> str:
        """
        删除key 所有的数据
        """
        return await database.execute(
            """DELETE FROM DLIST WHERE KEY = ?""",
            params=(key,),
            fetchall=False,
            fetchone=False,
        )


class HashMap:
    """
    哈希类型
    """

    @staticmethod
    async def hset(key: str, field: str, value: str) -> str:
        """
        存储key对应的键值对数据
        """
        return await database.execute(
            """INSERT INTO HASHMAP (KEY, FIELD, VALUE) VALUES (?, ?, ?);""",
            params=(key, field, value),
            fetchall=False,
            fetchone=False,
        )

    @staticmethod
    async def hget(key: str, field: str) -> str:
        """
        获取key中field字段的value值
        """
        item = await database.execute(
            """SELECT * FROM HASHMAP WHERE KEY = ? AND field = ?""",
            params=(key, field),
            fetchone=True,
        )

        if item is None:
            msg = f"哈希表 {key} 不存在或者不存在 {field}!"
            return msg

        return item[3]

    @overload
    @staticmethod
    async def hdel(key: str, field: str):
        """
        删除key中field字段及其value值
        """
        ...

    @overload
    @staticmethod
    async def hdel(key: str):
        """
        删除key中所有数据
        """
        ...

    @staticmethod
    async def hdel(key: str, field: Optional[str] = None) -> str:
        if field is not None:
            return await database.execute(
                """DELETE FROM HASHMAP WHERE KEY = ? AND FIELD = ?""",
                params=(key, field),
                fetchall=False,
                fetchone=False,
            )

        return await database.execute(
            """DELETE FROM HASHMAP WHERE KEY = ?""",
            params=(key,),
            fetchall=False,
            fetchone=False,
        )
