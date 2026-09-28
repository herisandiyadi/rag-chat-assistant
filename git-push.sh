cd /root/rag-chat-app && git init
git remote add origin https://github.com/herisandiyadi/rag-chat-assistant.git
git pull origin master --allow-unrelated-histories || true
git add . && git commit -m "Sprint 2: Core RAG logic with 3-condition access control" 
git push -u origin master