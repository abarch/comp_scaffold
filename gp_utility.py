import enum
import random
import numpy as np

import GPy
import GPyOpt
from GPyOpt.methods import BayesianOptimization


class PracticeMode(enum.Enum):
    """
    All possible practice modes
    """
    IMP_PITCH = 0
    IMP_TIMING = 1
    LEFT = 2
    RIGHT = 3


# interval of possible bpm_values
BPM_BOUNDS = [50, 200]
class GaussianProcess:
    def __init__(self, bpm_norm_fac=100):
        self.data_X = None
        self.data_X_old_shape = None

        self.data_Y = None

        self.bpm_norm_fac = bpm_norm_fac

        self.domain = [
            {'name': 'practice_mode', 'type': 'categorical', 'domain': (0, 1, 2, 3)},
            {'name': 'bpm', 'type': 'continuous', 'domain':
                (self._norm_bpm(BPM_BOUNDS[0]), self._norm_bpm(BPM_BOUNDS[1]))},
            #{'name': 'error_pitch_left', 'type': 'continuous', 'domain': (0, 1)},
            {'name': 'error_pitch_right', 'type': 'continuous', 'domain': (0, 1)},
            #{'name': 'error_timing_left', 'type': 'continuous', 'domain': (0, 1)},
            {'name': 'error_timing_right', 'type': 'continuous', 'domain': (0, 1)}
        ]

        self.space = GPyOpt.core.task.space.Design_space(self.domain)
        self.kernel = None
        self.bayes_opt = None

    def _norm_bpm(self, v: float) -> float:
        
        return v / self.bpm_norm_fac

    def _params2domain(self, error, bpm: int, practice_mode: PracticeMode):
        domain_x = [
            practice_mode.value,
            self._norm_bpm(bpm),
            #error['pitch_left'],
            error['pitch_right'],
            #error['timing_left'],
            error['timing_right']
        ]

        return np.array([domain_x])

    def _domain2space(self, domain_x):
        # Converts the domain variables into the GPs input space
        space_rep = self.space.unzip_inputs(domain_x) 
        
        return space_rep 

    def _get_bayes_opt(self) -> BayesianOptimization:
        return self.bayes_opt

    def update_model(self):
       
        """
        If the Gaussian Process' training data has changed, "trains" the GP on the complete data set.
        """
        if self.data_X is None or self.data_X.shape == self.data_X_old_shape:
            return

        self.data_X_old_shape = self.data_X.shape

       
        self.bayes_opt = GPyOpt.methods.BayesianOptimization(
            f=None, domain=self.domain, X=self.data_X, Y=self.data_Y,
            maximize=True, normalize_Y=True,
            kernel=self.kernel
        )
        
        #print ("variance pre update", self.bayes_opt.model.model.kern.variance) 

        #print ("model parameters of the BO ",   self.bayes_opt.model.model.kern.parameters)
        # ASYA: this place needs to be changed
        self.bayes_opt.model.max_iters = 5
        
        # print ("model parameters of the BO",  self.bayes_opt.model.kernel)   
        self.bayes_opt._update_model()
        #self.bayes_opt.run_optimization()
        #print ("model parameters of the BO after",   self.bayes_opt.model.model.kern.parameters)
                   
        #print ("variance post update", self.bayes_opt.model.model.kern.variance) 

        #self.bayes_opt.model.max_iters = 30
        #self.bayes_opt._update_model()
        #print (self.bayes_opt.X)
        #print ("variance after iteration ", self.bayes_opt.model.model.kern.variance, self.bayes_opt.model.model.kern.lengthscale) 

    def get_estimate(self, error, bpm, practice_mode: PracticeMode) -> float:
        """
        Estimates the utility value for a given practice mode
        @param error: error values
        @param bpm: bpm of the music piece
        @param practice_mode: the practice mode for which the utility value should be estimated
        @return: gaussian process' estimate of the utility value
        """
        if not hasattr(self, "bayes_opt"):
            # if there is no model yet, e.g. in the first iteration return random utility
            return random.random()

        bayes_opt = self._get_bayes_opt()

        x = self._params2domain(error, bpm, practice_mode)
        x = self._domain2space(x)

        mean, var = bayes_opt.model.predict(x)
        

        return mean[0]

    def get_best_practice_mode(self, error, bpm, epsilon=0):
        """
        computes the gaussian process' estimate of the best practice mode
        currently utilizes epsilon-greedy exploration
        @param error: error values
        @param bpm: bpm of the music piece
        @param (optional) epsilon: the probability of making a random decision. set to 0 for no exploration.
        @return: chosen for given input parameters PracticeMode
        """
        left = False
        right = True
        if left and right:
            all_practice_modes = list(PracticeMode)
        else:
            all_practice_modes = [PracticeMode.IMP_PITCH, PracticeMode.IMP_TIMING]
        # epsilon-greedy
        if random.random() > epsilon:
            max_i = np.argmax([self.get_estimate(error, bpm, pm)
                               for pm in all_practice_modes])
            return all_practice_modes[max_i]
        else:
            return np.random.choice(all_practice_modes)

    def add_data_point(self, error, bpm: int, practice_mode: PracticeMode,
                       utility_measurement: float):
        """
        Adds a new datapoint to the dataset of the gaussian process.
        Does not update the Gaussian Process for the new training data (see: update_model)
        @param error: error values
        @param bpm: bpm of the music piece
        @param practice_mode: practice mode in which the performer practiced
        @param utility_measurement: observed utility value for the given parameters
        """

        new_x = self._params2domain(error, bpm, practice_mode)
        new_y = [utility_measurement]

        if self.data_X is None:
            self.data_X = new_x
            self.data_Y = np.array([new_y])
        else:
            self.data_X = np.vstack((self.data_X, new_x[0]))
            self.data_Y = np.vstack((self.data_Y, new_y[0]))
        
    def update_model_with_kernel(self, kernel):
        self.kernel = kernel
    #update a new model with a given kernel

        ## only calculate new model if data changed
        #if self.data_X is None or self.data_X.shape == self.data_X_old_shape:
        #    return
        
        
        #self.data_X_old_shape = self.data_X.shape
        
        
        
        #self.bayes_opt = GPyOpt.methods.BayesianOptimization(
        #    f = None, domain = self.domain, X = self.data_X, Y = self.data_Y,
        #    maximize=True,
        #    kernel=kernel,
        #)
        
        #self.bayes_opt.model.max_iters = 0
        #self.bayes_opt.update_model_with_kernel(kernel) 
        
        # ASYA - comment out
        #self.bayes_opt.model.model.kern.variance.constrain_bounded(0.2,1,
        #                                                           warning=False)
        #self.bayes_opt.model.model.kern.lengthscale.constrain_bounded(1, 2,
        #                                                           warning=False)
        
        #self.bayes_opt.model.max_iters = 1000
        #self.bayes_opt.update_model_with_kernel(kernel) 
        
   
    
    def compare_to_best_policy(self, policy_argmax, best_argmax, best_error_diff=1):
            num_diff_cases = np.sum(np.abs(policy_argmax-best_argmax))
    
            abs_diff = num_diff_cases / policy_argmax.shape[0]

    
            return abs_diff


        # Different functions used to deliver a utility value to the plot_utility function -------------------------------------

    # returns the utility estimate of a gaussian process for a specific practice mode
    def _utility_gp(self, bpm, practice_mode, error_pre):
        return self.get_estimate(error_pre, bpm, practice_mode)

    # wrapper function to abstract arguments gaussian process and practice mode
    def utility_gp(self, bpm, practice_mode):
        return lambda error_pre: self._utility_gp(bpm, practice_mode, error_pre)[0]

    def plot_utility(self, utility_function, density=50, title="Utility", data_points=None):
        plot_data = []
        for i, error_pitch in enumerate(np.linspace(0, 1, density)):
            for j, error_timing in enumerate(np.linspace(0, 1, density)):
                error_pre = {
                    #'pitch_left': 0,
                    'pitch_right': error_pitch,
                    #'timing_left': 0,
                    'timing_right': error_timing
                }
                utility = utility_function(error_pre)

                plot_data.append([error_pitch, error_timing, utility])

        plot_data = np.array(plot_data)

        fig = plt.figure(figsize=(10, 7))
        ax = plt.axes(projection="3d")

        ax.scatter3D(plot_data[:, 0], plot_data[:, 1], plot_data[:, 2], s=8)

        if data_points is not None:
            ax.scatter3D(data_points[:, 0], data_points[:, 1], data_points[:, 2], color="red", alpha=0.6)

        ax.set_title(title)
        ax.set_xlabel('error_pitch')
        ax.set_ylabel('error_timing')
        ax.set_zlabel('utility')
        ax.set_zlim(-100, 100)

        plt.show()

def policy_test(gauss_model, test_points):
    #calculate the policy diff for a single gp, given the recorded points and the expert decision
    policy_diff = []
    practice_mode_map = {'IMP_PITCH': PracticeMode.IMP_PITCH, 'IMP_TIMING': PracticeMode.IMP_TIMING}
    #for all recorded data points
    #recorded_points = calc_utility(test_points, a, mean_utility)
    points =[]
    for i, point in  test_points.iterrows():  # recorded_points.iterrows():


        #point_data = point.drop("utility")
        #expert_opt_policy = point["utility"]
        bpm=point["bpm"]
        given_practice_mode = point["practice_mode"]
        expert_practice_mode = practice_mode_map[given_practice_mode]
        
        if expert_practice_mode == PracticeMode.IMP_PITCH:
            wrong_practice_mode = PracticeMode.IMP_TIMING
        else:
           wrong_practice_mode = PracticeMode.IMP_PITCH
       
        errors = {
       # 'pitch_left': point_data['error_before_left_pitch'],
        'pitch_right': point['error_before_right_pitch'],
       # 'timing_left': point_data['error_before_left_timing'],
        'timing_right': point['error_before_right_timing']}

 
        best_estimated = gauss_model.get_best_practice_mode(errors, bpm)
        points.append ((errors, bpm,  expert_practice_mode, wrong_practice_mode, best_estimated)) 
        
    
    right_utility = 0
    wrong_utility = 0
    for point in points:
        errors, bpm, expert_practice_mode, wrong_practice_mode, best_estimated = point 
        #print ("expert practice mode:", expert_practice_mode,  "best practice mode ", best_estimated)

        if best_estimated == expert_practice_mode:
            right_utility += 1.0
        else:
            wrong_utility += 1.0
    print ("accumulated correct=", right_utility,  "wrong =" ,wrong_utility, "ratio=", right_utility/(right_utility+wrong_utility))
    return wrong_utility/right_utility

def policy_add_test(gauss_model, test_points,a,  mean_utility):
    #calculate the policy diff for a single gp, given the recorded points and the expert decision
    # 1) step: add data points to the gauss process 
    policy_diff = []
    practice_mode_map = {'IMP_PITCH': PracticeMode.IMP_PITCH, 'IMP_TIMING': PracticeMode.IMP_TIMING}
    #for all recorded data points
    recorded_points = calc_utility(test_points, a,  mean_utility)
    points =[]
    for i, point in recorded_points.iterrows():
        point_data = point.drop("utility")
        expert_opt_policy = point["utility"]
        bpm=point["bpm"]
        given_practice_mode = point["practice_mode"]
        expert_practice_mode = practice_mode_map[given_practice_mode]
        
        if expert_practice_mode == PracticeMode.IMP_PITCH:
            wrong_practice_mode = PracticeMode.IMP_TIMING
        else:
           wrong_practice_mode = PracticeMode.IMP_PITCH
       
        errors = {
        #'pitch_left': point_data['error_before_left_pitch'],
        'pitch_right': point_data['error_before_right_pitch'],
        #'timing_left': point_data['error_before_left_timing'],
        'timing_right': point_data['error_before_right_timing']}
        gauss_model.add_data_point(errors ,bpm, expert_practice_mode, expert_opt_policy)
        
    gauss_model.update_model()
    
    # estimate the quality of prediction

    for i, point in recorded_points.iterrows():


        point_data = point.drop("utility")
        expert_opt_policy = point["utility"]
        bpm=point["bpm"]
        given_practice_mode = point["practice_mode"]
        expert_practice_mode = practice_mode_map[given_practice_mode]
        
        if expert_practice_mode == PracticeMode.IMP_PITCH:
            wrong_practice_mode = PracticeMode.IMP_TIMING
        else:
           wrong_practice_mode = PracticeMode.IMP_PITCH
       
        errors = {
       # 'pitch_left': point_data['error_before_left_pitch'],
        'pitch_right': point_data['error_before_right_pitch'],
       # 'timing_left': point_data['error_before_left_timing'],
        'timing_right': point_data['error_before_right_timing']}

 
        best_estimated = gauss_model.get_best_practice_mode(errors, bpm)
        points.append ((errors, bpm,  expert_practice_mode, wrong_practice_mode, best_estimated)) 
        
    
    right_utility = 0
    wrong_utility = 0
    for point in points:
        errors, bpm, expert_practice_mode, wrong_practice_mode, best_estimated = point 
        #print ("expert practice mode:", expert_practice_mode,  "best practice mode ", best_estimated)
        r= gauss_model.get_estimate(errors,bpm, expert_practice_mode)
        w= gauss_model.get_estimate(errors,bpm, wrong_practice_mode)
        diff = abs (r-w)
        
        if best_estimated == expert_practice_mode:
            right_utility += diff # maximize
            
        else:
            wrong_utility += diff # penalize 
            
    print ("accumulated correct=", right_utility,  "wrong =" ,wrong_utility)
    return (1/right_utility) + 0.1 *wrong_utility
    # the further the correct from the wrong the wrose. 
    #wrong_utility/right_utility

def calc_utility(recorded_points,a,  mean_utility):
    #calc utility for all expert data
    recorded_points["utility"] = recorded_points.apply(lambda row: error_diff_to_utility_for_opt(row["error_before_right_pitch"],
                                                                                row["error_after_right_pitch"],
                                                                                row["error_before_right_timing"],
                                                                                row["error_after_right_timing"],a, mean_utility), axis=1)
    return recorded_points  

def error_diff_to_utility_for_opt(error_pre_pitch, error_post_pitch, error_pre_timing, error_post_timing, a, MEAN_UTILITY):
    #calculate the difference in both errors between the pre and post error
    #calculate the utility of the difference in errors
    diff_timing = error_post_timing - error_pre_timing
    diff_pitch  = error_post_pitch  - error_pre_pitch
    return -diff_timing*a  -diff_pitch*(1-a)  - MEAN_UTILITY

def objective_function(x, kernel_type):
    #objective function for the optimization of the hyperparameters, getting the mean policy diff for the current hyperparameters
    if x.ndim > 1:
        x = x.flatten()
        
    # x is a list of hyperparameters
    a, mean_utility = x
    print (a, mean_utility)
    # Initialize a GP model with the given hyperparameters and kernel type
    # per calculation of the objective function we calculate the whole prediction of the gaussian process and compare it to the ground truth data. 
    gp = GaussianProcess()
    
    #gp.space.model_dimensionality
    if kernel_type == 'Matern52':
        kernel = GPy.kern.Matern52(input_dim=gp.space.model_dimensionality, ARD=True)
    elif kernel_type == 'RBF':
        kernel = GPy.kern.RBF(input_dim=gp.space.model_dimensionality, ARD=True)
    elif kernel_type == 'RatQuad':
        kernel = GPy.kern.RatQuad(input_dim=gp.space.model_dimensionality, ARD=True)
    elif kernel_type == 'Poly':
        kernel = GPy.kern.Poly(input_dim=gp.space.model_dimensionality, degree=1, variance=1.0, scale=1.0, offset=0.0, ARD=True)
    elif kernel_type == 'Exp':
        kernel = GPy.kern.Exponential(input_dim=gp.space.model_dimensionality, ARD=True)
    else:
        raise ValueError("Invalid kernel type")

    gp.update_model_with_kernel(kernel)

    # Calculate the utility using the expert data and the GP model
    recorded_points =  expert_data [[  #'error_before_left_timing',
     'error_before_right_timing',
       #'error_before_left_pitch', 
       'error_before_right_pitch',
       #'error_after_left_timing', 
        'error_after_right_timing',
       #'error_after_left_pitch', 
       'error_after_right_pitch', "practice_mode", "bpm"]]
    # policy_diff = policy_diff_for_single_gp(gp, recorded_points,a,mean_utility)
    #policy_diff_list.append(-policy_diff)
    #return -policy_diff

    policy_diff= policy_add_test(gp,recorded_points,a, mean_utility) #policy_diff_for_single_gp(gp, recorded_points,a, mean_utility)
    gp_list.append(gp)
    policy_diff_list.append(policy_diff)
    #plot_best_policy(gp, 70)
    return policy_diff