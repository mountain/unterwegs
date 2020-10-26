from flask_appfactory import appfactory


def create_app(load=True, **kwargs_config):
    return appfactory(
        "unterwegs",
        "unterwegs.config",
        load=load,
        **kwargs_config
    )
