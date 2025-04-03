from flask import Flask, request, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

# 📌 Define Parquet files
DATA_FILES = {
    6: "data/pm_mean_last_6_months.parquet",
    12: "data/pm_mean_last_12_months.parquet"
}

@app.route("/")
def serve_homepage():
    """
    Serve the main HTML file when the root URL is accessed.
    """
    return send_file("ddorf_embed.html")

@app.route("/get-data", methods=["POST"])
def get_data():
    try:
        # Retrieve JSON data from the request
        data = request.json
        x_value = str(data.get("x"))  # x as string
        y_value = str(data.get("y"))  # y as string
        z_count = int(data.get("z", 6))  # Default value: 6

        # 🔹 Construct ID
        search_id = f"CRS3035RES1000mN{y_value}E{x_value}"

        print(search_id)

        # 📌 Load the appropriate file based on `z`
        if z_count not in DATA_FILES:
            return jsonify({"error": "Invalid value for 'z'. Use 6 or 12."}), 400

        parquet_file = DATA_FILES[z_count]

        if not os.path.exists(parquet_file):
            return jsonify({"error": f"Data file {parquet_file} not found"}), 500

        df = pd.read_parquet(parquet_file)

        # 🔎 Search for ID
        row = df[df["ID"] == search_id]

        if row.empty:
            return jsonify({"error": "No matching data found"}), 404

        # ✅ Return pollution value
        pollution_value = row.iloc[0]["pollution"]
        return jsonify({"values": pollution_value})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<path:filename>")
def serve_file(filename):
    """
    Serve requested files directly if they exist.
    """
    file_path = f"./{filename}"
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
