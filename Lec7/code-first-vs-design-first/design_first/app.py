from pathlib import Path

import connexion


BASE_DIR = Path(__file__).parent
application = connexion.FlaskApp(__name__, specification_dir=str(BASE_DIR / "openapi"))
application.add_api("products.yaml", pythonic_params=True)
app = application.app


if __name__ == "__main__":
    application.run(port=5002)

