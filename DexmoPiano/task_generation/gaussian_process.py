#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum

import matplotlib.pyplot as plt
import numpy as np
import random
import GPyOpt
from GPyOpt.methods import BayesianOptimization
from task_generation.task_parameters import TaskParameters
from dataclasses import dataclass
from collections import defaultdict


class PracticeMode(enum.Enum):
    IMP_PITCH = enum.auto()
    IMP_TIMING = enum.auto()


class NoteRangePerHand(enum.Enum):
    EASY = enum.auto()
    MEDIUM = enum.auto()
    HARD = enum.auto()


practicemode_to_int = {pm: i for i, pm in enumerate(PracticeMode)}
int_to_practicemode = {i: pm for i, pm in enumerate(PracticeMode)}


@dataclass
class GPPlotData:
    X1: np.array = None
    X2: np.array = None
    mean: np.array = None
    mean_max: float = None
    mean_min: float = None
    std: np.array = None
    std_max: float = None
    std_min: float = None
    acq: np.array = None
    acq_max: float = None
    acq_min: float = None

    def apply_to_arrays(self, func):
        return [
            func(self.mean),
            func(self.std),
            func(self.acq),
        ]


def hands_to_int(left, right):
    r = -1
    if left:
        r += 2
    if right:
        r += 1
    return r


def round_to_closest(f, vals):
    diff = [(abs(f - v), v) for v in vals]
    diff = sorted(diff)
    return diff[0][1]


def enforce_categorical(np_array):
    np_array[:, 1] = np.floor(np_array[:, 1])
    np_array[:, 2] = np.floor(np_array[:, 2])

    return np_array.astype(int)


class GaussianProcess:
    domain = [{'name': 'complexity_level', 'type': 'discrete', 'domain': tuple(range(10))},
              {'name': 'practice_mode', 'type': 'categorical', 'domain': (0, 1, 2, 3)},
              {'name': 'hands', 'type': 'categorical', 'domain': (0, 1, 2)},
              {'name': 'bpm', 'type': 'discrete', 'domain': range(50, 201)},
              ]

    # only subset of task_parameters for easier testing for now
    space = GPyOpt.core.task.space.Design_space(domain)

    def __init__(self):
        self.data_X = None
        self.data_Y = None

    def _params_to_domain(self, complexity_level: int, task_parameters: TaskParameters, practice_mode: PracticeMode):
        # TODO normalize these here??
        domain_x = [complexity_level,
                    practicemode_to_int[practice_mode],
                    hands_to_int(task_parameters.left, task_parameters.right),
                    int(task_parameters.bpm),
                    ]

        return np.array([domain_x])

    def _domain_to_space(self, domain_x):
        space_rep = self.space.unzip_inputs(domain_x)
        return space_rep

    def _get_bayes_opt(self) -> BayesianOptimization:
        bayes_opt = BayesianOptimization(
            f=None, domain=self.domain, X=self.data_X, Y=self.data_Y,
            maximize=True,
        )
        bayes_opt._update_model()

        return bayes_opt

    def get_estimate(self, complexity_level: int, task_parameters: TaskParameters,
                     practice_mode: PracticeMode) -> float:
        if self.data_X is None:
            print("(gp) DATA_X IS NONE, RETURNING RANDOM NUMBER")
            return random.random()

        bayes_opt = self._get_bayes_opt()

        X = self._params_to_domain(complexity_level, task_parameters, practice_mode)
        X = self._domain_to_space(X)

        mean, var = bayes_opt.model.predict(X)
        print("EST RES:", mean[0], var[0])
        return mean[0]

    def get_best_practice_mode(self, complexity_level: int,
                               task_parameters: TaskParameters) -> PracticeMode:
        all_practice_modes = list(PracticeMode)
        return all_practice_modes[
            np.argmax([self.get_estimate(complexity_level, task_parameters, pm)
                       for pm in all_practice_modes])]

    def add_data_point(self, complexity_level: int, task_parameters: TaskParameters,
                       practice_mode: PracticeMode,
                       utility_measurement: float):
        new_x = self._params_to_domain(complexity_level, task_parameters, practice_mode)
        new_y = [utility_measurement]

        if self.data_X is None:
            self.data_X = new_x
            self.data_Y = new_y
        else:
            self.data_X = np.vstack((self.data_X, new_x[0]))
            self.data_Y = np.vstack((self.data_Y, new_y[0]))

    def _get_plot_data(self, data_dict, c, practice_mode, bayes_opt):
        bounds = [[0, 3], [50, 200]]

        acquisition_function = bayes_opt.acquisition.acquisition_function
        model = bayes_opt.model

        X1 = np.linspace(bounds[0][0], bounds[0][1], 200, endpoint=False)
        X2 = np.linspace(bounds[1][0], bounds[1][1], 200)
        x1, x2 = np.meshgrid(X1, X2)
        X = np.hstack((

            np.array([c] * (200 * 200)).reshape(200 * 200, 1),
            np.array([practicemode_to_int[practice_mode]] * (200 * 200)).reshape(200 * 200, 1),
            x1.reshape(200 * 200, 1),
            x2.reshape(200 * 200, 1)))

        X = enforce_categorical(X)
        X_spaced = self._domain_to_space(X)

        acqu = acquisition_function(X_spaced)
        acqu_normalized = acqu  # (-acqu - min(-acqu))/(max(-acqu - min(-acqu)))

        m, v = model.predict(X_spaced)

        data_dict[practice_mode].mean = m
        data_dict[practice_mode].std = np.sqrt(v)
        data_dict[practice_mode].acq = acqu_normalized
        data_dict[practice_mode].X1 = X1
        data_dict[practice_mode].X2 = X2

    def _plot_single_practice_mode(self, gp_plot_data: GPPlotData, subplotf):
        label_x = "Hands"
        label_y = "BPM"

        bounds = [[0, 3], [50, 200]]

        X1 = gp_plot_data.X1
        X2 = gp_plot_data.X2

        acqu_normalized = gp_plot_data.acq.reshape((200, 200))

        subplotf(1)
        plt.contourf(X1, X2, gp_plot_data.mean.reshape(200, 200), 100,
                     vmin=gp_plot_data.mean_min,
                     vmax=gp_plot_data.mean_max, )
        plt.colorbar()

        plt.ylabel(label_y)
        plt.title('Posterior mean')
        plt.axis((bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]))
        subplotf(2)
        plt.contourf(X1, X2, gp_plot_data.std.reshape(200, 200), 100,
                     vmin=gp_plot_data.std_min,
                     vmax=gp_plot_data.std_max)
        plt.colorbar()
        plt.xlabel(label_x)
        plt.ylabel(label_y)
        plt.title('Posterior sd.')
        plt.axis((bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]))
        subplotf(3)
        plt.contourf(X1, X2, acqu_normalized, 100,
                     vmin=gp_plot_data.acq_min,
                     vmax=gp_plot_data.acq_max, )
        plt.colorbar()
        plt.xlabel(label_x)
        plt.ylabel(label_y)
        plt.title('Acquisition function')
        plt.axis((bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1]))

    def plot_single(self, c, practice_mode: PracticeMode):
        bayes_opt = self._get_bayes_opt()

        plt.figure(figsize=(10, 5))
        subplotf = lambda idx: plt.subplot(1, 3, idx)

        self._plot_single_practice_mode(c, practice_mode, bayes_opt, subplotf)
        plt.show()

    def plot_mutiple(self, c, practice_modes: [PracticeMode]):
        bayes_opt = self._get_bayes_opt()

        n_rows = len(practice_modes)

        data_dict = defaultdict(GPPlotData)
        for i, practice_mode in enumerate(practice_modes):
            self._get_plot_data(data_dict, c, practice_mode, bayes_opt)

        mean_max, std_max, acq_max = np.max([d.apply_to_arrays(np.max) for d in
                                             data_dict.values()], axis=0)

        mean_min, std_min, acq_min = np.min([d.apply_to_arrays(np.min) for d in
                                             data_dict.values()], axis=0)

        for pd in data_dict.values():
            pd.mean_max = mean_max
            pd.mean_min = mean_min
            pd.std_max = std_max
            pd.std_min = std_min
            pd.acq_max = acq_max
            pd.acq_min = acq_min

        fig = plt.figure(figsize=(10, 5 * n_rows))

        for i, practice_mode in enumerate(practice_modes):
            subplotf = lambda idx: plt.subplot(n_rows, 3, i * 3 + idx)
            self._plot_single_practice_mode(data_dict[practice_mode], subplotf)

            ax = subplotf(1)
            row = practice_mode.name
            pad = 5
            ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                        xycoords=ax.yaxis.label, textcoords='offset points',
                        size='large', ha='right', va='center')

        fig.tight_layout()

        plt.show()

        some_pd = list(data_dict.values())[0]

        argmax_plot_data = GPPlotData(X1=some_pd.X1, X2=some_pd.X2)
        argmax_plot_data.mean = np.argmax([d.mean for d in
                                           data_dict.values()], axis=0)

        argmax_plot_data.std = np.argmax([d.std for d in
                                          data_dict.values()], axis=0)

        argmax_plot_data.acq = np.argmax([d.acq for d in
                                          data_dict.values()], axis=0)

        plt.figure(figsize=(10, 5))
        subplotf = lambda idx: plt.subplot(1, 3, idx)

        self._plot_single_practice_mode(argmax_plot_data, subplotf)
        ax = subplotf(1)
        row = "ARGMAX"
        pad = 5
        ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')
        plt.show()


if __name__ == "__main__":
    STARTING_COMPLEXITY_LEVEL = 0
    c = STARTING_COMPLEXITY_LEVEL
    GP = GaussianProcess()

    tp = TaskParameters()
    print(GP.get_best_practice_mode(c, tp))

    for i in range(8):
        print("ADD DATA")
        tp.bpm = 60 + i * 10
        GP.add_data_point(c, tp,
                          PracticeMode.IDENTITY,
                          10 - i)

    print(GP.get_best_practice_mode(c, tp))

    GP.plot_mutiple(c, [
        PracticeMode.IDENTITY,
        PracticeMode.SLOWER
    ])
