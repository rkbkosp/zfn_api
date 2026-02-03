# 正方教务系统 MCP Server

这是一个适配正方教务系统的 Model Context Protocol (MCP) 服务器。它允许 AI Agent（如 Claude Desktop）访问你的成绩、课表和个人信息。

## 安装设置

1.  **安装 `uv`**:
    如果你还没有安装，请先安装 [uv](https://github.com/astral-sh/uv)。

2.  **配置凭据**:
    将 `.env.example` 复制为 `.env` 并填写你的信息：
    ```bash
    cp .env.example .env
    ```
    编辑 `.env` 文件:
    - `ZFN_URL`: 你所在学校正方教务系统的基础 URL（必须以 `/` 结尾）。
    - `ZFN_SID`: 你的学号。
    - `ZFN_PASSWORD`: 你的密码。
    
    *注意：凭据存储在本地的 `.env` 文件中，并通过环境变量传递给服务器。*

## 本地运行

要在本地测试服务器：

```bash
uv run server.py
```

你可以使用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 进行交互调试：

```bash
npx @modelcontextprotocol/inspector uv run server.py
```

## Claude Desktop 配置

将以下内容添加到你的 `claude_desktop_config.json` 文件中：

```json
{
  "mcpServers": {
    "zhengfang": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[fastmcp]",
        "--with",
        "requests",
        "--with",
        "pyquery",
        "--with",
        "rsa",
        "server.py"
      ],
      "cwd": "/absolute/path/to/zfn_api",
      "env": {
        "ZFN_URL": "http://your-school-url.edu.cn/",
        "ZFN_SID": "your_id",
        "ZFN_PASSWORD": "your_password"
      }
    }
  }
}
```

> **注意**：你可以像上面那样直接在 `claude_desktop_config.json` 中传递环境变量，也可以依赖 `.env` 文件（这通常需要额外的配置来加载 .env，或者 `uv run` 会自动读取）。在配置文件中显式定义通常更直接。

## 可用工具 (Tools)

- `get_my_grades(year, term)`: 获取成绩
- `get_my_schedule(year, term)`: 获取课表
- `get_student_info()`: 获取学生信息
- `get_exam_schedule(year, term)`: 获取考试安排
- `login_check()`: 检查登录状态
