import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import gspread
import hashlib
import base64
import secrets
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # solo para desarrollo local

CLIENT_SECRETS_FILE = "client_secret.json"

def get_client_secrets_file():
    client_secret_json = os.environ.get("GOOGLE_CLIENT_SECRET")
    if client_secret_json:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        tmp.write(client_secret_json)
        tmp.flush()
        return tmp.name
    return CLIENT_SECRETS_FILE

SPREADSHEET_NAME = "Gym Tracker"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# ── AUTH HELPERS ───────────────────────────────────────────────────────────────

def get_gspread_client():
    creds_data = session.get("credentials")
    if not creds_data:
        return None
    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"]
    )
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_gspread_client()
    if not client:
        return None
    spreadsheet = client.open(SPREADSHEET_NAME)
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=sheet_name, rows=500, cols=20)

def is_logged_in():
    return "credentials" in session


# ── AUTH ROUTES ────────────────────────────────────────────────────────────────

@app.route("/login")
def login():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()
    session["code_verifier"] = code_verifier

    flow = Flow.from_client_secrets_file(get_client_secrets_file(), scopes=SCOPES)
    flow.redirect_uri = url_for("callback", _external=True)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow = Flow.from_client_secrets_file(
        get_client_secrets_file(), scopes=SCOPES, state=session["state"]
    )
    flow.redirect_uri = url_for("callback", _external=True)
    flow.fetch_token(
        authorization_response=request.url,
        code_verifier=session["code_verifier"]
    )
    creds = flow.credentials
    session["credentials"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ── TEMPLATES ──────────────────────────────────────────────────────────────────

@app.route("/api/templates", methods=["GET"])
def get_templates():
    if not is_logged_in():
        return jsonify({"ok": False, "error": "no_auth"}), 401
    try:
        sheet = get_sheet("Templates")
        records = sheet.get_all_records()
        templates = {}
        for row in records:
            day = str(row.get("dia"))
            if day not in templates:
                templates[day] = {"activacion": [], "bloques": {"A": [], "B": [], "C": [], "D": []}}
            section = row.get("seccion")
            exercise = {
                "nombre": row.get("ejercicio"),
                "sets": row.get("sets"),
                "reps": row.get("reps")
            }
            if section == "activacion":
                templates[day]["activacion"].append(exercise)
            elif section in templates[day]["bloques"]:
                templates[day]["bloques"][section].append(exercise)
        return jsonify({"ok": True, "templates": templates})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/templates", methods=["POST"])
def save_templates():
    if not is_logged_in():
        return jsonify({"ok": False, "error": "no_auth"}), 401
    try:
        data = request.json
        sheet = get_sheet("Templates")
        all_records = sheet.get_all_values()

        # Borrar filas del día que se actualiza
        rows_to_delete = []
        for i, row in enumerate(all_records[1:], start=2):
            if row and str(row[0]) == str(data["dia"]):
                rows_to_delete.append(i)
        for row_idx in reversed(rows_to_delete):
            sheet.delete_rows(row_idx)

        # Asegurar header
        all_records = sheet.get_all_values()
        if not all_records or all_records[0] != ["dia", "seccion", "ejercicio", "sets", "reps"]:
            sheet.clear()
            sheet.append_row(["dia", "seccion", "ejercicio", "sets", "reps"])

        for ex in data.get("activacion", []):
            sheet.append_row([data["dia"], "activacion", ex["nombre"], ex["sets"], ex["reps"]])
        for bloque, ejercicios in data.get("bloques", {}).items():
            for ex in ejercicios:
                sheet.append_row([data["dia"], bloque, ex["nombre"], ex["sets"], ex["reps"]])

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── LOG ────────────────────────────────────────────────────────────────────────

@app.route("/api/log", methods=["POST"])
def save_log():
    if not is_logged_in():
        return jsonify({"ok": False, "error": "no_auth"}), 401
    try:
        data = request.json
        sheet = get_sheet("Log")
        all_values = sheet.get_all_values()
        header = ["session_id", "fecha", "semana", "dia", "seccion", "ejercicio", "sets", "reps", "peso", "comentario"]
        if not all_values:
            sheet.append_row(header)
        elif all_values[0] != header:
            sheet.update(range_name="A1", values=[header])
        for row in data["rows"]:
            sheet.append_row([
                data["session_id"], data["fecha"], data["semana"], data["dia"],
                row["seccion"], row["ejercicio"], row["sets"], row["reps"], row["peso"],
                row.get("comentario", "")
            ])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/log", methods=["GET"])
def get_log():
    if not is_logged_in():
        return jsonify({"ok": False, "error": "no_auth"}), 401
    try:
        sheet = get_sheet("Log")
        records = sheet.get_all_records()
        return jsonify({"ok": True, "log": records})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/log/<session_id>", methods=["PUT"])
def update_log(session_id):
    if not is_logged_in():
        return jsonify({"ok": False, "error": "no_auth"}), 401
    try:
        data = request.json
        sheet = get_sheet("Log")
        all_values = sheet.get_all_values()
        header = all_values[0]
        sid_col = header.index("session_id")
        ej_col = header.index("ejercicio")
        sec_col = header.index("seccion")
        peso_col = header.index("peso")
        updated = False
        for i, row in enumerate(all_values[1:], start=2):
            if row[sid_col] == session_id and row[ej_col] == data["ejercicio"] and row[sec_col] == data["seccion"]:
                sheet.update_cell(i, peso_col + 1, data["peso"])
                updated = True
        return jsonify({"ok": updated})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── MAIN ───────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", logged_in=is_logged_in())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
