redis://username:password@localhost:6380/0

```bash
sudo docker compose down -v
sudo docker compose up -d --force-recreate --remove-orphans
sudo docker exec -it redis_container redis-cli
sudo docker compose up --build --watch  store
sudo docker compose up --watch  store
```



