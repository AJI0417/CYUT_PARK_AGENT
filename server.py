from flask import Flask, render_template

from db.initialize import initialize_database
from routes.announcement_routes import announcement_bp
from routes.facility_routes import facility_bp
from routes.line_routes import line_bp


app = Flask(__name__)

initialize_database()

app.register_blueprint(facility_bp)
app.register_blueprint(announcement_bp)
app.register_blueprint(line_bp)


@app.get("/")
def index():
    """顯示朝陽主題樂園營運輔助 Agent 介紹頁。"""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
