import json
import redis

settings_path=f"C:/Users/zhixian/OneDrive/Settings/RedisLabs/.redis-labs.json"

with open(settings_path, "r", encoding="utf-8") as settings_file:
    redis_settings = json.load(settings_file)

redis_host       = redis_settings['minidb']['url']
redis_port      = redis_settings['minidb']['port']
redis_password  = redis_settings['minidb']['password']

r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
r.set('hello', 'world')
print(r.get('hello'))
