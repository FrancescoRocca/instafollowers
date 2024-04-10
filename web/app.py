from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__, template_folder="./pages/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate_difference", methods=["POST"])
def calculate_difference():
    try:
        # Validate file types (example)
        if (
            request.files["followers_json"].content_type != "application/json"
            or request.files["following_json"].content_type != "application/json"
        ):
            return jsonify({"error": "Invalid file format. Please upload JSON files."})

        followers_data = request.files["followers_json"].read()
        following_data = request.files["following_json"].read()

        # JSON parsing with error handling
        followers_data = json.loads(followers_data)
        following_data = json.loads(following_data)

        diff = difference(followers_data, following_data)
        num_names = len(diff)

        return jsonify({"diff": list(diff), "num_names": num_names})
    except (json.JSONDecodeError, FileNotFoundError) as e:
        # Handle errors gracefully
        return jsonify({"error": f"Error processing data: {str(e)}"})


def extract_following(json_data):
    names = set()
    for relationship in json_data.get("relationships_following", []):
        name = relationship["string_list_data"][0]["value"]
        if name:
            names.add(name)
    return names


def extract_followers(json_data):
    names = set()
    for follower in json_data:
        name = follower["string_list_data"][0]["value"]
        if name:
            names.add(name)
    return names


def difference(json1, json2):
    set1 = extract_followers(json1)
    set2 = extract_following(json2)
    diff = set2 - set1
    return diff


if __name__ == "__main__":
    app.run(debug=True)
