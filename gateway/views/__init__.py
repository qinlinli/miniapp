from .send import bp as send_bp


def register_app(app):
    app.blueprint(send_bp)