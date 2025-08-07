main.py is used with fastapi and prometheus-client 

docker compose.yml creates a prometheus and chat containers 

localhost:8000 shows the chat ui

localhost:8000/metrics prometheus metrics

localhost:9090 prometheus ui

i like to dockerize the realtime chat app and launch it on render for chat

need to work it out, check it more, theres no time enough to learn bro.......

docker compose down -v to remove the 

docker compose up --build to create 


after editing the scrape config->job of chat-app on prometheus

sudo systemctl daemon-reload
sudo systemctl restart prometheus

sudo systemctl status prometheus


to check the error
sudo journalctl -u prometheus -f


grafana-installed with docker compose

username: admin
password: cygday

http://localhost:3000

checkout how to insert username on the chat-app

username with login is not running well
