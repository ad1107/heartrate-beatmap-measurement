# A sample graph that simulate random heartrate with time elapsed.
# Waiting for variables coming from Hyperate and Gosumemory.

import time
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime


# animation function
def animate(i, data_lst, start_time):
    # Adjust Step Size
    step_size = 5

    # Value Range
    start = 85
    end = 130
    flt = random.uniform(start, end)
    data_lst.append(flt)
    data_lst = data_lst[-100:]

    plt.gcf().set_facecolor("black")  # Black window
    graph.set_facecolor("black")  # Black background

    # Clear the last frame and draw the next frame
    graph.clear()
    graph.plot(data_lst, marker=".", linestyle="-", color="red")  # Use dots as markers

    # Formating
    graph.set_title("Line Graph Testing", fontsize=30, color="white")
    graph.set_ylabel(
        f"Simulated Heartrate from {start} - {end}", fontsize=15, color="white"
    )
    graph.set_xlabel("Time (mm:ss)", fontsize=15, color="white")

    # White x and y axis line, and spines.
    graph.tick_params(axis="x", colors="white")
    graph.tick_params(axis="y", colors="white")
    graph.spines["bottom"].set_color("white")  # X-axis line
    graph.spines["left"].set_color("white")  # Y-axis line

    # Calculate elapsed time using the system clock
    elapsed_time = datetime.now() - start_time
    elapsed_seconds = elapsed_time.total_seconds()
    elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed_seconds))

    # Set the x-axis labels with a specified step size
    x_labels_str = [elapsed_str] * len(data_lst)
    step_size = step_size if step_size > 0 else 1
    visible_indices = list(range(0, len(data_lst), step_size))
    graph.set_xticks(visible_indices)
    graph.set_xticklabels(
        [x_labels_str[i] for i in visible_indices], rotation=45, ha="right"
    )

    graph.annotate(
        f"Elapsed Time: {elapsed_str}",
        (0.85, 0.95),
        xycoords="axes fraction",
        ha="right",
        va="center",
        fontsize=15,
        color="white",
    )


# Adjust default window size along with its DPI.
plt.rcParams["figure.figsize"] = [1366 / 100, 768 / 100]
plt.rcParams["figure.dpi"] = 75

# Create empty list to store data
# Create figure and axes objects
data_lst = []
fig, graph = plt.subplots()

# Set the start time using the system clock
start_time = datetime.now()

# Run the animation and show graph
ani = animation.FuncAnimation(
    fig, animate, fargs=(data_lst, start_time), frames=100, interval=200
)
plt.show()
