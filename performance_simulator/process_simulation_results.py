import numpy as np
import matplotlib.pyplot as plt
from typing import List


def draw_time_cost(b1: List[int], b2: List[int], our: List[int]) -> None:
    print('Time cost')

    # Sort the data in ascending order
    b1 = np.sort(b1)/1000
    b2 = np.sort(b2)/1000
    our = np.sort(our)/1000

    # Create an array of indices from 1 to the length of the data
    b1_indices = np.arange(1, len(b1) + 1)
    b2_indices = np.arange(1, len(b2) + 1)
    our_indices = np.arange(1, len(our) + 1)

    # Divide each index by the total number of values to get the proportion
    b1_proportions = b1_indices / len(b1)
    b2_proportions = b2_indices / len(b2)
    our_proportions = our_indices / len(our)

    # plot the cumulative distribution function
    plt.plot(b1, b1_proportions, label='one batch baseline')
    plt.plot(b2, b2_proportions,  label='multiple batch baseline')
    plt.plot(our, our_proportions,  label='ours')

    plt.xlabel('Time spend (seconds)')
    plt.ylabel('CDF')
    plt.xlim(0)
    plt.legend()
    plt.show()


def draw_video_cost(b1: List[int], b2: List[int], our: List[int], opt: List[int]) -> None:
    print('Money cost')
    print(b1)
    print(b2)
    print(our)
    print(opt)

    # Sort the data in ascending order
    b1 = np.sort(b1)
    b2 = np.sort(b2)
    our = np.sort(our)
    opt = np.sort(opt)

    # Create an array of indices from 1 to the length of the data
    b1_indices = np.arange(1, len(b1) + 1)
    b2_indices = np.arange(1, len(b2) + 1)
    our_indices = np.arange(1, len(our) + 1)
    opt_indices = np.arange(1, len(opt) + 1)

    # Divide each index by the total number of values to get the proportion
    b1_proportions = b1_indices / len(b1)
    b2_proportions = b2_indices / len(b2)
    our_proportions = our_indices / len(our)
    opt_proportions = opt_indices / len(opt)

    # plot the cumulative distribution function
    plt.plot(b1, b1_proportions, label='one batch baseline')
    plt.plot(b2, b2_proportions,  label='multiple batch baseline')
    plt.plot(our, our_proportions,  label='ours')
    plt.plot(opt, opt_proportions,  label='optimal')

    plt.xlabel('Number of video sessions viewed')
    plt.ylabel('CDF')
    plt.xlim(0)
    plt.legend()
    plt.show()
