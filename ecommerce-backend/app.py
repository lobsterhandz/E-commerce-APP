from app import create_app
from flask import Flask, jsonify
from flask_cors import CORS

# Create the app instance
app = create_app()

# Enable CORS immediately after app creation
CORS(app)

@app.route('/')
def home():
    return {'message': 'Welcome to the E-Commerce API'}

@app.route('/routes', methods=['GET'])
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(str(rule))
        output.append(f"{url} -> {methods}")
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
