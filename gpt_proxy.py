from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/public/<path:path>', methods=['GET','POST','PUT','DELETE','PATCH'])
def public_proxy(path):
    url = f'http://localhost:5000/{path}'
    resp = requests.request(
        method=request.method,
        url=url,
        headers={'x-api-key': 'nasteesecret123'},
        params=request.args,
        json=request.get_json(silent=True),
        data=request.get_data(),
        allow_redirects=False
    )
    excluded = {'content-encoding','transfer-encoding','connection'}
    headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]
    return Response(resp.content, status=resp.status_code, headers=headers, content_type=resp.headers.get('Content-Type'))

if __name__ == '__main__':
    app.run(port=5002)
