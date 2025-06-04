from PiControlWidget import (
    PIControlWidget,
)
from GalvoWidget import (
    SlidesWidget,
)
from ScansWidget import (
    ScanBTNWidget,
)
from app_func.app_functions import *

import napari
from pymmcore_plus import (
    CMMCorePlus,
)

from pi_contol.PiController import PiController

if __name__ == "__main__":
    params = load_yaml(CONFIG)

    galvo1_val = float(params["galvo1_val"])
    galvo2_val = float(params["galvo2_val"])
    pi1_val = float(params["pi1_val"])
    pi2_val = float(params["pi2_val"])
    pi3_val = float(params["pi3_val"])
    pi4_val = float(params["pi4_val"])

    pi_vals = [
        pi1_val,
        pi2_val,
        pi3_val,
        pi4_val,
    ]

    pi_controller = PiController()

    core = CMMCorePlus()
    core.loadSystemConfiguration(SYS_CONFIG)

    app = napari.Viewer()

    for i in range(
        1,
        5,
    ):
        if i == 1:
            (
                mini,
                maxi,
            ) = (
                8,
                16.999,
            )
        elif i == 2:
            (
                mini,
                maxi,
            ) = (
                -360,
                360,
            )
        elif i == 3:
            (
                mini,
                maxi,
            ) = (
                4,
                16.999,
            )
        else:
            (
                mini,
                maxi,
            ) = (
                0.001,
                16.999,
            )

        pi_widget = PIControlWidget(
            pi_controller,
            pi_vals[i - 1],
            controller_id=i,
            mini=mini,
            maxi=maxi,
        )
        app.window.add_dock_widget(
            pi_widget,
            area="right",
        )
        pi_widgets.append(pi_widget)

    sl_widget = SlidesWidget(
        galvo1_val,
        galvo2_val,
    )
    app.window.add_dock_widget(
        sl_widget,
        area="bottom",
    )

    sc_widget = ScanBTNWidget(
        pi_controller,
        core,
    )
    app.window.add_dock_widget(
        sc_widget,
        area="left",
    )

    napari.run()
