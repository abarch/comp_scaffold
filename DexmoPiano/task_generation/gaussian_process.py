import random
from dataclasses import dataclass

import GPy
import GPyOpt
import numpy as np


# interval of possible bpm_values
import pandas
from GPyOpt.methods import BayesianOptimization
from pandas import DataFrame

from task_generation.practice_modes import PracticeMode
from task_generation.task_parameters import TaskParameters

BPM_BOUNDS = [50, 200]



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
    def __init__(self, bpm_norm_fac=100):
        self.data_X = None
        self.data_X_old_shape = None

        self.data_Y = None

        self.bpm_norm_fac = bpm_norm_fac

        self.domain = [
            {'name': 'practice_mode', 'type': 'categorical', 'domain': (0, 1, 2)},
            {'name': 'bpm', 'type': 'continuous', 'domain':
                (self._norm_bpm(BPM_BOUNDS[0]), self._norm_bpm(BPM_BOUNDS[1]))},
            {'name': 'error_pitch', 'type': 'continuous', 'domain': (0, 1)},
            {'name': 'error_timing', 'type': 'continuous', 'domain': (0, 1)}
        ]

        self.space = GPyOpt.core.task.space.Design_space(self.domain)

    def _norm_bpm(self, v: float) -> float:
        return v / self.bpm_norm_fac

    def _params2domain(self, error: DataFrame, task_parameters: TaskParameters, practice_mode: PracticeMode):
        domain_x = [
            practice_mode.value,
            self._norm_bpm(task_parameters.bpm),
            error.pitch_right + error.pitch_left,
            error.timing_right + error.timing_left
        ]

        return np.array([domain_x])

    def _domain2space(self, domain_x):
        # Converts the domain variables into the GPs input space
        # does one-hot encoding
        space_rep = self.space.unzip_inputs(domain_x)
        return space_rep

    def _get_bayes_opt(self) -> BayesianOptimization:
        return self.bayes_opt

    def update_model(self):
        """
            If the Gaussian Process' training data has changed, "trains" the GP on the complete data set.
        """
        # only calculate new model if data changed
        if self.data_X is None or self.data_X.shape == self.data_X_old_shape:
            return

        self.data_X_old_shape = self.data_X.shape

        kernel = GPy.kern.RBF(input_dim=self.space.model_dimensionality,
                              variance=0.01,
                              lengthscale=1)
        self.bayes_opt = GPyOpt.methods.BayesianOptimization(
            f=None, domain=self.domain, X=self.data_X, Y=self.data_Y,
            maximize=True, normalize_Y=False,
            kernel=kernel,
        )

        self.bayes_opt.model.max_iters = 0
        self.bayes_opt._update_model()
        self.bayes_opt.model.max_iters = 1000
        self.bayes_opt._update_model()

    def get_estimate(self, error: DataFrame, task_parameters: TaskParameters, practice_mode: PracticeMode) -> float:
        """
            Estimates the utility value for a given practice mode
        @param error: namedtuple("Error", "pitch timing")
        @param task_parameters: task_parameters of the music piece
        @param practice_mode: the practice mode for which the utility value should be estimated
        @return: gaussian process' estimate of the utility value
        """
        if not hasattr(self, "bayes_opt"):
            # if there is no model yet, e.g. in the first iteration
            # print("(GP) DATA_X IS NONE, RETURNING RANDOM NUMBER")
            return random.random()

        bayes_opt = self._get_bayes_opt()

        x = self._params2domain(error, task_parameters, practice_mode)
        x = self._domain2space(x)

        mean, var = bayes_opt.model.predict(x)

        return mean[0]

    def get_best_practice_mode(self, error: DataFrame, task_parameters: TaskParameters, epsilon=0.05):
        """
            computes the gaussian process' estimate of the best practice mode
            for exploration: currently utilizes epsilon-greedy exploration
        @param error: dataframe with the error values
        @param task_parameters: task_parameters of the music piece
        @param (optional) epsilon: the probability of making a random decision. set to 0 for no exploration.
        @return: chosen for given input parameters PracticeMode
        """
        all_practice_modes = list(PracticeMode)
        # epsilon-greedy
        if random.random() > epsilon:
            max_i = np.argmax([self.get_estimate(error, task_parameters, pm)
                               for pm in all_practice_modes])
            return all_practice_modes[max_i]
        else:
            return np.random.choice(all_practice_modes)

    def add_data_point(self, error: DataFrame, task_parameters: TaskParameters, practice_mode: PracticeMode, utility_measurement: float):
        """
            Adds a new datapoint to the dataset of the gaussian process.
            Does not update the Gaussian Process for the new training data (see: update_model)
        @param error: dataframe with the error values
        @param task_parameters: task_parameters of the music piece
        @param practice_mode: practice mode in which the performer practiced
        @param utility_measurement: observed utility value for the given parameters
        """
        new_x = self._params2domain(error, task_parameters, practice_mode)
        new_y = [utility_measurement]

        if self.data_X is None:
            self.data_X = new_x
            self.data_Y = [new_y]
        else:
            self.data_X = np.vstack((self.data_X, new_x[0]))
            self.data_Y = np.vstack((self.data_Y, new_y[0]))