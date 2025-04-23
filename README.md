# backend-recruit-task-02

## 项目简介

这是一个基于Python实现的轻量级内存数据库服务器，支持多种数据结构和客户端-服务器交互。该项目模仿 Redis 的部分功能，提供了字符串、双向链表和哈希表三种基础数据结构的存储和操作能力。

## 功能特性

### 核心数据结构

- **字符串(String)**：支持基本的键值对存储
  - `set`：存储键值对
  - `get`：获取键对应的值
  - `del`：删除键值对

- **双向链表(LinkedList)**：高效的列表数据结构
  - `lpush`/`rpush`：在链表左端/右端添加元素
  - `lpop`/`rpop`：获取并删除链表左端/右端元素
  - `range`：获取指定范围内的所有元素
  - `len`：获取链表长度
  - `ldel`：删除整个链表

- **哈希表(HashMap)**：支持字段级别的数据操作
  - `hset`：设置哈希表字段的值
  - `hget`：获取哈希表字段的值
  - `hdel`：删除哈希表字段或整个哈希表

### 系统功能

- 客户端与服务器基于 TCP 协议(Socket)通信，支持多个客户端连接
- 命令行交互式操作
- 断线重连功能
- 完善的日志记录系统
- 基于SQLite的持久化存储
- 支持YAML配置

## 技术栈

- **语言**: Python 3.9+
- **网络通信**: asyncio (异步IO) + socket
- **命令解析**: Alconna
- **数据库**: SQLite + aiosqlite (异步SQLite操作)
- **配置管理**: Pydantic + YAML
- **日志系统**: logging + colorlog
- **代码风格检查**: Pre-commit: flake8, mypy, black, isort

## 快速开始

1. 确保安装了所有依赖包:
   ```
   pip install pydantic aiosqlite colorlog arclet-alconna
   ```

2. 配置服务 (可选):
   编辑 `config.yaml` 文件修改服务器地址、端口等配置

3. 启动服务器:
   ```
   python server.py
   ```

4. 启动客户端:
   ```
   python client.py
   ```

5. 在客户端中使用命令进行操作，如:
   ```
   set mykey hello
   get mykey
   lpush mylist item1
   rpush mylist item2
   hset user name alice
   ```

## 目录结构

- `server.py`: 服务端主程序
- `client.py`: 客户端主程序
- `command.py`: 命令解析与处理模块
- `config.py`: 配置加载与管理
- `logger.py`: 日志系统
- `database/`: 数据库相关模块
  - `_sqlite.py`: SQLite数据库管理
  - `_types.py`: 数据类型实现
- `.pre-commit-config.yaml` Pre-commit 配置

## 遗憾

· 使用的语言和数据库不太贴合审核要求

· 审核要求使用指令历史数据持久化，我实现了数据库持久化

· 尽管使用了 Pre-Commit 工具规范了代码格式且找出隐藏类型错误，但还是无法深入测试程序稳健性

· 模拟而并非实现了要求的数据格式

由于我的时间有限，本来想用 Java/C++ & Redis 规范实现此项目，最终只能使用我所熟悉的 Python 草草实现。如果还有做的不好的地方，还请师兄指正。