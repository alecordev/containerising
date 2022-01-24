import os
import redis
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

r = redis.Redis(password=os.getenv("REDIS_PASSWORD"))
r.set("key", 2)

resp = int(r.get("key").decode())
print(resp)

assert resp == 2

r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
print(r.get("Bahamas"))
