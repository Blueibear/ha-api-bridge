import os
import logging
from flask import Flask, request, Response
import requests

# Target Home Assistant internal API
REAL_API_BASE = "http://127.0.0.1:5001"

# Log everything to file
logging.basicConfig(
    filename='/home/james/gpt_proxy.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

app = Flask(__name__)

@app.route('/public/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def public_proxy(path):
    try:
        # Log incoming request
        logging.info("=== REQUEST START ===")
        logging.info("Received %s /public/%s", request.method, path)
        logging.info("Headers: %s", {k: v for k, v in request.headers.items() if k.lower() != 'host'})
        logging.info("Body: %s", request.get_data(as_text=True))
        logging.info("=== REQUEST END ===")

        # Forward request
        target_url = f"{REAL_API_BASE}/{path}"
        headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
        headers['Authorization'] = f"Bearer {os.getenv('HASS_API_KEY')}"
        headers['x-api-key'] = os.getenv('HASS_SECRET')

        # Log the injected secret
        logging.info("Injected HASS_SECRET: %s", os.getenv('HASS_SECRET'))

        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            allow_redirects=False,
        )

        return Response(resp.content, resp.status_code, resp.headers.items())

    except Exception as e:
        logging.error("Proxy error: %s", str(e))
        return Response(f"Proxy Error: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

