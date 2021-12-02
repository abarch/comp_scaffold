#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from task_generation.generator import TaskParameters

SIMPLIFIED_TEST_ENUMS = False

if SIMPLIFIED_TEST_ENUMS == False:
    from task_generation.practice_modes import PracticeMode
    from task_generation.note_range_per_hand import NoteRangePerHand
    
else:
    import enum
    class PracticeMode(enum.Enum):
        IMP_PITCH = enum.auto()
        IMP_TIMING = enum.auto()
        
    class NoteRangePerHand(enum.Enum):
        EASY = enum.auto()
        MEDIUM = enum.auto()
        HARD = enum.auto()
    
    
#FIXME: next - shorten the dictionary to the first three elements
practicemode2int = {pm: i for i, pm in enumerate(PracticeMode)}
int2practicemode = {i: pm for i, pm in enumerate(PracticeMode)}
print ("pracitcemode 2 int ", type(practicemode2int))
print (" int2 practice mode", int2practicemode)


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
    

# def hands2int(left, right):
#     r = -1
#     if left:
#         r+=2
#     if right:
#         r+=1
#     return r

def round_to_closest(f, vals):
    diff = [(abs(f-v), v) for v in vals]
    diff = sorted(diff)
    return diff[0][1]

def enforce_categoricals(np_array):
    np_array[:,1] = np.floor(np_array[:,1])
    np_array[:,2] = np.floor(np_array[:,2])
    
    return np_array.astype(int)

# imp left pitch, imp right pitch imp both (identity) analyse only pitch errors, hands are always both true
class GaussianProcess:
    domain =[ # {'name': 'complexity_level', 'type': 'discrete', 'domain': tuple(range(10))},
              {'name': 'practice_mode', 'type': 'categorical', 'domain': (0,1,2)},
              #{'name': 'hands', 'type': 'categorical', 'domain': (0,1,2)},
             {'name': 'bpm', 'type': 'discrete', 'domain': range(50, 201)},
             #{'name': 'notes_left', 'type': 'discrete', 'domain': range(0,5)},
             {'name': 'notes_right', 'type': 'discrete', 'domain': range(1,5)}
             ]
             # only subset of task_parameters for easier testing for now
    space = GPyOpt.core.task.space.Design_space(domain)
        
    def _params2domain(self,  task_parameters, practice_mode):
        #TODO normalize these here??
        domain_x = [ # complexity_level,
                    practicemode2int[practice_mode],
                    #int(task_parameters.note_range_left),
                    int(task_parameters.note_range_right.value),
                    # hands2int(task_parameters.left, task_parameters.right),
                    int(task_parameters.bpm),
                    ]
        
        
        return np.array([domain_x])
        
    def _domain2space(self, domain_x):
        # domain_x = np.array([domain_x])
        print(domain_x.shape)
        space_rep = self.space.unzip_inputs(domain_x)
        print("DX", domain_x, domain_x.shape)
        print("SX", space_rep)
        return space_rep
    
    def __init__(self):
        self.data_X = None
        self.data_Y = None
        
    def _get_bayes_opt(self):
        global bayes_opt
        
        # kernel = GPy.kern.RBF(input_dim=4, 
        #                       variance=0.22, 
        #                       lengthscale=0.000001)
        
        bayes_opt = GPyOpt.methods.BayesianOptimization(
            f = None, domain = self.domain, X = self.data_X, Y = self.data_Y,
            maximize=True,
            # kernel=kernel,
            # normalize_Y=False,
                                                  # kernel=kernel,
                                             )
        bayes_opt._update_model() #.suggest_next_locations()
        ## somehow needed, otherwise the model is None
        return bayes_opt
    
    def get_estimate(self, task_parameters, practice_mode):
        if self.data_X is None:
            print("(GP) DATA_X IS NONE, RETURNING RANDOM NUMBER")
            return random.random()
        
        # print(self.data_X, self.data_Y)
        # print(self.data_X.shape, self.data_Y.shape)
        
        bayes_opt = self._get_bayes_opt()
        
        
        X = self._params2domain( task_parameters, practice_mode)
        X = self._domain2space(X)
        
        # print(bayes_opt.X, bayes_opt.X.shape)
        
        # print(bayes_opt.model.predict)
        
        # print("XX", X)
        
        mean, var = bayes_opt.model.predict(X)
        print("EST RES:", mean[0], var[0])
        return mean[0]
        
        
    def get_best_practice_mode(self,  task_parameters):
        all_practice_modes = list(PracticeMode)
        return all_practice_modes[np.argmax([self.get_estimate(task_parameters, pm)
                                             for pm in all_practice_modes])]
    
    def add_data_point(self,  task_parameters, practice_mode,
                       utility_measurement):
        new_x =  self._params2domain(task_parameters, practice_mode)
        new_y = [ utility_measurement ]
        
        if self.data_X is None:
            self.data_X = new_x
            self.data_Y = new_y
        else:
            # print(self.data_X, new_x)
            self.data_X = np.vstack((self.data_X, new_x[0]))
            self.data_Y = np.vstack((self.data_Y, new_y[0]))
    
    
    def _get_plot_data(self, data_dict,  practice_mode, bayes_opt):
        bounds = [[0,3], [50,200]]
        c=0
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
        acqu_normalized = acqu #(-acqu - min(-acqu))/(max(-acqu - min(-acqu)))
        
        m, v = model.predict(X_spaced)
        
        data_dict[practice_mode].mean = m
        data_dict[practice_mode].std = np.sqrt(v)
        data_dict[practice_mode].acq = acqu_normalized
        data_dict[practice_mode].X1 = X1
        data_dict[practice_mode].X2 = X2
        
    
    def _plot_single_practice_mode(self, gp_plot_data, subplotf):
        label_x = "Hands"
        label_y = "BPM"
        
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
        
    
    def plot_single(self, c, practice_mode):
        bayes_opt = self._get_bayes_opt()
        
        plt.figure(figsize=(10,5))
        subplotf = lambda idx: plt.subplot(1,3,idx)
        
        self._plot_single_practice_mode(c, practice_mode, bayes_opt, subplotf)
        plt.show()
        
    def plot_mutiple(self, practice_modes):
        bayes_opt = self._get_bayes_opt()
        
        n_rows = len(practice_modes)
        # n_plots = n_rows*3
        
        data_dict = defaultdict(GPPlotData)
        for i, practice_mode in enumerate(practice_modes):
            self._get_plot_data(data_dict, practice_mode, bayes_opt)
            
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
        
        
        

    
    
if __name__ == "__main__":
    #STARTING_COMPLEXITY_LEVEL = 0
    #c = STARTING_COMPLEXITY_LEVEL
    GP = GaussianProcess()
    
    tp = TaskParameters()
    print("get best practice mode in the beginning before optimization", GP.get_best_practice_mode(tp))

    import random
    for i in range(10):
        print("ADD DATA")
        tp.bpm = 60 + random.randrange(-20,20,2)
        GP.add_data_point(tp,
                          PracticeMode.RIGHT_HAND,
                          10-i)
        GP.add_data_point(tp,
                          PracticeMode.LEFT_HAND,
                          12-i)
        GP.add_data_point(tp,
                          PracticeMode.IDENTITY,
                          8 - i)
    
    # GP.add_data_point(c, tp, 
    #                       PracticeMode.SLOWER, 
    #                       3)
    
    # GP.add_data_point(c, tp, PracticeMode.IDENTITY, 5)
    # GP.add_data_point(c, tp, PracticeMode.SLOWER, 2)
    
    print(" best practice mode", GP.get_best_practice_mode(tp))
    
    # GP.plot_single(c=c, practice_mode=PracticeMode.IDENTITY)
    # GP.plot_single(c=c, practice_mode=PracticeMode.SLOWER)
    GP.plot_mutiple([
        PracticeMode.IDENTITY,
        PracticeMode.LEFT_HAND,
        PracticeMode.RIGHT_HAND
        ])

    