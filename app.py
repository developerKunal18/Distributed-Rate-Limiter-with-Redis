from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

# Redis Connection
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

RATE_LIMIT = 10      # requests
WINDOW = 60          # seconds

@app.route("/api")
def api():

    client_ip = request.remote_addr

    key = f"rate:{client_ip}"

    current = redis_client.get(key)

    if current is None:

        redis_client.setex(
            key,
            WINDOW,
            1
        )

        remaining = RATE_LIMIT - 1

    else:

        current = int(current)

        if current >= RATE_LIMIT:

            return jsonify({
                "message": "Rate limit exceeded"
            }), 429

        redis_client.incr(key)

        remaining = RATE_LIMIT - current - 1

    return jsonify({
        "message": "Request Accepted",
        "remaining_requests": remaining
    })


@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


if __name__ == "__main__":

    app.run(debug=True)
