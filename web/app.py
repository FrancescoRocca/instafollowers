from flask import Flask, render_template, request, jsonify
import json
import logging

app = Flask(__name__, template_folder="./pages/")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate_difference", methods=["POST"])
def calculate_difference():
    try:
        # Check if files are present
        if (
            "followers_json" not in request.files
            or "following_json" not in request.files
        ):
            return jsonify({"error": "Missing required JSON files."}), 400

        followers_file = request.files["followers_json"]
        following_file = request.files["following_json"]

        # Check if files are actually selected
        if followers_file.filename == "" or following_file.filename == "":
            return jsonify({"error": "No files selected."}), 400

        # Validate file extensions
        if not (
            followers_file.filename.endswith(".json")
            and following_file.filename.endswith(".json")
        ):
            return jsonify({"error": "Please upload only JSON files."}), 400

        # Read and parse JSON data
        try:
            followers_data = json.loads(followers_file.read())
            following_data = json.loads(following_file.read())
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400

        # Validate JSON structure
        if not isinstance(followers_data, list):
            return jsonify({"error": "Followers JSON must be an array."}), 400

        if (
            not isinstance(following_data, dict)
            or "relationships_following" not in following_data
        ):
            return jsonify(
                {
                    "error": "Following JSON must contain 'relationships_following' field."
                }
            ), 400

        diff = difference(followers_data, following_data)
        num_names = len(diff)

        logger.info(f"Successfully calculated difference: {num_names} names")
        return jsonify({"diff": sorted(list(diff)), "num_names": num_names})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify(
            {"error": "An unexpected error occurred. Please try again."}
        ), 500


def extract_following(json_data):
    names = set()
    try:
        for relationship in json_data.get("relationships_following", []):
            if (
                "string_list_data" in relationship
                and len(relationship["string_list_data"]) > 0
            ):
                name = relationship["string_list_data"][0].get("value")
                if name:
                    names.add(name)
    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Error extracting following data: {str(e)}")
    return names


def extract_followers(json_data):
    names = set()
    try:
        for follower in json_data:
            if "string_list_data" in follower and len(follower["string_list_data"]) > 0:
                name = follower["string_list_data"][0].get("value")
                if name:
                    names.add(name)
    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Error extracting followers data: {str(e)}")
    return names


def difference(json1, json2):
    set1 = extract_followers(json1)
    set2 = extract_following(json2)
    diff = set2 - set1
    return diff


if __name__ == "__main__":
    app.run(debug=True)
