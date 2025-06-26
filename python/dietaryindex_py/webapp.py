from __future__ import annotations
import io
from flask import Flask, request, send_file, render_template
from . import acs2020_v1, acs2020_v2, ahei

app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    score = request.form.get("score", "acs2020_v1")
    if not file:
        return "No file uploaded", 400

    df = None
    try:
        import pandas as pd
        df = pd.read_csv(file)
    except Exception as e:
        return f"Failed to read CSV: {e}", 400

    func = {
        "acs2020_v1": acs2020_v1,
        "acs2020_v2": acs2020_v2,
        "ahei": ahei,
    }.get(score, acs2020_v1)

    out = func(df)
    if not isinstance(out, pd.DataFrame):
        out = pd.DataFrame(out)

    buf = io.BytesIO()
    out.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="text/csv",
        as_attachment=True,
        download_name="scores.csv",
    )

if __name__ == "__main__":
    app.run(debug=True)
