import yaml

# Paths to configuration files
CONFIG_FOLDER = "config/"
B_PARAMS = CONFIG_FOLDER + "brillouin_params.yaml"
F_PARAMS = CONFIG_FOLDER + "fluo_params.yaml"
CONFIG = CONFIG_FOLDER + "galvo_pi_config.yaml"
SYS_CONFIG = r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaFlash_orcaQuest.cfg"
# Alternative configuration file (commented out)
#SYS_CONFIG = r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaflash4.cfg"

# Default safety values in case of hardware malfunction

galvo1_val = 0
galvo2_val = 0
pi1_val = 11
pi2_val = 80
pi3_val = 14.35
pi4_val = 12

# List to store PI widgets (e.g., motor controllers)
pi_widgets = []


def load_yaml(path: str):
    """
    Load and parse a YAML file from the given path.

    Args:
        path (str): Path to the YAML file.

    Returns:
        dict: Parsed YAML content as a dictionary.
    """
    with open(path, "r") as file:
        return yaml.safe_load(file)


def save_yaml(dictionnaire, chemin):
    """
    Save a dictionary to a YAML file at the specified path.

    Args:
        dictionnaire (dict): The data to save.
        chemin (str): Path where the YAML file will be written.
    """
    with open(chemin, "w") as file:
        yaml.dump(dictionnaire, file, default_flow_style=False)


def save_params_for_all_widgets(pi_widgets):
    """
    Decorator that ensures all widgets save their parameters
    before executing the wrapped function.

    Args:
        pi_widgets (list): List of widget objects that may have a save_params method.

    Returns:
        Callable: Wrapped function with pre-execution save logic.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for widget in pi_widgets:
                if hasattr(widget, "save_params"):
                    widget.save_params()
            return func(*args, **kwargs)

        return wrapper

    return decorator
