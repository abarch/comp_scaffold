#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
from collections import namedtuple

Error = namedtuple("Error", "pitch timing")

BPM_BOUNDS = [50,200]

# def _norm_bpm(v):
#     return v/50

# BPM_BOUNDS = [90,160]

#### SIMPLIFIED ENUMS
import enum
class PracticeMode(enum.Enum):
    IMP_PITCH = enum.auto()
    IMP_TIMING = enum.auto()
    
class NoteRangePerHand(enum.Enum):
    EASY = 0.5
    MEDIUM = 1.5
    HARD = 3.0
    

import dataclasses as dc
from dataclasses import dataclass, astuple    
@dataclass
class TaskParameters:
    """
    We need to redefine this to use the new, simplified NoteRangePerHand.
    """
    timeSignature: tuple    = (4,4)
    noteValues: list        = dc.field(default_factory= lambda: [1, 1 / 2, 1 / 4, 1 / 8] )
    maxNotesPerBar: int       = 3
    noOfBars: int           = 7
    note_range: NoteRangePerHand = NoteRangePerHand.MEDIUM
    left: bool              = False
    right: bool             = True
    bpm: float              = 120
    
    def astuple(self):
        return astuple(self)
    

practicemode2int = {pm: i for i, pm in enumerate(PracticeMode)}
int2practicemode = {i: pm for i, pm in enumerate(PracticeMode)}
    
noterange2int = {pm: i for i, pm in enumerate(NoteRangePerHand)}
int2noterange = {i: pm for i, pm in enumerate(NoteRangePerHand)}


import matplotlib.pyplot as plt
import numpy as np
import random
import GPyOpt
import GPy

from dataclasses import dataclass
from collections import defaultdict


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

def round_to_closest(f, vals):
    diff = [(abs(f-v), v) for v in vals]
    diff = sorted(diff)
    return diff[0][1]

def enforce_categoricals(np_array):
    np_array[:,1] = np.floor(np_array[:,1])
    np_array[:,2] = np.floor(np_array[:,2])
    
    return np_array#.astype(int)

class GaussianProcess:
    def __init__(self, bpm_norm_fac=10):
        self.data_X = None
        self.data_X_hash = hash(str(None))
        
        self.data_Y = None
        
        self.bpm_norm_fac = bpm_norm_fac
        
        self.domain =[
            {'name': 'complexity_level', 'type': 'discrete', 'domain': tuple(range(10))},
            {'name': 'practice_mode', 'type': 'categorical', 'domain': (0,1,2,3)},
            # {'name': 'hands', 'type': 'categorical', 'domain': (0,1,2)},
            {'name': 'note_range', 'type': 'categorical', 'domain': (0,1,2)},
            {'name': 'bpm', 'type': 'continuous', 'domain': 
                 (self._norm_bpm(BPM_BOUNDS[0]),self._norm_bpm(BPM_BOUNDS[1]))},
                 
                ]
                 # only subset of task_parameters for easier testing for now
        self.space = GPyOpt.core.task.space.Design_space(self.domain)
        
    def _norm_bpm(self, v):
        return v/self.bpm_norm_fac
        
    def _params2domain(self, complexity_level, task_parameters, practice_mode):
        #TODO normalize these here??
        domain_x = [complexity_level,
                    practicemode2int[practice_mode],
                    noterange2int[task_parameters.note_range],
                    self._norm_bpm(task_parameters.bpm),
                    ]
        
        
        return np.array([domain_x])
        
    def _domain2space(self, domain_x):
        # domain_x = np.array([domain_x])
        # print(domain_x.shape)
        space_rep = self.space.unzip_inputs(domain_x)
        # print("DX", domain_x, domain_x.shape)
        # print("SX", space_rep)
        return space_rep
    
        
    def _get_bayes_opt(self):
        return self.bayes_opt
        
    
    def update_model(self):
        ## only calculate new model if data changed
        ## not sure why its so complicated with global and everything..
        if hash(str(self.data_X)) == self.data_X_hash:
            return
            # return self.bayes_opt
        
        self.data_X_hash = hash(str(self.data_X))
        # print("X", self.data_X)
        # print("Y", self.data_Y)
        
        
        # kernel = GPy.kern.RBF(input_dim=1, 
        #                       variance=1, 
        #                       lengthscale=1)
        
        # _pre = time.time()
        
        self.bayes_opt = GPyOpt.methods.BayesianOptimization(
            f = None, domain = self.domain, X = self.data_X, Y = self.data_Y,
            maximize=True,
            # model_type="GP",
            # model_type= 'GP_MCMC',
            # acquisition_type='EI_MCMC',
            # kernel=kernel,
            # normalize_Y=False,
                                                  # kernel=kernel,
        )
        self.bayes_opt._update_model() #.suggest_next_locations())
        
        ## somehow needed, otherwise the model is None
        
        # print("Constructing model took {:.2f}s".format(
        #     time.time()-_pre))
        # return self.bayes_opt
        
    
    def get_estimate(self, complexity_level, task_parameters, practice_mode,
                     add_variance=True):
        if not hasattr(self, "bayes_opt"):
            # print("(GP) DATA_X IS NONE, RETURNING RANDOM NUMBER")
            return random.random()
        
        # print(self.data_X, self.data_Y)
        # print(self.data_X.shape, self.data_Y.shape)
        
        # _pre = time.time()
        bayes_opt = self._get_bayes_opt()
        # print("Constructing model took {:.2f}s".format(
        #     time.time()-_pre))
        
        
        X = self._params2domain(complexity_level, task_parameters, practice_mode)
        X = self._domain2space(X)
        
        # print(bayes_opt.X, bayes_opt.X.shape)
        
        # print(bayes_opt.model.predict)
        
        # print("XX", X)
        
        mean, var = bayes_opt.model.predict(X)
        
        r = mean[0]
        if add_variance:
            r += np.sqrt(var[0])
        # print("EST RES:", mean[0], var[0])
        return r
        
        
    def get_best_practice_mode(self, complexity_level, task_parameters):
        all_practice_modes = list(PracticeMode)
        return all_practice_modes[np.argmax([self.get_estimate(complexity_level, task_parameters, pm)
                                             for pm in all_practice_modes])]
    
    def add_data_point(self, complexity_level, task_parameters, practice_mode, 
                       utility_measurement):
        new_x =  self._params2domain(complexity_level, task_parameters, practice_mode) 
        new_y = [ utility_measurement ]
        
        if self.data_X is None:
            self.data_X = new_x
            self.data_Y = [new_y]
        else:
            # print(self.data_X, new_x)
            self.data_X = np.vstack((self.data_X, new_x[0]))
            self.data_Y = np.vstack((self.data_Y, new_y[0]))
    
    
    def _get_plot_data(self, data_dict, c, practice_mode, bayes_opt):
        bounds = [[0,3], (self._norm_bpm(BPM_BOUNDS[0]),self._norm_bpm(BPM_BOUNDS[1]))]
        
        acquisition_function = bayes_opt.acquisition.acquisition_function
        model = bayes_opt.model
        
        
        X1 = np.linspace(bounds[0][0], bounds[0][1], 200, endpoint=False)
        # X1 = np.array([0,1,2])
        X2 = np.linspace(bounds[1][0], bounds[1][1], 200)
        x1, x2 = np.meshgrid(X1, X2)
        X = np.hstack((
            
            np.array([c]*(200*200)).reshape(200*200,1),
            np.array([practicemode2int[practice_mode]]*(200*200)).reshape(200*200,1),
            x1.reshape(200*200,1),
             x2.reshape(200*200,1)))
        
        X = enforce_categoricals(X)
        X_spaced = self._domain2space(X)
        # print(X[:100,:])
        
        acqu = acquisition_function(X_spaced)
        # acqu = acqu #(-acqu - min(-acqu))/(max(-acqu - min(-acqu)))
        
        m, v = model.predict(X_spaced)
        
        if type(m) == list:
            m = m[0]
        
        if type(v) == list:
            v = v[0]
        
        if type(acqu) == list:
            acqu = acqu[0]
        
        
        
        data_dict[practice_mode].mean = m
        data_dict[practice_mode].std = np.sqrt(v)
        data_dict[practice_mode].acq = acqu
        data_dict[practice_mode].X1 = X1
        data_dict[practice_mode].X2 = X2
        
    
    def _plot_single_practice_mode(self, gp_plot_data, subplotf):
        label_x = "NoteRange"
        label_y = "BPM"
        
        # Xdata = bayes_opt.X
        bounds = [[0,3], (self._norm_bpm(BPM_BOUNDS[0]),self._norm_bpm(BPM_BOUNDS[1]))]
        # color_by_step = True
        
        ## Derived from GPyOpt/plotting/plots_bo.py
        # n = Xdata.shape[0]
        # colors = np.linspace(0, 1, n)
        # cmap = plt.cm.Reds
        # norm = plt.Normalize(vmin=0, vmax=1)
        # points_var_color = lambda X: plt.scatter(
        #     X[:,0], X[:,1], c=colors, label=u'Observations', cmap=cmap, norm=norm)
        # points_one_color = lambda X: plt.plot(
        #     X[:,0], X[:,1], 'r.', markersize=10, label=u'Observations')
        
        X1 = gp_plot_data.X1
        X2 = gp_plot_data.X2
        
        acqu_normalized = gp_plot_data.acq.reshape((200,200))
        # acqu_normalized *= -1
        # acqu_normalized += 1
        
        
        # print(X[:100,:])
        # m, v = model.predict(X_spaced)
        
        # plt.subplot(1, 3, 1)
        subplotf(1)
        plt.contourf(X1, X2, gp_plot_data.mean.reshape(200,200),100,
                     vmin=gp_plot_data.mean_min,
                     vmax=gp_plot_data.mean_max,)
        plt.colorbar()
        # if color_by_step:
        #     points_var_color(Xdata)
        # else:
        #     points_one_color(Xdata)
        plt.xlabel(label_x)
        plt.ylabel(label_y)
        plt.title('Posterior mean')
        plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
        ##
        # plt.subplot(1, 3, 2)
        subplotf(2)
        plt.contourf(X1, X2, gp_plot_data.std.reshape(200,200),100,
                     vmin=gp_plot_data.std_min,
                     vmax=gp_plot_data.std_max)
        plt.colorbar()
        # if color_by_step:
        #     points_var_color(Xdata)
        # else:
        #     points_one_color(Xdata)
        plt.xlabel(label_x)
        plt.ylabel(label_y)
        plt.title('Posterior sd.')
        plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
        ##
        # plt.subplot(1, 3, 3)
        
        
        
        subplotf(3)
        plt.contourf(X1, X2, acqu_normalized,100,
                     vmin=gp_plot_data.acq_min,
                     vmax=gp_plot_data.acq_max,)
        plt.colorbar()
        # plt.plot(suggested_sample[:,0],suggested_sample[:,1],'m.', markersize=10)
        plt.xlabel(label_x)
        plt.ylabel(label_y)
        plt.title('Acquisition function')
        plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
        # if filename!=None:
        #     savefig(filename)
        # else:
        
    
    def get_policy(self, c):
        if not hasattr(self, "bayes_opt"):
            return np.round(np.random.random((200*200,1)))
        
        bayes_opt = self._get_bayes_opt()
        
        data_dict = defaultdict(GPPlotData)
        for i, practice_mode in enumerate([PracticeMode.IMP_TIMING,
                                           PracticeMode.IMP_PITCH]):
            plot_data = self._get_plot_data(data_dict, c, practice_mode, bayes_opt)
            # print("got data")
            
        return np.argmax([d.mean for d in [
            data_dict[PracticeMode.IMP_TIMING], data_dict[PracticeMode.IMP_PITCH]]], axis=0)
        
            
    
    def plot_single(self, c, practice_mode):
        bayes_opt = self._get_bayes_opt()
        
        plt.figure(figsize=(10,5))
        subplotf = lambda idx: plt.subplot(1,3,idx)
        
        self._plot_single_practice_mode(c, practice_mode, bayes_opt, subplotf)
        plt.show()
        
    def plot_mutiple(self, c, practice_modes):
        bayes_opt = self._get_bayes_opt()
        
        n_rows = len(practice_modes)
        # n_plots = n_rows*3
        
        data_dict = defaultdict(GPPlotData)
        for i, practice_mode in enumerate(practice_modes):
            self._get_plot_data(data_dict, c, practice_mode, bayes_opt)
            
        # print([d.apply_to_arrays(np.max) for d in 
        #                                      data_dict.values()])
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
        
        fig = plt.figure(figsize=(10,5*n_rows))
        
        for i, practice_mode in enumerate(practice_modes):
            
        # for i, practice_mode in enumerate(practice_modes):
            subplotf = lambda idx: plt.subplot(n_rows,3,i*3+idx)
            self._plot_single_practice_mode(data_dict[practice_mode], subplotf)
            
            ax = subplotf(1)
            row = practice_mode.name
            pad = 5
            ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                        xycoords=ax.yaxis.label, textcoords='offset points',
                        size='large', ha='right', va='center')
        
        
        
        
        
        # print(argmax_plot_data.mean.shape)
        
        
        # axes = fig.get_axes()
        # print(axes)
        # pad = 5
        # rows = ["HAHA"] * n_rows
        # for ax, row in zip(axes[:,0], rows):
            
        
        fig.tight_layout()
        # plt.savefig("detailed_noise01.png")
        plt.show()
        
        some_pd = list(data_dict.values())[0]
        
        argmax_plot_data = GPPlotData(X1=some_pd.X1, X2=some_pd.X2)
        argmax_plot_data.mean = np.argmax([d.mean for d in 
                                             data_dict.values()], axis=0)
        
        argmax_plot_data.std = np.argmax([d.std for d in 
                                             data_dict.values()], axis=0)
        
        argmax_plot_data.acq = np.argmax([d.acq for d in 
                                             data_dict.values()], axis=0)
        
        plt.figure(figsize=(10,5))
        subplotf = lambda idx: plt.subplot(1,3,idx)
        
        self._plot_single_practice_mode(argmax_plot_data, subplotf)
        ax = subplotf(1)
        row = "ARGMAX"
        pad = 5
        ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')
        plt.show()
        
        
        
def gen_tasks(num_tasks=1000, seed=546354):
    rng = np.random.default_rng(seed)
    
    for i in range(num_tasks):
        bpm = rng.integers(*BPM_BOUNDS) 
        note_range = rng.choice(NoteRangePerHand)
    
        yield TaskParameters(bpm=bpm, note_range=note_range)
    
def task2error(task_parameters):
    return Error(pitch=task_parameters.note_range.value,
                timing=task_parameters.bpm/100
                 )

def task2error2(np_array):
    def note_range_map(v):
        import math
        return [NoteRangePerHand.EASY.value, NoteRangePerHand.MEDIUM.value, 
                NoteRangePerHand.HARD.value][int(math.floor(v))]
    
    out = [[note_range_map(nr), bpm/100] for nr, bpm in np_array]
    return np.array(out)
    
def perf_bad_pitch(error):
    return Error(timing=error.timing,
                 pitch=error.pitch*1.5)

def perf_bad_timing(error):
    return Error(timing=error.timing*1.75,
                 pitch=error.pitch)

def perf_balanced(error):
    return Error(timing=error.timing,
                 pitch=error.pitch)
    
def per_after_practice(practice_mode, error):
    if practice_mode == PracticeMode.IMP_PITCH:
        return perf_after_pitch_practice(error)
    if practice_mode == PracticeMode.IMP_TIMING:
        return perf_after_timing_practice(error)
    raise Exception()

def perf_after_pitch_practice(error):
    return Error(timing=error.timing,
                 pitch=error.pitch*0.5)

def perf_after_timing_practice(error):
    return Error(timing=error.timing*0.5,
                 pitch=error.pitch)

def error_diff_to_utility(error_pre, error_post):
    diff_timing = error_post.timing - error_pre.timing
    diff_pitch  = error_post.pitch  - error_pre.pitch
    
    
    MEAN_UTILITY = 0.75
    
    return - (diff_timing*1 + diff_pitch*1) - MEAN_UTILITY


def calc_optimal_policy(performance):
    bounds = [[0,3], BPM_BOUNDS]
            
    
    X1 = np.linspace(bounds[0][0], bounds[0][1], 200, endpoint=False)
    # X1 = np.array([0,1,2])
    X2 = np.linspace(bounds[1][0], bounds[1][1], 200)
    x1, x2 = np.meshgrid(X1, X2)
    X = np.hstack((    
         x1.reshape(200*200,1),
          x2.reshape(200*200,1)))
    
    error2d = task2error2(X)
    error2d = np.array([performance(Error(*err)) for err in error2d])
    # print(error2d)
    error1d = np.sum(error2d, axis=1)
    error1d_pitch = np.array([a for a, b in error2d])
    error1d_timing = np.array([b for a, b in error2d])
    
    err_post_pitch = np.array(
        [perf_after_pitch_practice(Error(*err)) for err in error2d])
    
    err_post_timing = np.array(
        [perf_after_timing_practice(Error(*err)) for err in error2d])
    
    error1d = np.sum(err_post_timing, axis=1)
    
    argmax = np.argmin(np.vstack((
        np.sum(err_post_timing, axis=1),
        np.sum(err_post_pitch, axis=1)
        )), axis=0)
    
    
    error_diff = np.array([timing-pitch for timing, pitch in
                          zip(
        np.sum(err_post_timing, axis=1),
        np.sum(err_post_pitch, axis=1))])
    
    return argmax.reshape(200*200,1), np.abs(error_diff.reshape(200*200,1))

def compare_to_best_policy(policy_argmax, best_argmax, best_error_diff):
    num_diff_cases = np.sum(np.abs(policy_argmax-best_argmax))
    
    abs_diff = num_diff_cases / policy_argmax.shape[0]
    weighted_diff = np.sum(best_error_diff[policy_argmax!=best_argmax]) / \
                            (np.median(best_error_diff) * best_error_diff.shape[0])
    
    return abs_diff, weighted_diff

def plot_best_policy():
    label_x = "NoteRange"
    label_y = "BPM"
    
    bounds = [[0,3], BPM_BOUNDS]
            
    
    X1 = np.linspace(bounds[0][0], bounds[0][1], 200, endpoint=False)
    # X1 = np.array([0,1,2])
    X2 = np.linspace(bounds[1][0], bounds[1][1], 200)
    x1, x2 = np.meshgrid(X1, X2)
    X = np.hstack((    
         x1.reshape(200*200,1),
          x2.reshape(200*200,1)))
    
    
    # print(X)
    plt.figure(figsize=(10,5))
    for idx, performance in enumerate([perf_bad_pitch, perf_balanced,
                                       perf_bad_timing]):
        title = ["Bad Pitch", "Balanced", "Bad Timing"][idx]
        
        error2d = task2error2(X)
        error2d = np.array([performance(Error(*err)) for err in error2d])
        # print(error2d)
        error1d = np.sum(error2d, axis=1)
        error1d_pitch = np.array([a for a, b in error2d])
        error1d_timing = np.array([b for a, b in error2d])
        
        err_post_pitch = np.array(
            [perf_after_pitch_practice(Error(*err)) for err in error2d])
        
        err_post_timing = np.array(
            [perf_after_timing_practice(Error(*err)) for err in error2d])
        
        error1d = np.sum(err_post_timing, axis=1)
        
        argmax = np.argmin(np.vstack((
            np.sum(err_post_timing, axis=1),
            np.sum(err_post_pitch, axis=1)
            )), axis=0)
        
        
        error_diff = np.array([timing-pitch for timing, pitch in
                              zip(
            np.sum(err_post_timing, axis=1),
            np.sum(err_post_pitch, axis=1))])
        
        # print(error1d.shape, error1d)
        # X = enforce_categoricals(X)
        # X_spaced = self._domain2space(X)
        # print(X[:100,:])
        
        # acqu = acquisition_function(X_spaced)
        # acqu_normalized = acqu #(-acqu - min(-acqu))/(max(-acqu - min(-acqu)))
        
        # m, v = model.predict(X_spaced)
        
        # Xdata = bayes_opt.X
        bounds = [[0,3], [50,200]]
        # color_by_step = True
        
        ## Derived from GPyOpt/plotting/plots_bo.py
        # n = Xdata.shape[0]
        # colors = np.linspace(0, 1, n)
        # cmap = plt.cm.Reds
        # norm = plt.Normalize(vmin=0, vmax=1)
        # points_var_color = lambda X: plt.scatter(
        #     X[:,0], X[:,1], c=colors, label=u'Observations', cmap=cmap, norm=norm)
        # points_one_color = lambda X: plt.plot(
        #     X[:,0], X[:,1], 'r.', markersize=10, label=u'Observations')
        
       
        
        # print(X[:100,:])
        # m, v = model.predict(X_spaced)
        
        plt.subplot(1, 3, idx+1)
        plt.contourf(X1, X2, argmax.reshape(200,200),50,)
        plt.xlabel(label_x)
        if idx == 0:
            plt.ylabel(label_y)
        plt.title(title)
        plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
        
        if idx == 0:
            from matplotlib.patches import Patch
            cmap = plt.cm.viridis
            custom_lines = [Patch(facecolor=cmap(1.)),
                        Patch(facecolor=cmap(0.)),]
            plt.legend(custom_lines, ["IMP_PITCH", "IMP_TIMING"])
        
    # plt.savefig("optimal_policies.eps")
    plt.show()
    
def single_experiment_run(inp_tup):
        performer, noise_var, bpm_norm_fac = inp_tup
        res = _single_experiment_run(num_rounds=75, 
                                    performer=performer, 
                                    task_err_noise_var=noise_var, 
                                    utility_noise_var=noise_var, 
                                    bpm_norm_fac=bpm_norm_fac)
        return (performer, noise_var, bpm_norm_fac), res

def _single_experiment_run(num_rounds, 
                          performer, 
                          task_err_noise_var, utility_noise_var,
                          bpm_norm_fac,
                          seed=None,
                          plot=False):
    
    
    seed = seed or random.randint(0, 2**16)
    
    performance_dict = dict(bad_pitch=perf_bad_pitch,
                            balanced=perf_balanced,
                            bad_timing=perf_bad_timing)
    
    perf_string = str(performer)
    performer = performance_dict[perf_string]
    
    best_policy = calc_optimal_policy(performer)
    policy_diffs = list()
    
    GP = GaussianProcess(bpm_norm_fac=bpm_norm_fac)
    c = 0
    for idx, tp in enumerate(gen_tasks(num_rounds, seed=seed)):
        if idx % 3 == 0:
            GP.update_model()
            policy_diff = compare_to_best_policy(GP.get_policy(c),
                *best_policy)
        
        policy_diffs.append(policy_diff[1]) # only use weighted diff 
        # tqdm.write(f"Policy Diff: {policy_diff}")
        
        # print(tp)
        task_error = task2error(tp)
        
        task_error = Error(
            pitch=task_error.pitch* random.gauss(1,task_err_noise_var),
            timing=task_error.timing* random.gauss(1,task_err_noise_var),)
        
        
        error_pre = performer(task_error)
        given_practice_mode = GP.get_best_practice_mode(c, tp)
        # given_practice_mode = [PracticeMode.IMP_PITCH, 
        #                         PracticeMode.IMP_TIMING][np.random.randint(0,2)]
        error_post = per_after_practice(given_practice_mode, error_pre)
        utility = error_diff_to_utility(error_pre, error_post)
        
        utility *= random.gauss(1,utility_noise_var)
        
        GP.add_data_point(c, tp, given_practice_mode, utility)
        
    if plot:
        GP.plot_mutiple(c, [
            
            PracticeMode.IMP_TIMING,
            PracticeMode.IMP_PITCH,
            ])
        
        plt.plot(list(range(len(policy_diffs))), policy_diffs)
        plt.ylim((-0.01,None))
        plt.show()
        
    return policy_diffs

def run_all_combinations():
    num_per_comb = 10
    performers = ["balanced"] #["bad_pitch", "balanced", "bad_timing"]
    noise_vars = [0.0, 0.1, 0.25, 0.5] # [0.0, 0.1] #
    bpm_norm_facs = [10] #1
    
    import itertools
    comb = list()
    for performer, noise_var, bpm_norm_fac in itertools.product(performers, 
                                                                 noise_vars,
                                                                 bpm_norm_facs):
        comb.extend([(performer, noise_var, bpm_norm_fac)]*num_per_comb)
        
    from multiprocessing import Pool
    pool = Pool(12)
    
    
    from tqdm import tqdm
    results = list()
    for res in tqdm(pool.imap_unordered(single_experiment_run, comb),
                    total=len(comb),
                    smoothing=0):
    # for res in tqdm(map(single_experiment_run, comb), # for debugging
    #             total=len(comb)):
        results.append(res)
        
    res_dicts = list()
    for (performer, noise_var, bpm_norm_fac), diffs in results:
        pre_dict = dict(performer=performer,
                        noise_var=noise_var,
                        bpm_norm_fac=bpm_norm_fac)
        for idx, val in enumerate(diffs):
            d = pre_dict.copy()
            d["iteration"] = idx+1
            d["weighted_error"] = val
            
            res_dicts.append(d)
            
    
        
    return res_dicts
        
    
    
    

if __name__ == "__main__":
    STARTING_COMPLEXITY_LEVEL = 0
    c = STARTING_COMPLEXITY_LEVEL
    
    
    
    
    # performer = perf_bad_timing
    # performer = perf_bad_pitch
    performer = perf_balanced
    
    # results = run_all_combinations()
    
    # plot_best_policy()
    
    import sys
    # sys.exit()
    
    task_err_noise_var = 0.1
    utility_noise_var =  0.1
    
    from tqdm import tqdm
    
    best_policy = calc_optimal_policy(performer)
    policy_diffs = list()
    
    num_rounds = 40
    GP = GaussianProcess()
    for idx, tp in enumerate(tqdm(gen_tasks(num_rounds, 5), total=num_rounds)):
        if idx % 3 == 0:
            GP.update_model()
            policy_diff = compare_to_best_policy(GP.get_policy(c),
                *best_policy)
            
        policy_diffs.append(policy_diff)
        tqdm.write(f"Policy Diff: {policy_diff}")
        
        # print(tp)
        task_error = task2error(tp)
        
        task_error = Error(
            pitch=task_error.pitch* random.gauss(1,task_err_noise_var),
            timing=task_error.timing* random.gauss(1,task_err_noise_var),)
        
        
        error_pre = performer(task_error)
        given_practice_mode = GP.get_best_practice_mode(c, tp)
        # given_practice_mode = [PracticeMode.IMP_PITCH, 
        #                         PracticeMode.IMP_TIMING][np.random.randint(0,2)]
        error_post = per_after_practice(given_practice_mode, error_pre)
        utility = error_diff_to_utility(error_pre, error_post)
        
        utility *= random.gauss(1,utility_noise_var)
        
        GP.add_data_point(c, tp, given_practice_mode, utility)
        # GP.update_model()
        
        tqdm.write("\n")
        tqdm.write(f"NoteRange = {tp.note_range}")
        tqdm.write(f"BPM = {tp.bpm}")
        tqdm.write(f"Suggested PracticeMode: {given_practice_mode}")
        tqdm.write(f"Error Pre: {error_pre}")
        tqdm.write(f"Error post: {error_post}")
        tqdm.write(f"Utility: {utility}")
        tqdm.write("-"*32)
        
    GP.plot_mutiple(c, [
        
        PracticeMode.IMP_TIMING,
        PracticeMode.IMP_PITCH,
        ])
    
    plt.plot(list(range(len(policy_diffs))), policy_diffs)
    plt.ylim((-0.01,None))
    plt.show()
    
        

    