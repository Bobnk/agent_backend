\# AI‑Agent后端项目（FastAPI）

> 本项目完成时间：2026‑10‑01

\## 📖项目简介

基于FastAPI开发的AI Agent对话后端，对接DeepSeek大模型；实现流式SSE输出聊天；手写Agent工具调用；增加JWT账号登录鉴权。适合AI后端实习练习项目。



\## 🛠技术栈

\- Python，FastAPI

\- SQLAlchemy‑ORM + SQLite（保存聊天会话数据）

\- httpx异步请求大模型接口

\- JWT登录鉴权（passlib + python‑jose，Depends依赖注入做权限校验）

\- SSE StreamingResponse实现打字机流式返回

\- 原生手写Function‑Call Agent工具循环（获取服务器时间，未使用LangChain）



\## ✨实现功能清单

1\. 用户注册、登录；JWT令牌鉴权；聊天接口需要登录才可访问

2\. SSE流式对话接口，大模型打字机效果输出回答

3\. Agent工具调用（非流式）：大模型可以调用本地工具获取服务器当前系统时间

4\. lifespan生命周期管理，服务启动初始化数据库

5\. CORS跨域配置，全局异常捕获，日志记录



\## 🚀本地运行步骤

1\. 创建python虚拟环境

2\. 安装依赖

```bash

pip install fastapi uvicorn sqlalchemy httpx python-jose\\\\\\\[cryptography] passlib\\\\\\\[bcrypt]





