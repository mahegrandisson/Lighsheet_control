import yaml

CONFIG_FOLDER = "../config/"
B_PARAMS = CONFIG_FOLDER + "brillouin_params.yaml"
CONFIG = CONFIG_FOLDER + "galvo_pi_config.yaml"
# SYS_CONFIG = r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaFlash_orcaQuest.cfg"
SYS_CONFIG = r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaflash4.cfg"


galvo1_val = 0
galvo2_val = 0
pi1_val = 11
pi2_val = 80
pi3_val = 14.35
pi4_val = 12

pi_widgets = []


def load_yaml(
    path: str,
):
    with open(
        path,
        "r",
    ) as file:
        return yaml.safe_load(file)


def save_yaml(
    dictionnaire,
    chemin,
):
    with open(
        chemin,
        "w",
    ) as file:
        yaml.dump(
            dictionnaire,
            file,
            default_flow_style=False,
        )


def save_params_for_all_widgets(
    pi_widgets,
):
    def decorator(
        func,
    ):
        def wrapper(
            *args,
            **kwargs,
        ):

            for widget in pi_widgets:
                if hasattr(
                    widget,
                    "save_params",
                ):
                    widget.save_params()

            return func(
                *args,
                **kwargs,
            )

        return wrapper

    return decorator
