from pathlib import Path

from flask import Flask, abort, render_template_string, send_from_directory
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields, validate


app = Flask(__name__)
OPENAPI_DIR = Path(__file__).parent / "openapi"
app.config.update(
    API_TITLE="Products API - Code-First",
    API_VERSION="1.0.0",
    OPENAPI_VERSION="3.0.3",
)
api = Api(app)
products_blp = Blueprint("products", __name__, url_prefix="/products", description="Product operations")


class ProductSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    # stock = fields.Int(required=True)


class ProductInputSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))


products = [
    {"id": 1, "name": "Coffee", "price": 4.5},
    {"id": 2, "name": "Tea", "price": 3.0},
]


@products_blp.route("")
class ProductCollection(MethodView):
    @products_blp.response(200, ProductSchema(many=True))
    def get(self):
        """List products."""
        return products

    @products_blp.arguments(ProductInputSchema)
    @products_blp.response(201, ProductSchema)
    def post(self, body):
        """Create a product."""
        product = {"id": len(products) + 1, **body}
        products.append(product)
        return product


api.register_blueprint(products_blp)


@app.get("/openapi/<version>/openapi.yaml")
def openapi_yaml(version):
    """Serve one of the versioned generated OpenAPI files."""
    version_dir = OPENAPI_DIR / version
    if not version_dir.is_dir() or not version.startswith("v"):
        abort(404)
    return send_from_directory(version_dir, "openapi.yaml", mimetype="text/yaml")


@app.get("/swagger/<version>")
def swagger_ui(version):
    """Display Swagger UI for a generated OpenAPI version."""
    spec_path = OPENAPI_DIR / version / "openapi.yaml"
    if not version.startswith("v") or not spec_path.is_file():
        abort(404)
    spec_url = f"/openapi/{version}/openapi.yaml"
    return render_template_string(
        """
        <!doctype html>
        <html>
          <head>
            <title>Products API - {{ version }}</title>
            <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
          </head>
          <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
              SwaggerUIBundle({url: {{ spec_url|tojson }}, dom_id: '#swagger-ui'});
            </script>
          </body>
        </html>
        """,
        version=version,
        spec_url=spec_url,
    )


if __name__ == "__main__":
    app.run(port=5001, debug=True)

