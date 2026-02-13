from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "granite:3.3-2b"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>GenAI Curriculum Generator</title>
    <style>
        body {
            font-family: Arial;
            text-align: center;
            background: linear-gradient(to right, #4e73df, #1cc88a);
            color: white;
            padding: 20px;
        }

        .form-container {
            margin: 20px auto;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            width: 350px;
            border-radius: 10px;
        }

        input {
            margin: 5px;
            padding: 8px;
            width: 90%;
            border-radius: 5px;
            border: none;
        }

        button {
            padding: 10px;
            margin: 10px;
            background-color: black;
            color: white;
            cursor: pointer;
            border-radius: 5px;
            border: none;
        }

        #result {
            margin: 20px auto;
            white-space: pre-wrap;
            background: white;
            color: black;
            padding: 20px;
            width: 70%;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <h1>GenAI Curriculum Generator</h1>

    <div class="form-container">
        <input type="text" id="skill" placeholder="Skill (e.g. Machine Learning)">
        <input type="text" id="level" placeholder="Level (Diploma/Masters)">
        <input type="number" id="semesters" placeholder="Semesters">
        <input type="text" id="weekly_hours" placeholder="Weekly Hours">
        <input type="text" id="industry" placeholder="Industry Focus">
        <button onclick="generateCurriculum()">Generate</button>
    </div>

    <div id="result"></div>
    <button onclick="downloadPDF()">Download PDF</button>

    <script>
    async function generateCurriculum() {
        const data = {
            skill: document.getElementById("skill").value,
            level: document.getElementById("level").value,
            semesters: document.getElementById("semesters").value,
            weekly_hours: document.getElementById("weekly_hours").value,
            industry: document.getElementById("industry").value
        };

        const response = await fetch("/api/generate-curriculum", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const result = await response.json();
        document.getElementById("result").innerText = result.curriculum;
    }

    async function downloadPDF() {
        const content = document.getElementById("result").innerText;

        const response = await fetch("/api/download-pdf", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({content: content})
        });

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "curriculum.pdf";
    a.click();
});
</script>

</body>
</html>
"""


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/api/generate-curriculum", methods=["POST"])
def generate_curriculum():
    data = request.json

    skill = data["skill"]
    level = data["level"]
    semesters = data["semesters"]
    weekly_hours = data["weekly_hours"]
    industry = data["industry"]

    prompt = f"""
    Create a {level} level curriculum for {skill}.
    Duration: {semesters} semesters.
    Weekly Hours: {weekly_hours}.
    Industry Focus: {industry}.
    
    Provide:
    - Semester wise course names
    - 5 topics per course
    - Course description
    - Learning outcomes
    """

    response = requests.post(OLLAMA_URL, json={
        "model": "granite:3.3-2b",
        "prompt": prompt,
        "stream": False
    })

    result = response.json()["response"]

    return jsonify({"curriculum": result})


@app.route("/api/download-pdf", methods=["POST"])
def download_pdf():
    content = request.json["content"]
    file_path = generate_pdf(content)
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)



