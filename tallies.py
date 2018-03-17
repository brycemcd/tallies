import datetime as dt
from flask import Flask
from flask import jsonify
from redis import Redis, RedisError

app = Flask(__name__)

# Connect to Redis
redis = Redis(host="redis",
              db=0,
              socket_connect_timeout=2,
              socket_timeout=2,
              decode_responses=True,
              )


@app.route('/v1/tally/<tallyable>')
def tally(tallyable='misfire'):
    try:
        # NOTE: this is really dangerous, but it only runs on my computer on my network
        redis.lpush(tallyable, dt.datetime.now().isoformat())
        tallies = redis.lrange(tallyable, -10, -1)
        length = redis.llen(tallyable)
        success = {
            "success": True,
            "tallyable": tallyable,
            "tallyable_cnt": length,
            "tallies": list(tallies),
        }
        return jsonify(success)
    except RedisError as e:
        failure = {"success": False}
        return jsonify(failure)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
