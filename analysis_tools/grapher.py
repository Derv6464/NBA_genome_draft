import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

class Grapher:
    def __init__(self):
        pass

    def graph_hist_bar(self, x_data: list[float], y_data: dict, category: list[int], cat_label: str, y_label: str, title: str):
        bar_width = 0.8 / len(x_data)
        x = np.arange(len(category))

        plt.figure()

        for i, team_name in enumerate(x_data):
            scores = y_data[team_name]
            plt.bar(x + i * bar_width, scores, width=bar_width, label=team_name)

        plt.xlabel(cat_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(x + bar_width * (len(x_data) - 1) / 2, category)
        plt.legend()
        file_path = os.path.join("data/images/", f"{title}-{datetime.now().strftime("%d_%m_%Y-%H:%M:%S")}.png")
        plt.savefig(file_path, bbox_inches='tight')

    def graph_line(self, x_data: list[float], y_data : list[tuple[str, float]], x_label: str, y_label: str, title: str):
        plt.figure()
        for label, data  in y_data:
            plt.plot(x_data, data, label=label)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.legend()
        file_path = os.path.join("data/images/", f"{title}-{datetime.now().strftime("%d_%m_%Y-%H:%M:%S")}.png")
        plt.savefig(file_path, bbox_inches='tight')
