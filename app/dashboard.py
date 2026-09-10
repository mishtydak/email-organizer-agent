from flask import Flask, render_template, jsonify, request
import os
import sys

# Add the app directory to sys.path so we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dashboard_service import DashboardService

app = Flask(__name__)
service = DashboardService()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def get_state():
    return jsonify(service.get_state())

@app.route("/api/process", methods=["POST"])
def process_inbox():
    try:
        service.process_inbox()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/drafts/<draft_id>/edit", methods=["POST"])
def edit_draft(draft_id):
    data = request.json
    try:
        service.edit_draft(draft_id, data.get("subject"), data.get("body"))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/drafts/<draft_id>/approve", methods=["POST"])
def approve_draft(draft_id):
    data = request.json
    try:
        service.approve_draft(draft_id, data.get("reviewer", "Faculty"))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/drafts/<draft_id>/reject", methods=["POST"])
def reject_draft(draft_id):
    data = request.json
    try:
        service.reject_draft(draft_id, data.get("reviewer", "Faculty"))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/drafts/<draft_id>/send", methods=["POST"])
def send_draft(draft_id):
    try:
        service.send_draft(draft_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/tasks/<task_id>/complete", methods=["POST"])
def complete_task(task_id):
    try:
        service.complete_task(task_id, confirmed=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/followups/<followup_id>/complete", methods=["POST"])
def complete_followup(followup_id):
    try:
        service.complete_followup(followup_id, confirmed=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/meetings/<meeting_id>/confirm", methods=["POST"])
def confirm_meeting(meeting_id):
    data = request.json
    try:
        service.confirm_meeting(meeting_id, data.get("slot"), approved=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
