import datetime as dt
from dateutil.parser import parse as dt_parse
from flask import Flask
from flask import jsonify
from redis import Redis, RedisError
from tally.tallyable import Tallyable

app = Flask(__name__)

# Connect to Redis
redis = Redis(host="redis",
              db=0,
              socket_connect_timeout=2,
              socket_timeout=2,
              decode_responses=True,
              )


@app.route('/v1/tally/<tallyable>', methods=['POST'])
def post_tally(tallyable='misfire'):
    try:
        # NOTE: this is really dangerous, but it only runs on my computer on my network
        redis.lpush(tallyable, dt.datetime.now().isoformat())
        return jsonify(_success_dict(tallyable))
    except RedisError as e:
        failure = {"success": False}
        return jsonify(failure)


@app.route('/v1/tally/<tallyable>', methods=['GET'])
def get_tally(tallyable='misfire'):
    try:
        return jsonify(_success_dict(tallyable))
    except RedisError as e:
        failure = {"success": False}
        return jsonify(failure)

@app.route('/v1/tally/<date>/<tallyable>', methods=['POST'])
def post_tally_and_date(date, tallyable='misfire'):
    try:
        tallies = Tallyable(redis, tallyable)
        tallies.add(dt_parse(date))
        dttms, length = tallies.get_tallies_for_tallyable()

        success = {
            "success": True,
            "tallyable": tallyable,
            "tallyable_cnt": length,
            "tallies": dttms,
        }
        return jsonify(success)
    except RedisError as e:
        failure = {"success": False}
        return jsonify(failure)

def _get_tallies_for_tallyable(tallyable):
    "Return a list of the last 10 tally times and total count in a tuple"
    tallies = redis.lrange(tallyable, 0, 9)
    length = redis.llen(tallyable)
    return (tallies, length)


def _success_dict(tallyable):
    "A dict representing the structure of a successful response for a tallyable"
    tallies, length = _get_tallies_for_tallyable(tallyable)
    success = {
        "success": True,
        "tallyable": tallyable,
        "tallyable_cnt": length,
        "tallies": list(tallies),
    }
    return success


if __name__ == '__main__':
    app.run()
