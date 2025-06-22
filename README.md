# GraphDo
An intelligent ToDo agent powered by LangGraph, built for managing and reasoning over daily tasks.

Use `langgraph + langchain + openai` for agent
And  `vue3 + litestar + postgreSQL` for web app


run: 
```bash
git clone https://github.com/break1145/GraphDo.git
cd GraphDo
docker-compose up -d
```
默认在80端口开启

需要按照.env.example填写相关信息，并命名为.env。如api-key等。注意frontend/.env.example也需要填写
