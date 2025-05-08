from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

# Chaves API válidas e seus status
VALID_API_KEYS = {
    "ZD": "active"
}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "Chave API ausente", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "Chave API inválida", "status_code": 401}
    
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "Chave API desativada", "status_code": 403}
    if status == "banned":
        return {"error": "Chave API banida", "status_code": 403}
    
    return {"valid": True} 

def check_banned(player_id):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            result = {
                "credits": "@BRSTORE",
                "channel": "https://t.me/BrStore01",
                "status": "BANIDO" if is_banned else "NÃO BANIDO",
                "ban_period": period if is_banned else 0,
                "uid": player_id,
                "is_banned": bool(is_banned)
            }

            return Response(json.dumps(result), mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Falha ao buscar dados do servidor", "status_code": 500}), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e), "status_code": 500}), mimetype="application/json")

@app.route("/bancheck", methods=["GET"])
def bancheck():
    api_key = request.args.get("key", "")
    player_id = request.args.get("uid", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    if not player_id:
        return Response(json.dumps({"error": "ID do jogador é obrigatório", "status_code": 400}), mimetype="application/json")

    return check_banned(player_id)

@app.route("/check_key", methods=["GET"])
def check_key():
    api_key = request.args.get("key", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    return Response(json.dumps({"status": "válida", "key_status": VALID_API_KEYS.get(api_key, "desconhecido")}), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)