from flask import Flask, jsonify, request, abort
import os
import requests
import yaml

app = Flask(__name__)

# Environment-based configuration
HASS_URL = "https://jandcsmarthome.duckdns.org"
TOKEN = os.getenv("HASS_TOKEN")
SHARED_SECRET = os.getenv("HASS_SECRET")

if not TOKEN or not SHARED_SECRET:
    raise EnvironmentError("HASS_TOKEN and HASS_SECRET environment variables must be set.")

def auth_header():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def require_api_key():
    api_key = request.headers.get("x-api-key")
    print(f"🔐 Incoming x-api-key: {api_key}")
    print(f"🔒 Backend HASS_SECRET: {SHARED_SECRET}")
    if api_key != SHARED_SECRET:
        abort(401, description="Invalid API key")

@app.route('/')
def index():
    return 'Flask is up and running!'

@app.route("/hass/check-key", methods=["GET"])
def check_key():
    require_api_key()
    return jsonify({"status": "Key is valid"})

@app.route("/hass/entities", methods=["GET"])
def get_entities():
    require_api_key()
    try:
        response = requests.get(f"{HASS_URL}/api/states", headers=auth_header())
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/services", methods=["GET"])
def list_services():
    require_api_key()
    try:
        response = requests.get(f"{HASS_URL}/api/services", headers=auth_header())
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/state/<entity_id>", methods=["GET"])
def get_state(entity_id):
    require_api_key()
    try:
        response = requests.get(f"{HASS_URL}/api/states/{entity_id}", headers=auth_header())
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/state/<entity_id>", methods=["POST"])
def set_state(entity_id):
    require_api_key()
    state = request.json.get("state")
    if not state:
        return jsonify({"error": "Missing state"}), 400
    try:
        payload = {"state": state}
        response = requests.post(f"{HASS_URL}/api/states/{entity_id}", headers=auth_header(), json=payload)
        response.raise_for_status()
        return jsonify({"status": "State updated"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/script", methods=["POST"])
def run_script():
    require_api_key()
    data = request.json
    entity_id = data.get("entity_id")

    if not entity_id:
        return jsonify({"error": "Missing entity_id"}), 400

    try:
        response = requests.post(
            f"{HASS_URL}/api/services/script/turn_on",
            headers=auth_header(),
            json={"entity_id": entity_id}
        )
        response.raise_for_status()
        return jsonify({"status": "Script executed"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/scene", methods=["POST"])
def activate_scene():
    require_api_key()
    data = request.json
    entity_id = data.get("entity_id")
    if not entity_id:
        return jsonify({"error": "Missing entity_id"}), 400
    try:
        response = requests.post(
            f"{HASS_URL}/api/services/scene/turn_on",
            headers=auth_header(),
            json={"entity_id": entity_id}
        )
        response.raise_for_status()
        return jsonify({"status": "Scene activated"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/state/<entity_id>", methods=["GET"])
def get_entity_state(entity_id):
    require_api_key()
    try:
        response = requests.get(f"{HASS_URL}/api/states/{entity_id}", headers=auth_header())
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/automation", methods=["POST"])
def create_automation():
    require_api_key()
    automation = request.json.get("automation")
    if not automation:
        return jsonify({"error": "Missing automation payload"}), 400
    try:
        file_path = "/var/lib/homeassistant/homeassistant/automations.yaml"
        with open(file_path, "a") as file:
            yaml.dump([automation], file, sort_keys=False)
        response = requests.post(f"{HASS_URL}/api/services/automation/reload", headers=auth_header())
        response.raise_for_status()
        return jsonify({"status": "Automation created and reloaded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/reload/<domain>", methods=["POST"])
def reload_domain(domain):
    require_api_key()
    try:
        response = requests.post(f"{HASS_URL}/api/services/{domain}/reload", headers=auth_header())
        response.raise_for_status()
        return jsonify({"status": f"{domain} domain reloaded"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/call-service/<domain>/<service>", methods=["POST"])
def call_service(domain, service):
    require_api_key()
    data = request.json or {}
    try:
        response = requests.post(
            f"{HASS_URL}/api/services/{domain}/{service}",
            headers=auth_header(),
            json=data
        )
        response.raise_for_status()
        return jsonify({"status": f"{domain}.{service} called"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hass/config", methods=["GET"])
def get_config():
    require_api_key()
    try:
        response = requests.get(f"{HASS_URL}/api/config", headers=auth_header())
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

@app.route("/debug/token")
def debug_token():
    return jsonify({"token": TOKEN})
