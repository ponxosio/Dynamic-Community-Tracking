import numpy as np

error_color = np.array([204, 0, 204])/255

distribution_colors_5 = [
    np.array([247, 247, 247])/255,
    np.array([204, 204, 204])/255,
    np.array([150, 150, 150])/255,
    np.array([99, 99, 99])/255,
    np.array([37, 37, 37])/255
]

distribution_colors_10 = [
    np.array([0, 104, 55])/255,
    np.array([26, 152, 80])/255,
    np.array([102, 189, 99])/255,
    np.array([166, 217, 106])/255,
    np.array([217, 239, 139])/255,
    np.array([254, 224, 139])/255,
    np.array([253, 174, 97])/255,
    np.array([244, 109, 67])/255,
    np.array([215, 48, 39])/255,
    np.array([165, 0, 38])/255
]


def select_color_5(value):
    c_color = error_color
    
    if 0 < value < 0.2:
        c_color = distribution_colors_5[0]
    elif 0.2 <= value < 0.4:
        c_color = distribution_colors_5[1]
    elif 0.4 <= value < 0.6:
        c_color = distribution_colors_5[2]
    elif 0.6 <= value < 0.8:
        c_color = distribution_colors_5[3]
    elif 0.8 <= value < 1.0:
        c_color = distribution_colors_5[4]
    return c_color


def select_color_10(value):
    c_color = error_color

    if 0 < value < 0.1:
        c_color = distribution_colors_10[0]
    elif 0.1 <= value < 0.2:
        c_color = distribution_colors_10[1]
    elif 0.2 <= value < 0.3:
        c_color = distribution_colors_10[2]
    elif 0.3 <= value < 0.4:
        c_color = distribution_colors_10[3]
    elif 0.4 <= value < 0.5:
        c_color = distribution_colors_10[4]
    elif 0.5 <= value < 0.6:
        c_color = distribution_colors_10[5]
    elif 0.6 <= value < 0.7:
        c_color = distribution_colors_10[6]
    elif 0.7 <= value < 0.8:
        c_color = distribution_colors_10[7]
    elif 0.8 <= value < 0.9:
        c_color = distribution_colors_10[8]
    elif 0.9 <= value < 1.0:
        c_color = distribution_colors_10[9]
    
    return c_color


def print_legend_5(axs):
    xs = [0]*5
    ys = range(5)

    increment = 0.2
    labels = ["{0: .1f} <= x < {1: .1f}".format(increment*i, increment*(i+1)) for i in range(1, 5)]
    labels.insert(0, "0 < x < 0.1")

    axs.scatter(xs, ys, c=distribution_colors_5, edgecolors='#252525', marker='s')
    for i, txt in enumerate(labels):
        axs.annotate(txt, (xs[i], ys[i]))


def print_legend_10(axs):
    xs = [0]*10
    ys = range(10)

    increment = 0.1
    labels = ["{0: .1f} <= x < {1: .1f}".format(increment*i, increment*(i+1)) for i in range(1, 10)]
    labels.insert(0, "0 < x < 0.1")

    axs.scatter(xs, ys, c=distribution_colors_10, edgecolors='#252525', marker='s')
    for i, txt in enumerate(labels):
        axs.annotate(txt, (xs[i], ys[i]+0.15))

    axs.axis('off')
