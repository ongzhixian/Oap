import redis
r = redis.Redis()
r = redis.Redis(host='172.30.157.57', port=32638, db=0)
r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
r.get("Bahamas")