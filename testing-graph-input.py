# Graph approach for inputting values to the console by hand

import sys  # For flushing output
import time
import random  # RNG
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Get current time
from datetime import datetime

# Smooth line
import numpy as np
from scipy.interpolate import interp1d


# Animation function
def animate(
    frame, data_list, start_time, Ox_labels, smooth=False, colors_list=[]
):  # Flag to check if smoothing is enabled
    # Adjust Step Size and overflow.
    step_size = 8
    overflow = 20

    # Automatically advance to the next frame for initialization formatting.
    if frame == 0:
        frame += 1
    else:
        # Start taking input or receiving data.
        flt = int(input())
        data_list.append(flt)
    data_list = data_list[-100:]
    # Limit to 100 elements to save memory space; usually, the graph does not actually contain that many.

    # Apply smoothing if there are 4 or more data points
    if len(data_list) >= 4 and smooth:
        x = np.arange(len(data_list))
        cubic_interpolation_model = interp1d(x, data_list, kind="cubic")
        x_smooth = np.linspace(0, len(data_list) - 1, 500)
        data_lst_smooth = cubic_interpolation_model(x_smooth)
    else:
        x_smooth = np.arange(len(data_list))
        data_lst_smooth = data_list

    plt.gcf().set_facecolor("black")  # Black window
    graph.set_facecolor("black")  # Black background

    # Clear the last frame and draw the next frame
    graph.clear()

    # Formatting for the graph
    graph.set_title("Line Graph Testing", fontsize=30, color="white")
    graph.set_ylabel("Simulated Heartrate", fontsize=15, color="white")
    graph.set_xlabel("Time", fontsize=15, color="white")

    # White x and y axis line, and spines.
    graph.tick_params(axis="x", colors="white")
    graph.tick_params(axis="y", colors="white")
    graph.spines["bottom"].set_color("white")  # X-axis line
    graph.spines["left"].set_color("white")  # Y-axis line

    # Calculate elapsed time for each data point using the system clock
    elapsed_time = datetime.now() - start_time
    elapsed_seconds = elapsed_time.total_seconds()
    elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed_seconds))

    # Append the "Time elapsed" value to x.
    # Note: This array can be modified for showing status, such as "pausing"
    # Simulated Pause
    if elapsed_seconds > 4 and elapsed_seconds < 10:
        Ox_labels.append("Paused")
        colors_list.append("blue")
    elif elapsed_seconds > 15 and elapsed_seconds < 20:
        Ox_labels.append("Failed")
        colors_list.append("purple")
    else:
        Ox_labels.append(elapsed_str)
        colors_list.append("red")

    # Limit to 100 elements to save memory space, usually the graph does not actually contain that many.
    colors_list = colors_list[-100:]
    Ox_labels = Ox_labels[-100:]

    # Plot the smooth line with colors from the colors_list array
    for i in range(len(x_smooth) - 1):
        x1, x2, y1, y2 = (
            x_smooth[i],
            x_smooth[i + 1],
            data_lst_smooth[i],
            data_lst_smooth[i + 1],
        )
        color = colors_list[int(x1)]
        graph.plot([x1, x2], [y1, y2], color=color, linewidth=2)

    # Plot the data points with colors from the colors_list array
    for i, (x, y) in enumerate(zip(range(len(data_list)), data_list)):
        color = colors_list[i]
        graph.plot(x, y, marker="o", markersize=8, color=color)

    # Show all values until the data points reach a certain threshold (to avoid too much text).
    if len(data_list) <= overflow:
        visible_indices = list(range(len(data_list)))
    else:
        step_size = max(step_size, 1)
        visible_indices = list(range(0, len(data_list), step_size)) + [
            len(data_list) - 1
        ]
        # (Including the last x-value)

    # Format the x-axis labels, with 45-degree rotation.
    graph.set_xticks(visible_indices)
    graph.set_xticklabels(
        [Ox_labels[i] for i in visible_indices], rotation=45, ha="right", fontsize=13
    )

    # Increase font size for label y.
    plt.tick_params(axis="y", labelsize=13)

    # Display the elapsed time annotation
    graph.annotate(
        f"Elapsed Time: {elapsed_str}",
        (0.85, 0.95),  # Coordinations
        xycoords="axes fraction",  # Fraction of axes from lower left
        ha="right",
        va="center",
        fontsize=15,
        color="white",
    )

    # DEBUGGING
    print("Number of points:", len(data_list))
    # print(data_list)
    # print(Ox_labels)
    # print(colors_list)


# Adjust default window size along with its DPI.
plt.rcParams["figure.figsize"] = [1366 / 100, 768 / 100]
plt.rcParams["figure.dpi"] = 75

# Create empty list to store data
colors_list = []
data_lst = []
x_labels_str = []

# Create figure and axes objects
fig, graph = plt.subplots()

# Set the start time using the system clock
start_time = datetime.now()

# Run the animation and show graph with smoothing enabled
ani = animation.FuncAnimation(
    fig,
    animate,
    fargs=(data_lst, start_time, x_labels_str, True, colors_list),
    frames=100,
    interval=100,
)
plt.show()
