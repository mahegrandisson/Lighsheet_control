from PiControlWidget import PIControlWidget
from SlidesWidget import SlidesWidget
from ScansWidget import ScansWidget
from app_functions import *





if __name__=="__main__":

    params = load_yaml(CONFIG)

    galvo1_val = float(params["galvo1_val"])
    galvo2_val = float(params["galvo2_val"])
    pi1_val = float(params["pi1_val"])
    pi2_val = float(params["pi2_val"])
    pi3_val = float(params["pi3_val"])
    pi4_val = float(params["pi4_val"])

    pi_vals = [pi1_val, pi2_val, pi3_val, pi4_val]

    pi_controller = PiController()

    core = CMMCorePlus()
    core.loadSystemConfiguration(SYS_CONFIG)

    app = napari.Viewer()

    for i in range(1, 5):
        if i==1:
            mini = 8
            maxi = 16.999
        elif i==2:
            mini = -360
            maxi = 360
        elif i==3:
            mini = 4
            maxi = 16.999
        else:
            mini = 0.001
            maxi = 16.999
        pi_widget = PIControlWidget(pi_controller,pi_vals[i-1], controller_id=i,mini=mini,maxi=maxi)
        app.window.add_dock_widget(pi_widget, area='right')
        pi_widgets.append(pi_widget)

    sl_widget = SlidesWidget(galvo1_val,galvo2_val)
    app.window.add_dock_widget(sl_widget, area='left')

    sc_widget = ScansWidget(pi_controller, core)
    app.window.add_dock_widget(sc_widget, area='left')

    napari.run()