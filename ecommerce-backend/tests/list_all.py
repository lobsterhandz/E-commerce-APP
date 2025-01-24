from flask import Flask
from flasgger import Swagger

def list_routes_with_fields(app, swagger_template):
    output = []
    for rule in app.url_map.iter_rules():
        route = str(rule)
        endpoint = rule.endpoint
        methods = ', '.join(rule.methods)

        # Check if the route exists in Swagger docs
        doc = swagger_template.get("paths", {}).get(route, {})
        if doc:
            fields = []
            for method, details in doc.items():
                params = details.get("parameters", [])
                for param in params:
                    fields.append({
                        "name": param.get("name"),
                        "type": param.get("type", "unknown"),
                        "in": param.get("in"),
                        "required": param.get("required", False),
                        "description": param.get("description", "")
                    })
            output.append({
                "route": route,
                "endpoint": endpoint,
                "methods": methods,
                "fields": fields
            })
        else:
            output.append({
                "route": route,
                "endpoint": endpoint,
                "methods": methods,
                "fields": "No Swagger doc available"
            })

    # Print or return the output
    for route in output:
        print(f"Route: {route['route']}")
        print(f"Endpoint: {route['endpoint']}")
        print(f"Methods: {route['methods']}")
        print("Fields:")
        if isinstance(route["fields"], list):
            for field in route["fields"]:
                print(f"  - {field['name']} ({field['type']}): {field['description']} [Required: {field['required']}]")
        else:
            print("  No Swagger doc available.")
        print("-" * 80)

if __name__ == "__main__":
    from app import create_app  # Import your app factory
    app = create_app('development')  # Replace 'development' with your config name

    # Retrieve existing Swagger instance
    swagger = app.extensions.get('swagger')
    if swagger is None:
        raise RuntimeError("Swagger is not initialized in your app. Check your create_app function.")

    with app.app_context():
        swagger_template = swagger.template
        list_routes_with_fields(app, swagger_template)
