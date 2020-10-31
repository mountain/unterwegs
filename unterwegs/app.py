from flask_appfactory import appfactory
from flask_compress import Compress


compress = Compress()


def create_app(load=True, **kwargs_config):
    app = appfactory(
        "unterwegs",
        "unterwegs.config",
        load=load,
        **kwargs_config
    )
    compress.init_app(app)

    return app
