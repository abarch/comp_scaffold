#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from task_generation.generator import TaskParameters
from task_generation.note_range_per_hand import NoteRangePerHand
from task_generation.practice_modes import PracticeMode
import time
import numpy as np
from collections import namedtuple



BPM_BOUNDS = [50,150]

# tell us how many different types of different note ranges we want to use in our exp.
NOTE_RANGE = list(NoteRangePerHand)[1:5]

# parameter that tell us how many practice modes out of the existing list we want to take
PRACTICE_RANGE = 3
PRACTICE_MODES = list(PracticeMode)[0:PRACTICE_RANGE]

# parameter for the stretching of plots
LINSPACE =30

assert (NOTE_RANGE[0].value==1)
assert (NOTE_RANGE[-1].value==4)


## Mappings of categorical data to ints.
### The pracice modes will be mapped onto a single dimension, placed far away
### from each other

practicemode2int = {pm: i*1000 for i, pm in zip(range(PRACTICE_RANGE), PRACTICE_MODES)}
int2practicemode = {i*1000: pm for i, pm in zip(range(PRACTICE_RANGE), PRACTICE_MODES)}


import matplotlib.pyplot as plt
import itertools
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


class GaussianProcess:
    def __init__(self, bpm_norm_fac=100):
        self.data_X = None
        self.data_X_old_shape = None
        
        self.data_Y = None

        # normalisation factor
        self.bpm_norm_fac = bpm_norm_fac


        self.note_number = len(NOTE_RANGE)
        self.note_range=range(1,self.note_number+1)

        self.beat_number = BPM_BOUNDS[1]-BPM_BOUNDS[0]

        assert (self.note_range[0]==1)
        assert (self.note_range[-1]==4)

        self.domain =[

            {'name': 'practice_mode', 'type': 'discrete', 'domain': tuple(i*1000 for i  in range(PRACTICE_RANGE))},
            {'name': 'note_range_right', 'type': 'categorical', 'domain':  range(0,5)}, # self.note_range}, # hier ist die 5 das Problem.  irgendwo wird 5 generiert  # self.note_range},
            {'name': 'bpm', 'type': 'continuous', 'domain': 
                 (self._norm_bpm(BPM_BOUNDS[0]),self._norm_bpm(BPM_BOUNDS[1]))},
                 
                ]

        self.space = GPyOpt.core.task.space.Design_space(self.domain)
        
    def _norm_bpm(self, v):
        return v/self.bpm_norm_fac


    def _params2domain(self, task_parameters, practice_mode):
        domain_x = [
                    practicemode2int[practice_mode],
                    int(task_parameters.note_range_right.value),
                    self._norm_bpm(task_parameters.bpm),
                    ]

        assert(practice_mode.value in range(3))
        assert(task_parameters.note_range_right.value in range(1,5))

        #print ("converted params ", task_parameters, practice_mode, " to domain" ,  domain_x)
        return np.array([domain_x])
        
    def _domain2space(self, domain_x):
        ## Converts the domain variables into the GPs input space
        ## does one-hot encoding
        #print("domain_x ", domain_x)

        space_rep = self.space.unzip_inputs(domain_x)
        #print ("space_rep ", space_rep)
        return space_rep
    
        
    def _get_bayes_opt(self):
        return self.bayes_opt
        
    
    def update_model(self):
        ## only calculate new model if data changed
        if self.data_X is None or self.data_X.shape == self.data_X_old_shape:
            return
        
        
        self.data_X_old_shape = self.data_X.shape
        
        # kernel = GPy.kern.RBF(input_dim=self.space.model_dimensionality, 
        #                       variance=0.01, 
        #                       lengthscale=1)
        
        kernel = GPy.kern.Matern52(input_dim=self.space.model_dimensionality, 
                              variance=0.01, 
                              lengthscale=1)
        
        
        
        self.bayes_opt = GPyOpt.methods.BayesianOptimization(
            f = None, domain = self.domain, X = self.data_X, Y = self.data_Y,
            maximize=True,
            kernel=kernel,
        )

        #print (X)
        self.bayes_opt.model.max_iters = 0
        self.bayes_opt._update_model() 
        
        self.bayes_opt.model.model.kern.variance.constrain_bounded(0.2,1,
                                                                   warning=False)
        self.bayes_opt.model.model.kern.lengthscale.constrain_bounded(1, 2,
                                                                   warning=False)
        
        self.bayes_opt.model.max_iters = 1000
        self.bayes_opt._update_model() 
        
        
        
    # if you have a practice mode and a task parameter tupel , then it will tell you, how useful it is.  At the moemnt it just outputs the mean value
    def get_estimate(self,  task_parameters, practice_mode,
                     add_variance=False):
        if not hasattr(self, "bayes_opt"):
            # if there is no model yet, e.g. in the first iteration
            # print("(GP) DATA_X IS NONE, RETURNING RANDOM NUMBER")
            return random.random()
        
        bayes_opt = self._get_bayes_opt()
        
        X = self._params2domain( task_parameters, practice_mode)
        X = self._domain2space(X)
        
        mean, var = bayes_opt.model.predict(X)
        
        r = mean[0]
        if add_variance:
            r += np.sqrt(var[0])
        return r
        
    # if you have a task parameter tupel, this thing will give you the practice mode that is the best w.r.t the current model
    # Important that the actually best practice mode is being selected only when random.random>0.05 (so that means - in most cases!)
    def get_best_practice_mode(self,  task_parameters):
        all_practice_modes = PRACTICE_MODES
        if random.random() > 0.05:
            max_i = np.argmax([self.get_estimate( task_parameters, pm)
                                             for pm in all_practice_modes])
            return all_practice_modes[max_i]
        
        else:
            # use weighted choice based on softmax
            # increases exploration
            def softmax(x):
                return np.exp(x) / np.sum(np.exp(x), axis=0)

            # the larger the utility of the practice mode, the higher the probability that it gets chosen?
            return random.choices(all_practice_modes, 
                                  softmax(
                [0.5*self.get_estimate( task_parameters, pm)
                                             for pm in all_practice_modes]), k=1)[0]
            
    
    def add_data_point(self,  task_parameters, practice_mode,
                       utility_measurement):
        new_x =  self._params2domain(task_parameters, practice_mode)
        new_y = [ utility_measurement ]
        
        if self.data_X is None:
            self.data_X = new_x
            self.data_Y = [new_y]
        else:
            self.data_X = np.vstack((self.data_X, new_x[0]))
            self.data_Y = np.vstack((self.data_Y, new_y[0]))


    def get_policy(self):
        # in case the policy the model does not exist, provide a random policy
        if not hasattr(self, "bayes_opt"):
            print ("the policy does not exist yet, output a random policy")
            return np.round(np.random.random((self.note_number*self.beat_number,1)))
        
        bayes_opt = self._get_bayes_opt()
        
        data_dict = defaultdict(GPPlotData)
        for i, practice_mode in zip(range(PRACTICE_RANGE), PRACTICE_MODES):
            # insert plot data into the data_dict, given a practice mode
            self._get_plot_data(data_dict, practice_mode, bayes_opt)

        # output which of the practice modes has the highest means for each parameter combination?
        tmp= [d.mean for d in [
            data_dict[PracticeMode.LEFT_HAND], data_dict[PracticeMode.RIGHT_HAND], data_dict[PracticeMode.IDENTITY]]]
        #print ("---------------")
        #print (tmp)
        #print ("---------------")
        m = np.argmax(tmp, axis=0)
        print ("best policy ", m)
        return m
    
    
    def _get_plot_data(self, data_dict, practice_mode, bayes_opt, for_plot=False):
        #c=0
        bounds = [(self.note_range[0], self.note_range[-1]), (self._norm_bpm(BPM_BOUNDS[0]),self._norm_bpm(BPM_BOUNDS[1]))]
        
        acquisition_function = bayes_opt.acquisition.acquisition_function
        model = bayes_opt.model

        # set the first parameter (number of notes!!!)
        if not for_plot:
            X1 = np.array([i for i in self.note_range])
            X1_axis = X1
            reshape_dim = self.note_number*self.beat_number

        else: # do that one can see a bit more, get more points into the grid from the predefined bound of the x-axis!
            X1_axis = np.linspace(bounds[0][0], bounds[0][1], LINSPACE*self.note_number, endpoint=False)

            assert (bounds[0][0]== 1)
            assert( bounds[0][1] ==4)

            X1 = np.array( [1]*LINSPACE +[2]*LINSPACE + [3]*LINSPACE + [4] *LINSPACE)
            reshape_dim = LINSPACE*self.note_number*self.beat_number
            
        X2 = np.linspace(bounds[1][0], bounds[1][1], self.beat_number)
        
        x1, x2 = np.meshgrid(X1, X2)
        X = np.hstack((
            
            #np.array([c]*(reshape_dim)).reshape(reshape_dim,1),
            np.array([practicemode2int[practice_mode]]*(reshape_dim)).reshape(reshape_dim,1),
            x1.reshape(reshape_dim,1),
             x2.reshape(reshape_dim,1)))

        #print ("domain before breaking", X)
        X_spaced = self._domain2space(X)
        #print ("spaced", X_spaced)
         
        acqu = acquisition_function(X_spaced)
        
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
        data_dict[practice_mode].X1 = X1_axis
        data_dict[practice_mode].X2 = X2
        
    
    def _plot_single_practice_mode(self, gp_plot_data, subplotf,
                                   plot_mean=True,
                                   plot_std=False,
                                   plot_acq=False):
        label_x = "NoteRange"
        label_y = "BPM"

        X_TICKS = ([i for i in self.note_range], [str(i) for i in self.note_range])
        #print ("X_TICKS", X_TICKS)
        #X_TICKS = ([0.5,1.5,2.5], ["0", "1", "2"])
        
        bounds = [(self.note_range[0], self.note_range[-1]), (self._norm_bpm(BPM_BOUNDS[0]),self._norm_bpm(BPM_BOUNDS[1]))]
        print ("bounds",  bounds)
        ## Derived from GPyOpt/plotting/plots_bo.py
        X1 = gp_plot_data.X1
        X2 = gp_plot_data.X2
        
        def inflate_array(a):
            #print (len(a))
            #print  (50 * self.note_number, self.beat_number)
            return a.reshape((self.beat_number, LINSPACE*self.note_number ))
        
        subplot_count = 0
        
        if plot_mean:
            subplot_count += 1
            print ("subplot count" , subplot_count)
            subplotf(subplot_count)
            #print ("gp_plot_data.mean!!!!!!!", gp_plot_data.mean )
            plt.contourf(X1, X2, inflate_array(gp_plot_data.mean),100,
                         vmin=gp_plot_data.mean_min,
                         vmax=gp_plot_data.mean_max,)
            plt.colorbar()
            plt.xlabel(label_x)
            plt.ylabel(label_y)
            plt.title('Posterior mean')
            plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
            plt.xticks(*X_TICKS)
            #plt.show()
        ##
        
        if plot_std:
            subplot_count += 1
            subplotf(subplot_count)
            plt.contourf(X1, X2, inflate_array(gp_plot_data.std),100,
                         vmin=gp_plot_data.std_min,
                         vmax=gp_plot_data.std_max)
            plt.colorbar()
            plt.xlabel(label_x)
            plt.ylabel(label_y)
            plt.title('Posterior sd.')
            plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
            plt.xticks(*X_TICKS)
        ##
        
        
        if plot_acq:
            subplot_count += 1
            subplotf(subplot_count)
            plt.contourf(X1, X2, inflate_array(gp_plot_data.acq),100,
                         vmin=gp_plot_data.acq_min,
                         vmax=gp_plot_data.acq_max,)
            plt.colorbar()
            plt.xlabel(label_x)
            plt.ylabel(label_y)
            plt.title('Acquisition function')
            plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
            plt.xticks(*X_TICKS)
            
    
    def plot_multiple(self, practice_modes,
                                   plot_mean=True,
                                   plot_std=True,
                                   plot_acq=True):
        bayes_opt = self._get_bayes_opt()
        
        n_rows = len(practice_modes)
        n_cols = sum([plot_mean, plot_std, plot_acq])
        fig = plt.figure(figsize=(n_cols * 3.34, 5 * n_rows))


        data_dict = defaultdict(GPPlotData)

        for i, practice_mode in enumerate(practice_modes):
            self._get_plot_data(data_dict, practice_mode, bayes_opt,
                                for_plot=True)

        mean_max, std_max, acq_max = np.max([d.apply_to_arrays(np.max) for d in 
                                             data_dict.values()], axis=0)
        # print (mean_max)
        
        mean_min, std_min, acq_min = np.min([d.apply_to_arrays(np.min) for d in 
                                             data_dict.values()], axis=0)
        
        for pd in data_dict.values():

            pd.mean_max = mean_max
            pd.mean_min = mean_min
            pd.std_max = std_max
            pd.std_min = std_min
            pd.acq_max = acq_max
            pd.acq_min = acq_min
        #print (data_dict)

        #n_rows = len(practice_modes)
        #n_cols = sum([plot_mean, plot_std, plot_acq])
        print (n_rows, n_cols)
        for i, practice_mode in enumerate(practice_modes):
            subplotf = lambda idx: plt.subplot(n_rows, n_cols, i * n_cols + idx)


            ax = subplotf(1)
            row = practice_mode.name
            pad = 5
            ax.annotate(row , xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                         xycoords=ax.yaxis.label, textcoords='offset points',
                         size='large', ha='right', va='center')


            self._plot_single_practice_mode(data_dict[practice_mode], subplotf,
                                            plot_mean=plot_mean,
                                            plot_std=plot_std,
                                            plot_acq=plot_acq)
            

        
        fig.tight_layout()
        plt.show()
        #plt.savefig("detailed_noise05.png")


        some_pd = list(data_dict.values())[0]
        #what happens here is we take a look at all (means,stds, ..) and compare which
        # practice modes has the highest. then we plot for each grid element - the number
        # of the practice that should be used accordidng to the policy



        argmax_plot_data = GPPlotData(X1=some_pd.X1, X2=some_pd.X2)
        argmax_plot_data.mean = np.argmax([d.mean for d in 
                                             data_dict.values()], axis=0)
        # print ("argmax ",  argmax_plot_data.mean)
        
        argmax_plot_data.std = np.argmax([d.std for d in 
                                             data_dict.values()], axis=0)
        
        argmax_plot_data.acq = np.argmax([d.acq for d in 
                                             data_dict.values()], axis=0)
        
        plt.figure(figsize=(10,5))
        subplotf = lambda idx: plt.subplot(1,3,idx)
        ax = subplotf(1)
        row = "ARGMAX"
        pad = 5
        ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center')
        self._plot_single_practice_mode(argmax_plot_data, subplotf)

        plt.show()
        
        
        
def gen_tasks(num_tasks=None, seed=546354):
    assert num_tasks != None
    rng = np.random.default_rng(seed)
    
    for i in range(num_tasks):
        bpm = rng.integers(*BPM_BOUNDS) 
        note_range_right = rng.choice(NOTE_RANGE)
    
        yield TaskParameters(bpm=bpm, note_range_right=note_range_right)



if __name__ == "__main__":
    #STARTING_COMPLEXITY_LEVEL = 0
    #c = STARTING_COMPLEXITY_LEVEL
    GP = GaussianProcess()
    GP.update_model()

    tp = TaskParameters()
    print("get best practice mode in the beginning before optimization", GP.get_best_practice_mode(tp))


    import random
    for i, tp in enumerate(gen_tasks(20)):
        print("ADD DATA")
        #print ("new screwy task parameters ", tp)

        GP.add_data_point(tp,
                             PracticeMode.RIGHT_HAND,
                          random.randrange(-20,20,1)+tp.note_range_right.value*10+tp.bpm)
        GP.add_data_point(tp,
                          PracticeMode.LEFT_HAND,
                          random.randrange(-50,50,1)+tp.note_range_right.value*15+tp.bpm)
        GP.add_data_point(tp,
                          PracticeMode.IDENTITY,
                          random.randrange(-200,200,1)+tp.note_range_right.value*30-2*tp.bpm)
        GP.update_model()
        print(" best practice mode", GP.get_best_practice_mode(tp))
    # GP.add_data_point(c, tp,
    #                       PracticeMode.SLOWER,
    #                       3)

    # GP.add_data_point(c, tp, PracticeMode.IDENTITY, 5)
    # GP.add_data_point(c, tp, PracticeMode.SLOWER, 2)




    # GP.plot_single(c=c, practice_mode=PracticeMode.IDENTITY)
    # GP.plot_single(c=c, practice_mode=PracticeMode.SLOWER)
    GP.plot_multiple([
        PracticeMode.IDENTITY,
        PracticeMode.LEFT_HAND,
        PracticeMode.RIGHT_HAND
        ])

#
# if __name__ == "__main__":
#     # single_test_run()
#     # run_all_combinations()
#     # plot_best_policy()
#     pass
#



    
# def task2error(task_parameters):
#     return Error(pitch=task_parameters.note_range_right.value,
#                 timing=task_parameters.bpm/100
#                  )
#
# def task2error2(np_array):
#     def note_range_map(v):
#         import math
#         return [NoteRangePerHand.ONE_NOTE.value, NoteRangePerHand.TWO_NOTES.value,
#                 NoteRangePerHand.THREE_NOTES.value][int(math.floor(v))]
#
#     out = [[note_range_map(nr), bpm/100] for nr, bpm in np_array]
#     return np.array(out)
#
# def perf_bad_pitch(error):
#     return Error(timing=error.timing,
#                  pitch=error.pitch*1.5)
#
# def perf_bad_timing(error):
#     return Error(timing=error.timing*1.75,
#                  pitch=error.pitch)
#
# def perf_balanced(error):
#     return Error(timing=error.timing,
#                  pitch=error.pitch)
#
# def per_after_practice(practice_mode, error):
#     if practice_mode == PracticeMode.IMP_PITCH:
#         return perf_after_pitch_practice(error)
#     if practice_mode == PracticeMode.IMP_TIMING:
#         return perf_after_timing_practice(error)
#     raise Exception()
#
# def perf_after_pitch_practice(error):
#     return Error(timing=error.timing,
#                  pitch=error.pitch*0.5)
#
# def perf_after_timing_practice(error):
#     return Error(timing=error.timing*0.5,
#                  pitch=error.pitch)
#
# def error_diff_to_utility(error_pre, error_post):
#     diff_timing = error_post.timing - error_pre.timing
#     diff_pitch  = error_post.pitch  - error_pre.pitch
#
#
#     MEAN_UTILITY = 0.75
#
#     return - (diff_timing*1 + diff_pitch*1) - MEAN_UTILITY
#
#
# def calc_optimal_policy(performance):
#     bounds = [[0,3], BPM_BOUNDS]
#
#     X1 = np.array([0,1,2])
#     X2 = np.linspace(bounds[1][0], bounds[1][1], 150)
#     x1, x2 = np.meshgrid(X1, X2)
#     X = np.hstack((
#          x1.reshape(3*150,1),
#           x2.reshape(3*150,1)))
#
#     error2d = task2error2(X)
#     error2d = np.array([performance(Error(*err)) for err in error2d])
#
#     err_post_pitch = np.array(
#         [perf_after_pitch_practice(Error(*err)) for err in error2d])
#
#     err_post_timing = np.array(
#         [perf_after_timing_practice(Error(*err)) for err in error2d])
#
#
#     argmax = np.argmin(np.vstack((
#         np.sum(err_post_timing, axis=1),
#         np.sum(err_post_pitch, axis=1)
#         )), axis=0)
#
#
#     error_diff = np.array([timing-pitch for timing, pitch in
#                           zip(
#         np.sum(err_post_timing, axis=1),
#         np.sum(err_post_pitch, axis=1))])
#
#     return argmax.reshape(3*150,1), np.abs(error_diff.reshape(3*150,1))
#
# def compare_to_best_policy(policy_argmax, best_argmax, best_error_diff):
#     num_diff_cases = np.sum(np.abs(policy_argmax-best_argmax))
#
#     abs_diff = num_diff_cases / policy_argmax.shape[0]
#     weighted_diff = np.sum(best_error_diff[policy_argmax!=best_argmax]) / \
#                             (np.median(best_error_diff) * best_error_diff.shape[0])
#
#     return abs_diff, weighted_diff
#
# def plot_best_policy():
#     label_x = "NoteRange"
#     label_y = "BPM"
#
#     bounds = [[0,3], BPM_BOUNDS]
#     X_TICKS = ([0.5,1.5,2.5], ["0", "1", "2"])
#
#     X1 = np.linspace(bounds[0][0], bounds[0][1], 150, endpoint=False)
#     X2 = np.linspace(bounds[1][0], bounds[1][1], 150)
#     x1, x2 = np.meshgrid(X1, X2)
#     X = np.hstack((
#          x1.reshape(150*150,1),
#           x2.reshape(150*150,1)))
#
#
#     plt.figure(figsize=(10,5))
#     for idx, performance in enumerate([perf_bad_pitch, perf_balanced,
#                                        perf_bad_timing]):
#         title = ["Bad Pitch", "Balanced", "Bad Timing"][idx]
#
#         error2d = task2error2(X)
#         error2d = np.array([performance(Error(*err)) for err in error2d])
#
#         err_post_pitch = np.array(
#             [perf_after_pitch_practice(Error(*err)) for err in error2d])
#
#         err_post_timing = np.array(
#             [perf_after_timing_practice(Error(*err)) for err in error2d])
#
#
#         argmax = np.argmin(np.vstack((
#             np.sum(err_post_timing, axis=1),
#             np.sum(err_post_pitch, axis=1)
#             )), axis=0)
#
#
#         plt.subplot(1, 3, idx+1)
#         plt.contourf(X1, X2, argmax.reshape(150,150),50,)
#         plt.xlabel(label_x)
#         if idx == 0:
#             plt.ylabel(label_y)
#         plt.title(title)
#         plt.axis((bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1]))
#         plt.xticks(*X_TICKS)
#
#         if idx == 0:
#             from matplotlib.patches import Patch
#             cmap = plt.cm.viridis
#             custom_lines = [Patch(facecolor=cmap(1.)),
#                         Patch(facecolor=cmap(0.)),]
#             plt.legend(custom_lines, ["IMP_PITCH", "IMP_TIMING"])
#
#     # plt.savefig("optimal_policies.eps")
#     plt.show()
#
# def single_experiment_run_tup(inp_tup, num_rounds):
#         performer, noise_var, bpm_norm_fac = inp_tup
#         gp, policy_diffs, kernel_params = single_experiment_run(
#                                     num_rounds=num_rounds,
#                                     performer=performer,
#                                     task_err_noise_var=noise_var,
#                                     utility_noise_var=noise_var,
#                                     bpm_norm_fac=bpm_norm_fac)
#         return (performer, noise_var, bpm_norm_fac), policy_diffs
#
# def single_experiment_run(num_rounds,
#                           performer,
#                           task_err_noise_var, utility_noise_var,
#                           bpm_norm_fac,
#                           seed=None,
#                           plot=False,
#                           print_details=False):
#
#     if print_details:
#         from tqdm import tqdm
#     else:
#         def tqdm(iterable, **kwargs):
#             for x in iterable:
#                 yield(x)
#
#     seed = seed or random.randint(0, 2**16)
#
#     performance_dict = dict(bad_pitch=perf_bad_pitch,
#                             balanced=perf_balanced,
#                             bad_timing=perf_bad_timing)
#
#     perf_string = str(performer)
#     performer = performance_dict[perf_string]
#
#     best_policy = calc_optimal_policy(performer)
#     policy_diffs = list()
#     kernel_params = list()
#
#     GP = GaussianProcess(bpm_norm_fac=bpm_norm_fac)
#     c = 0
#
#     for idx, tp in enumerate(tqdm(gen_tasks(num_rounds, seed=seed),
#                                   total=num_rounds)):
#         if idx % 3 == 0:
#             _pre = time.time()
#
#             GP.update_model()
#             policy_diff = compare_to_best_policy(GP.get_policy(c),
#                 *best_policy)
#
#
#         if hasattr(GP, "bayes_opt"):
#             kernel_params.append(list(map(lambda a:a.values[0],
#                     GP.bayes_opt.model.model.kern.parameters)))
#
#         policy_diffs.append(policy_diff[1]) # only use weighted diff
#
#         task_error = task2error(tp)
#
#         task_error = Error(
#             pitch=task_error.pitch* random.gauss(1,task_err_noise_var),
#             timing=task_error.timing* random.gauss(1,task_err_noise_var),)
#
#
#         error_pre = performer(task_error)
#         given_practice_mode = GP.get_best_practice_mode(c, tp)
#         error_post = per_after_practice(given_practice_mode, error_pre)
#         utility = error_diff_to_utility(error_pre, error_post)
#
#         utility *= random.gauss(1,utility_noise_var)
#
#         GP.add_data_point(c, tp, given_practice_mode, utility)
#
#         if print_details:
#             tqdm.write("\n")
#             tqdm.write(f"NoteRange = {tp.note_range_right}")
#             tqdm.write(f"BPM = {tp.bpm}")
#             tqdm.write(f"Suggested PracticeMode: {given_practice_mode}")
#             tqdm.write(f"Error Pre: {error_pre}")
#             tqdm.write(f"Error post: {error_post}")
#             tqdm.write(f"Utility: {utility}")
#             tqdm.write(f"Policy Diff: {policy_diff}")
#             tqdm.write("-"*32)
#
#
#     if plot:
#         GP.plot_mutiple(c, [
#
#             PracticeMode.IMP_TIMING,
#             PracticeMode.IMP_PITCH,
#             ])
#
#         plt.plot(list(range(len(policy_diffs))), policy_diffs)
#         plt.ylim((-0.01,None))
#         plt.show()
#
#     return GP, policy_diffs, kernel_params
#
# def run_all_combinations():
#     num_per_comb = 27
#     performers = ["bad_pitch", "balanced", "bad_timing"]
#     noise_vars = [0.0, 0.25, 0.5] # [0.0, 0.1] #
#     bpm_norm_facs = [100] #1
#
#     NUM_ROUNDS = 50
#
#     comb = list()
#     for performer, noise_var, bpm_norm_fac in itertools.product(performers,
#                                                                  noise_vars,
#                                                                  bpm_norm_facs):
#         comb.extend([(performer, noise_var, bpm_norm_fac)]*num_per_comb)
#
#     from multiprocessing import Pool
#     pool = Pool(2)
#
#     import functools
#     single_exp = functools.partial(single_experiment_run_tup,
#                                              num_rounds=NUM_ROUNDS)
#
#     from tqdm import tqdm
#     results = list()
#     for res in tqdm(pool.imap_unordered(single_exp, comb),
#                     total=len(comb),
#                     smoothing=0):
#     # for res in tqdm(map(single_exp, comb), # for debugging
#     #             total=len(comb),
#     #             smoothing=0):
#         results.append(res)
#
#     res_dicts = list()
#     for run_idx, ((performer, noise_var, bpm_norm_fac), diffs) in enumerate(results):
#         pre_dict = dict(run_idx=run_idx,
#                         performer=performer,
#                         noise_var=noise_var,
#                         bpm_norm_fac=bpm_norm_fac)
#         for idx, val in enumerate(diffs):
#             d = pre_dict.copy()
#             d["iteration"] = idx+1
#             d["policy_loss"] = val
#
#             res_dicts.append(d)
#
#     return res_dicts
#
#
# def single_test_run():
#     STARTING_COMPLEXITY_LEVEL = 0
#     c = STARTING_COMPLEXITY_LEVEL
#
#     performer = "bad_timing"
#     # performer = "bad_pitch"
#     # performer = "balanced"
#
#     task_err_noise_var = 0.5
#     utility_noise_var  = 0.5
#
#     TARGET_LOSS = 0.0
#
#     for idx in range(100):
#         print(str(idx).center(64, "="))
#
#         GP, policy_diffs, kernel_params = single_experiment_run(
#             num_rounds=100,
#             performer=performer,
#             task_err_noise_var=task_err_noise_var,
#             utility_noise_var=utility_noise_var,
#             bpm_norm_fac=100,
#             plot=False,
#             print_details=True)
#
#
#         if policy_diffs[-1] >= TARGET_LOSS:
#             GP.plot_mutiple(c, [
#
#                 PracticeMode.IMP_TIMING,
#                 PracticeMode.IMP_PITCH,
#                 ])
#
#             plt.plot(list(range(len(policy_diffs))), policy_diffs)
#             plt.ylim((-0.01,None))
#             plt.show()
#
#             plt.plot(list(range(len(kernel_params))), kernel_params)
#             plt.legend(["variance", "lengthscale"])
#             plt.ylim((-0.01,None))
#             plt.show()
#
#             break
#
# def run_combs_and_plot():
#     results = run_all_combinations()
#
#     import pandas as pd
#     import seaborn as sns
#     sns.set_theme(style="darkgrid")
#
#     df = pd.DataFrame.from_dict(results)
#     df = df.rename(columns={"performer": "human-learner"})
#
#     sns.relplot(
#         data=df,
#         x="iteration", y="policy_loss",
#         hue="noise_var",
#         # hue="noise_var",
#         col="human-learner",
#         kind="line",
#         ci=68,
#     )
#
#     # plt.ylim((None,0.8))
#     plt.xlim((1,50))
#     # plt.savefig("performers.png", dpi=300)

