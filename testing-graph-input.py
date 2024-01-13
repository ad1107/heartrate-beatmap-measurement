# Graph approach for inputting values to the console by hand
# Credit: 0x2ee08

import sys  # To allow flushing output.
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime


# animation function
def animate(frame, data_lst, start_time, x_labels_str):
    # Adjust Step Size and overflow.
    step_size = 5
    overflow = 20

    # Automatically advance to the next frame, for initialize formatting.
    if frame == 0:
        frame += 1
    else:
        # Start taking input or receiving data.
        flt = int(input())
        data_lst.append(flt)
    data_lst = data_lst[-100:]
    # Limit to 100 elements to save memory space, usually the graph does not actually contain that many.

    plt.gcf().set_facecolor("black")  # Black window
    graph.set_facecolor("black")  # Black background

    # Clear the last frame and draw the next frame
    graph.clear()
    graph.plot(
        data_lst, marker=".", linestyle="-", markersize=17, color="red"
    )  # Use dots as markers, dash for line

    # Formatting labels
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
    x_labels_str.append(elapsed_str)
    x_labels_str = x_labels_str[-100:]

    # Show all values until the data points reach values (to avoid too much texts).
    if len(data_lst) <= overflow:
        visible_indices = list(range(len(data_lst)))
    else:
        step_size = max(step_size, 1)
        visible_indices = list(range(0, len(data_lst), step_size)) + [len(data_lst) - 1]
        # (Including the last x-value)

    # Format the x-axis labels.
    graph.set_xticks(visible_indices)
    graph.set_xticklabels(
        [x_labels_str[i] for i in visible_indices], rotation=45, ha="right", fontsize=13
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
    sys.stdout.write("\rNumber of points: " + str(len(data_lst)) + "\n")
    sys.stdout.flush()


# Adjust default window size along with its DPI.
plt.rcParams["figure.figsize"] = [1366 / 100, 768 / 100]
plt.rcParams["figure.dpi"] = 75

# Create empty list to store data
data_lst = []
x_labels_str = []

# Create figure and axes objects
fig, graph = plt.subplots()

# Set the start time using the system clock
start_time = datetime.now()

# Run the animation and show graph
ani = animation.FuncAnimation(
    fig, animate, fargs=(data_lst, start_time, x_labels_str), frames=100, interval=500
)
plt.show()
