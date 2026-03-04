from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
import re

app = Flask(__name__)

# Intensity modifiers to judge skill strength
MODIFIERS = {
    "strong": 1.0, "expert": 1.0, "advanced": 1.0, "professional": 0.9,
    "good": 0.7, "intermediate": 0.6, "basic": 0.4, "beginner": 0.3
}

ROLE_PROFILES = {
    "ai": ["python", "java", "machine learning", "svm", "knn", "neural networks", "scikit-learn"],
    "frontend": ["html5", "css", "javascript", "react", "bootstrap"],
    "data": ["sql", "python", "power bi", "pandas", "statistics"]
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        resume_text = data.get("text", "").lower()
        role = data.get("role", "ai")
        required_skills = ROLE_PROFILES.get(role, [])

        tokens = re.findall(r'\b\w+\b', resume_text)
        total_score = 0
        matched = []

        for skill in required_skills:
            if skill in resume_text:
                matched.append(skill.capitalize())
                weight = 0.6  # Default weight
                # Context Search: Check 4 words before the skill
                try:
                    first_word = skill.split()[0]
                    if first_word in tokens:
                        idx = tokens.index(first_word)
                        window = tokens[max(0, idx-4):idx]
                        for word in window:
                            if word in MODIFIERS:
                                weight = MODIFIERS[word]
                                break
                except: pass
                total_score += weight

        final_score = int((total_score / len(required_skills)) * 100) if required_skills else 0
        missing = [s.capitalize() for s in required_skills if s.capitalize() not in matched]

        return jsonify({
            "score": min(final_score, 100),
            "missing": missing[:5],
            "status": "Success"
        })
    except Exception as e:
        return jsonify({"score": 0, "error": str(e)}), 200

# FIX: Keep this at the absolute bottom
if __name__ == '__main__':
    app.run(debug=True)