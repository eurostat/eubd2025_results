from flask import Flask
from routes.index import index_bp
from routes.agriculture import agriculture_bp
from routes.soil_moisture import soil_moisture_bp
from routes.docs import docs_bp
from routes.drought_index import drought_index_bp
from routes.forecasts import forecasts_bp
from routes.spacial_analysis import spacial_analysis_bp
from routes.tasmi import tasmi_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(index_bp)
app.register_blueprint(agriculture_bp)
app.register_blueprint(soil_moisture_bp)
app.register_blueprint(docs_bp)
app.register_blueprint(drought_index_bp)
app.register_blueprint(forecasts_bp)
app.register_blueprint(spacial_analysis_bp)
app.register_blueprint(tasmi_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8091)
