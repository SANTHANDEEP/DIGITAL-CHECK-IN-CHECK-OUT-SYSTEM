from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import json_util
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://saikrishnajayanth2020:jayanth@cluster0.fheg17w.mongodb.net/")
db = client["Project"]
collection = db["Students"]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/api/students", methods=["GET"])
def get_student():
    try:
        reg_no = request.args.get("reg_no")
        student = collection.find_one({"reg_no": reg_no})

        if student:
            # Convert ObjectId to string before jsonify
            student["_id"] = str(student["_id"])
            return jsonify(student)
        else:
            return jsonify({"error": "Student not found"}), 404

    except ValueError:
        return jsonify({"error": "Invalid Registration Number"}), 400

@app.route("/api/students/update", methods=["POST"])
def update_details():
    try:
        reg_no = request.form.get("reg_no")
        update_type = request.form.get("update_type")

        # Get the current date and time
        current_datetime = datetime.now()
        timestamp = current_datetime.isoformat()

        # Fields to update
        update_fields = {}

        if update_type == "check_out":
            update_fields["time_of_leaving"] = current_datetime.strftime("%H:%M:%S")
            # Decrease credit by 1
            update_fields["credit"] = max(0, collection.find_one({"reg_no": reg_no})["credit"] - 1)
        elif update_type == "check_in":
            update_fields["actual_date_of_return"] = current_datetime.strftime("%Y-%m-%d")
            update_fields["time_of_return"] = timestamp
            # Decrease credit by 1
            update_fields["credit"] = max(0, collection.find_one({"reg_no": reg_no})["credit"] - 1)

        # Update the MongoDB document
        result = collection.update_one(
        {"reg_no": reg_no},
        {"$set": update_fields}
        )

        # Fetch the updated document
        updated_student = collection.find_one({"reg_no": reg_no})   

        # Include credit in the response
        updated_student["credit"] = result.modified_count > 0 and updated_student.get("credit", 0)

        # Return the updated student details
        return jsonify(updated_student)

        if result.modified_count > 0:
            return jsonify({"message": "Details updated successfully!"})
        else:
            return jsonify({"error": "Failed to update details"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)



