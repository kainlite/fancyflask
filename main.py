import os
from flask import Flask
from waitress import serve
from redis import Redis

app = Flask(__name__)
redis = Redis(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    password=os.environ['REDIS_PASSWORD'],
)
bind_port = int(os.environ['BIND_PORT'])

@app.route('/readyz')
def readyz():
    redis.ping()
    return '{ "status": "All good" }'

@app.route('/livez')
def livez():
    return '{ "status": "IT\'S ALIVE!!!" }'

@app.route('/')
def hello():
    redis.incr('hits')
    total_hits = redis.get('hits').decode()
    return f'Hello from Redis! I have been seen {total_hits} times.'


if __name__ == "__main__":
    if "DEBUG" in os.environ:
        app.run(host="0.0.0.0", debug=True, port=bind_port)
    else:
        # Production runner, TODO: logger
        serve(app, host='0.0.0.0', port=bind_port)
