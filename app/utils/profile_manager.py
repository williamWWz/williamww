import json
import os

def load_profile(file_path="app/data/profile.json"):
    """Loads the user profile from a JSON file."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_profile(profile_data, file_path="app/data/profile.json"):
    """Saves the user profile to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4, ensure_ascii=False)

def get_default_profile():
    return {
        "personal_info": {
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin_url": "",
            "github_url": "",
            "portfolio_url": ""
        },
        "education": [
            {
                "school": "",
                "degree": "",
                "major": "",
                "start_date": "",
                "end_date": ""
            }
        ],
        "experience": [
            {
                "company": "",
                "title": "",
                "start_date": "",
                "end_date": "",
                "description": ""
            }
        ],
        "skills": []
    }
