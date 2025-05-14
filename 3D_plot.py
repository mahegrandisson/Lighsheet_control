import os
import matplotlib.pyplot as plt
from pi_ni_scan import read_tiff_img


def from_folder_data(folder_path: str):
    x, y, z = [], [], []
    for img in os.listdir(folder_path):
        image_path = folder_path + "/" + img
        metadata, img_data = read_tiff_img(image_path)
        x.append(metadata.pixels.planes[0].position_x)
        y.append(metadata.pixels.planes[0].position_y)
        z.append(metadata.pixels.planes[0].position_z)
    return x, y, z


def plot_3d_points(x, y, z, title="3D Scatter Plot", color="blue", marker="o"):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(x, y, z, c=color, marker=marker)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)

    plt.show()


if __name__ == "__main__":
    x_data, y_data, z_data = from_folder_data("images/Brillouin_Tiff")
    plot_3d_points(x_data, y_data, z_data)
