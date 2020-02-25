"""Core functions and operations for the ccb library.
"""
import os as _os
import numpy as _np
import pandas as _pd
import glob as _glob
import numbers as _num
import subprocess as _sp
import multiprocessing as _mp
from psutil import virtual_memory as _vm


# get info on the cpu for setting memory/thread limits
_ncpu = _mp.cpu_count()
_mems = _vm().total / (1024 * 1024)


# set up a function to run external commands and return stdout/stderr
def run(cmd, stderr=True):
    """
    """
    # set whether or not stderr is included in return or just stdout
    if stderr:
        se = _sp.STDOUT
    else:
        se = None
    
    # run the command, and return stdout as a list
    try:
        proc = _sp.check_output(cmd, shell=True, stderr=se)

        # return the proc string
        return proc.split(b"\n")

    # raise an exception and print the error if the command fails    
    except _sp.CalledProcessError as e:
        output = e.output.strip()
        sp = output.find(b":") + 2
        print(output[sp:])
        return e.output.strip().split(b"\n")


# test whether a file exists
def test_file(path, file_name='file'):
    """
    """
    try:
        if _os.path.isfile(path):
            return True
        else:
            prnt.error('{} does not exist: {}'.format(file_name, path))
            return False
    except:
        prnt.error('no {} path set'.format(file_name))
        return False
        

# test whether a directory exists
def test_dir(path, directory_name='directory'):
    """
    """
    try:
        if _os.path.isdir(path):
            return True
        else:
            prnt.error('{} does not exist: {}'.format(directory_name, path))
            return False
    except:
        prnt.error('no {} path set'.format(directory_name))
        return False

# set up a class to consistently print status/errors
class prnt:
    def __init__(self):
        pass
    
    @staticmethod
    def error(message):
        if type(message) is str:
            print("[ ERROR! ]: {}".format(message))
        elif type(message) is list:
            for item in list:
                print("[ ERROR! ]: {}".format(item))
        elif isinstance(message, _num.Number):
            print("[ ERROR! ]: {}".format(message))
        else:
            pass
        
    @staticmethod
    def status(message):
        if type(message) is str:
            print("[ STATUS ]: {}".format(message))
        elif type(message) is list:
            for item in list:
                print("[ STATUS ]: {}".format(item))
        elif isinstance(message, _num.Number):
            print("[ STATUS ]: {}".format(message))
        else:
            pass

class maxent:
    def __init__(self, samples=None, env_layers=None, model_dir=None, predict_layers=None,
                 bias_file=None, test_samples=None, tau=0.5, pct_test_points=0, n_background=10000,
                 n_replicates=1, replicate_type='bootstrap', features=['hinge'], write_grids=False,
                 logfile='maxent.log', cache=True, n_threads=_ncpu-1, mem=_mems/4):
        """
        """
        
        # assign the passed values to a parameters dictionary
        self.parameters_ = {
            'samples': samples,
            'model_dir': model_dir,
            'env_layers': env_layers,
            'predict_layers': predict_layers,
            'bias_file': bias_file,
            'test_samples': test_samples,
            'pct_test_points': pct_test_points,
            'n_background': n_background,
            'n_replicates': n_replicates,
            'replicate_type': replicate_type,
            'features': features,
            'write_grids': write_grids,
            'logfile': logfile,
            'cache': cache,
            'tau': tau,
            # set a few properties for which species and layers to map
            'species_list': None,
            'all_species': True,
            'layers_list': None,
            'layers_ignore': None,
            'layers_original': None,
            # and set a bunch of misc parameters that are usually too dumb to try and set
            'response_curves': True,
            'pictures': False,
            'jackknife': False,
            'output_format': 'cumulative',
            'output_type': 'asc',
            'random_seed': False,
            'log_scale': True,
            'warnings': False,
            'tooltips': False,
            'ask_overwrite': False,
            'skip_if_exists': True,
            'remove_duplicates': True,
            'write_clamp_grid': False,
            'write_mess': False,
            'beta_multiplier': 1.0,
            'per_species_results': True,
            'write_background_predictions': True,
            'response_curve_exponent': False,
            'add_samples_to_background': False,
            'add_all_samples_to_background': False,
            'write_plot_data': True,
            'fade_by_clamping': False,
            'extrapolate': False,
            'visible': True,
            'auto_feature': False,
            'do_clamp': False,
            'plots': True,
            'append_to_results_file': False,
            'maximum_iterations': 500,
            'convergence_threshold': 1e-5,
            'adjust_sample_radius': 0,
            'n_threads': _ncpu-1,
            'mem': mem,
            'min_samples_threshold_product': 80,
            'min_samples_quadratic': 10,
            'min_samples_hinge': 12,
            'beta_threshold': -1.,
            'beta_categorical': -1.,
            'beta_lqp': -1.,
            'beta_hinge': -1.,
            'verbose': True,
            'allow_partial_data': False,
            'nodata': -9999,
            'prefixes': False,
            'path_maxent': '/ccb/maxent.jar',
            'path_java': 'java'
            }
            
        # set a variable to track whether the object has been init
        self.initialized_ = False
        
    def set_parameters(self, **kwargs):
        """
        """
        keys = kwargs.keys()
        for param in keys:
            self.parameters_[param] = kwargs[param]
            
    def get_keys(self):
        """
        """
        keys = list(self.parameters_.keys())
        keys.sort()
        return keys
        
    def get_parameters(self, *args):
        """
        """
        params = {}
        for item in args:
            params[item] = self.parameters_[item]

        return params
        
    def initialize(self, **kwargs):
        """
        """
        # get ready for just so, so many if statements.
        
        # set a flag to track progress on whether the settings are correct
        flag = True
        
        # check that the bare minimum parameters have been set
        # check the input/output paths exist
        if not test_file(self.parameters_['samples'], 'samples file'):
            flag = False
        
        if not test_dir(self.parameters_['env_layers'], 'environmental layers directory'):
            flag = False
        else:
            # if it does exist, populate the layers list
            self.parameters_['layers_original'] = self.get_layers()
            
        if not test_dir(self.parameters_['model_dir'], 'model output (model_dir)'):
            try:
                _os.makedirs(self.parameters_['model_dir'])
                prnt.status('created output directory: {}'.format(self.parameters_['model_dir']))
            except:
                flag = False
            
        if self.parameters_['bias_file'] is not None:
            if not test_file(self.parameters_['bias_file'], 'bias file'):
                flag = False
                
        if self.parameters_['test_samples'] is not None:
            if not test_file(self.parameters_['test_samples'], 'test samples'):
                flag = False
                
        if self.parameters_['predict_layers'] is not None:
            if not test_dir(self.parameters_['predict_layers'], 'prediction directory'):
                flag = False
        
        # check correct formatting for several options    
        # set options for the features to use
        features_types = ['linear', 'quadratic', 'product', 'threshold', 'hinge', 'auto']
        features_default = ['hinge']
        for feature in self.parameters_['features']:
            if feature.lower() not in features_types:
                prnt.error("incorrect feature specified: {}".format(', '.join(feature)))
                prnt.error("  must be one of: {}".format(', '.join(features_types)))
                prnt.error("  using default: {}".format(', '.join(features_default)))
                continue
            
        # set how replicates are handled
        replicate_types = ['crossvalidate', 'bootstrap', 'subsample']
        replicate_types_default = 'crossvalidate'
        replicate_type = self.parameters_['replicate_type'].lower()
        if replicate_type not in replicate_types:
            prnt.error("incorrect replicate type specified: {}".format(replicate_type))
            prnt.error("  must be one of: {}".format(', '.join(replicate_types)))
            prnt.error("  using default: {}".format(replicate_types_default))
            self.parameters_['replicate_type'] = replicate_types_default
            
        # set test percentage to an integer if a float is passed
        test_pct_default = 25
        if type(self.parameters_['pct_test_points']) is float:
            self.parameters_['pct_test_points'] = int(100 * self.parameters_['pct_test_points'])
        else:
            if type(self.parameters_['pct_test_points']) is not int:
                prnt.error("incorrect test percent specified: {}".format(self.parameters_['pct_test_points']))
                prnt.error("  must be an integer between 0-100")
                prnt.error("  using default: {}".format(test_pct_default))
                self.parameters_['pct_test_points'] = test_pct_default

        # set the format for output data reporting
        formats = ['cloglog', 'logistic', 'cumulative', 'raw']
        formats_default = 'logistic'
        if self.parameters_['output_format'].lower() not in formats:
            prnt.error("incorrect output format specified: {}".format(self.parameters_['output_format']))
            prnt.error("  must be one of: {}".format(', '.join(formats)))
            prnt.error("  using default: {}".format(formats_default))
            self.outformat = formats_default
            
        # set the output file type if writing output files
        if self.parameters_['write_grids']:
            types = ['asc', 'bil', 'grd', 'mxe']
            types_default = 'bil'
            if self.parameters_['output_type'] not in types:
                prnt.error("incorrect output data type specified: {}".format(outtype))
                prnt.error("  must be one of: {}".format(', '.join(types)))
                prnt.error("  using default: {}".format(types_default))
                self.outtype = types_default
            
        # then update with the flag - should be true if no problems arose
        self.initialized_ = True
        return flag
    
    def get_layers(self):
        """
        """
        # find the raw layers files
        bil = _glob.glob('{}/*.bil'.format(self.parameters_['env_layers']))
        asc = _glob.glob('{}/*.asc'.format(self.parameters_['env_layers']))
        grd = _glob.glob('{}/*.grd'.format(self.parameters_['env_layers']))
        mxe = _glob.glob('{}/*.mxe'.format(self.parameters_['env_layers']))
        files = bil + asc + grd + mxe
        
        # get the base name for each file
        base = [_os.path.basename(f) for f in files]
        
        # then strip the extension and return the list of layer names
        layers = [(_os.path.splitext(b))[0] for b in base]
        layers.sort()
        return layers
    
    def set_layers(self, layers):
        """
        """
        # check initialized to ensure a directory is set
        if not self.initialized_:
            if not self.initialize():
                prnt.error('cannot set layers - fix obj.initialize() errors first')
                return False
                
        # if a single layers is passed as a string, convert it to a list to support iteration
        if type(layers) is str:
            layers = [layers]
                
        # set an output list to store the set layers
        output_layers = []
        
        # get the number of layers set, total number of layers in directory
        nl = len(layers)
        na = len(self.parameters_['layers_original'])
        
        # check that the layers passed are in the list of available layers
        for lyr in layers:
            # if its a string, check its available
            if type(lyr) is str:
                if lyr in self.parameters_['layers_original']:
                    output_layers.append(lyr)
                else:
                    prnt.error('invalid layer set: {}'.format(lyr))
                
            # if its an integer, use it as an index
            if type(lyr) is int:
                output_layers.append(self.parameters_['layers_original'][lyr])
                
        # set the layers we plan to use
        self.parameters_['layers_list'] = output_layers
        
        # but more importantly for maxent, the ones we will ignore
        self.parameters_['layers_ignore'] = list(set(self.parameters_['layers_original']) - set(output_layers))
        
    def get_species(self):
        """
        """
        # check that the input file exists
        if not test_file(self.parameters_['samples'], 'samples file'):
            prnt.error('unable to get species list')
            return None
        
        # pull the unique species ids from the csv file
        df = _pd.read_csv(self.parameters_['samples'])
        sp_list = (df['species'].unique()).tolist()
        sp_list.sort()
        
        # then update the parameters to include the species list
        #self.parameters_['species_list'] = sp_list
        return sp_list
        
    def set_species(self, species):
        """
        """
        # first get the full species list
        sp_list = self.get_species()
        
        # if a string is passed, convert it to a list so it is compatible with other iterables
        if type(species) is str:
            species = [species]
        
        # then check that the species passed are in the available list of species
        sp_flag = False
        sp_set = []
        for sp in species:
            if sp not in sp_list:
                prnt.error('Unable to set species: {}'.format(sp))
            else:
                sp_set.append(sp)
                
        # return the list of available species if any were incorrectly set, otherwise update the params list
        if sp_flag:
            prnt.error('Available species include: {}'.format(', '.join(sp_list)))
        else:
            self.parameters_['all_species'] = False
            self.parameters_['species_list'] = sp_set
            
    def get_predictions(self, species, prediction_type='raw', test=False):
        """
        """
        # check that the species passed is in the available list of species
        sp_list = self.get_species()
        if not species in sp_list:
            prnt.error('Unable to get predictions for species: {}'.format(species))
            prnt.error('Available species include: {}'.format(', '.join(sp_list)))
            return None
            
        # check that the type of prediction passed is valid
        pred_list = ['cloglog', 'logistic', 'cumulative', 'raw']
        if prediction_type not in pred_list:
            prnt.error('Prediction type not supported: {}'.format(prediction_type))
            prnt.error('Available options include: {}'.format(', '.join(pred_list)))
            return None
            
        # reconcile the stupid differences in column names for prediction type
        if prediction_type == 'raw':
            sample_column = 'Raw prediction'
            backgr_column = 'raw'
        elif prediction_type == 'cumulative':
            sample_column = 'Cumulative prediction'
            backgr_column = 'cumulative'
        elif prediction_type == 'logistic':
            sample_column = 'Logistic prediction'
            backgr_column = 'Logistic'
        else:
            sample_column = 'Cloglog prediction'
            backgr_column = 'cloglog'
            
        # build the strings to the prediction file paths
        sp_join = '_'
        sample_path = '{directory}/{sp}_samplePredictions.csv'.format(
            directory=self.parameters_['model_dir'], sp=sp_join.join(species.split()))
        backgr_path = '{directory}/{sp}_backgroundPredictions.csv'.format(
            directory=self.parameters_['model_dir'], sp=sp_join.join(species.split()))
        
        # test that these files exist
        sample_exists = test_file(sample_path, 'sample predictions file')
        backgr_exists = test_file(backgr_path, 'background precitions file')
        
        # if neither of them are there, don't return shit
        if not (sample_exists or backgr_exists):
            prnt.error('Unable to get predictions')
            return None
        
        # otherwise, read the data that do exist
        if sample_exists:
            df = _pd.read_csv(sample_path)
            
            # remove nodata values
            good_vals = _np.invert(df[sample_column].isnull())
            df = df[good_vals]
            
            # subset the test data if set
            if test:
                # check if test values are in the data
                try:
                    if len(df[df['Test or train'] == 'test']) > 0:
                        df = df[df['Test or train'] == 'test']
                except:
                    prnt.error('Unable to subset test data')
            
            # set the output array size
            nl = len(df)
            
            # then get arrays for the sample predictions
            y_true = _np.ones(nl)
            y_pred = _np.array(df[sample_column])
            
        if backgr_exists:
            df = _pd.read_csv(backgr_path)
            
            # remoe nodata values
            good_vals = _np.invert(df[backgr_column].isnull())
            df = df[good_vals]
            nl = len(df)
            
            # append these to the existing arrays if sample predictions already exist
            if sample_exists:
                y_true = _np.append(y_true, _np.zeros(nl))
                y_pred = _np.append(y_pred, _np.array(df[backgr_column]))
            else:
                y_true = _np.zeros(nl)
                y_pred = _np.array(df[backgr_column])
                
        return [y_true, y_pred]
        
    def build_cmd(self):
        """
        """
        # first, check whether the options have been parsed through the initializer
        if not self.initialize():
            prnt.error("unable to build cmd string. update your parameters then re-run object.initialize()")
            return False
            
        # then get ready for just a stupid number of if statements
        s = []
        join = ' '
        sp_join = '_'
        
        # set the strings for running maxent command
        s.append(self.parameters_['path_java'])
        
        # don't explicitly set memory -- it breaks headless model runs
        #s.append('-mx{}m'.format(self.parameters_['mem']))
        s.append('-jar')
        s.append(self.parameters_['path_maxent'])

        # set it to autorun
        s.append('-a')
        
        # set the environmental layers
        s.append('-e')
        s.append(self.parameters_['env_layers'])
        
        # call out which layers will not be used, if set
        if self.parameters_['layers_ignore'] is not None:
            for layer in self.parameters_['layers_ignore']:
                s.append('-N')
                s.append(layer)
        
        # set the samples CSV
        s.append('-s')
        s.append(self.parameters_['samples'])
        
        # call out which species will be mapped if not all
        if not self.parameters_['all_species']:
            for sp in self.parameters_['species_list']:
                s.append('-E')
                split = sp.split()
                s.append(sp_join.join(split))
                
        # set the output directory
        s.append('-o')
        s.append(self.parameters_['model_dir'])
        
        # set the optional bias/test/prediction data
        if self.parameters_['bias_file'] is not None:
            s.append('biasfile={}'.format(self.parameters_['bias_file']))
        if self.parameters_['predict_layers'] is not None:
            s.append('-j')
            s.append(self.parameters_['predict_layers'])
        
        # set how test data are handled
        if self.parameters_['test_samples'] is not None:
            s.append('-T')
            s.append(self.parameters_['test_samples'])
        elif self.parameters_['pct_test_points'] != 0:
            s.append('-X')
            s.append('{:d}'.format(self.parameters_['pct_test_points']))
            
        # set background and replicate data
        s.append('maximumbackground={}'.format(self.parameters_['n_background']))
        if self.parameters_['n_replicates'] > 1:
            s.append('replicates={}'.format(self.parameters_['n_replicates']))
            s.append('replicatetype={}'.format(self.parameters_['replicate_type']))
        
        # set options for writing grid data
        if self.parameters_['write_grids']:
            s.append('outputfiletype={}'.format(self.parameters_['output_type']))
        else:
            s.append('-x')
        
        # set the output model prediction format
        s.append('outputformat={}'.format(self.parameters_['output_format']))
        
        # add the tau value in logistic/cloglog predictions
        if self.parameters_['output_format'] in ['logistic', 'cloglog']:
            s.append('defaultprevalence={}'.format(self.parameters_['tau']))
        
        # set nodata value
        if self.parameters_['nodata'] is not None:
            s.append('-n')
            s.append('{}'.format(self.parameters_['nodata']))
        
        # set a bunch of boolean features based on their default on/off settings
        #  (i.e., only turn on params that are default off, only turn off params that
        #  are default on)
        
        if self.parameters_['response_curves']:
            s.append('responsecurves')
            
        if not self.parameters_['pictures']:
            s.append('nopictures')
            
            if not self.parameters_['log_scale']:
                s.append('nologscale')
            
        if self.parameters_['jackknife']:
            s.append('jackknife')
            
        if self.parameters_['random_seed']:
            s.append('randomseed')
            
        if not self.parameters_['ask_overwrite']:
            s.append('noaskoverwrite')
        
        if self.parameters_['skip_if_exists']:
            s.append('-S')
            
        if not self.parameters_['remove_duplicates']:
            s.append('noremoveduplicates')
            
        if not self.parameters_['write_clamp_grid']:
            s.append('nowriteclampgrid')
            
        if not self.parameters_['write_mess']:
            s.append('nowritemess')
            
        if self.parameters_['per_species_results']:
            s.append('perspeciesresults')
            
        if self.parameters_['write_background_predictions']:
            s.append('writebackgroundpredictions')
            
        if self.parameters_['response_curve_exponent']:
            s.append('responsecurvesexponent')
            
        if not self.parameters_['add_samples_to_background']:
            s.append('noaddsamplestobackground')
        
        if not self.parameters_['add_all_samples_to_background']:
            s.append('noaddallsamplestobackground')
            
        if self.parameters_['fade_by_clamping']:
            s.append('fadebyclamping')
            
        if not self.parameters_['extrapolate']:
            s.append('noextrapolate')
            
        if not self.parameters_['do_clamp']:
            s.append('nodoclamp')
            
        if not self.parameters_['plots']:
            s.append('noplots')
        else:
            if self.parameters_['write_plot_data']:
                s.append('writeplotdata')
        
        if self.parameters_['append_to_results_file']:
            s.append('appendtoresultsfile')
            
        if self.parameters_['allow_partial_data']:
            s.append('allowpartialdata')
            
        if not self.parameters_['prefixes']:
            s.append('noprefixes')
            
        # set the features to calculate
        if 'auto' in self.parameters_['features']:
            s.append('autofeature')
        else:
            for feature in self.parameters_['features']:
                s.append(feature)
        
        # set a bunch of feature-specific parameters
        if not 'auto' in self.parameters_['features']:
            
            s.append('noautofeature')
            
            if not 'linear' in self.parameters_['features']:
                s.append('nolinear')
                
            if 'quadratic' in self.parameters_['features']:
                s.append('l2lqthreshold={}'.format(self.parameters_['min_samples_quadratic']))
            else:
                s.append('noquadratic')
                
            if 'product' in self.parameters_['features']:
                s.append('lq2lqptthreshold={}'.format(self.parameters_['min_samples_threshold_product']))
                s.append('beta_lqp={}'.format(self.parameters_['beta_lqp']))
            else:
                s.append('noproduct')
                
            if 'threshold' in self.parameters_['features']:
                s.append('l2qlpthreshold={}'.format(self.parameters_['min_samples_threshold_product']))
                s.append('beta_threshold={}'.format(self.parameters_['beta_threshold']))
            else:
                s.append('nothreshold')
                
            if 'hinge' in self.parameters_['features']:
                s.append('hingethreshold={}'.format(self.parameters_['min_samples_hinge']))
                s.append('beta_hinge={}'.format(self.parameters_['beta_hinge']))
            else:
                s.append('nohinge')
                
        # set the beta scalar
        s.append('-b')
        s.append('{}'.format(self.parameters_['beta_multiplier']))
        
        # ok, finally done, set basic operational stuff and gtfo 
        
        # set the logfile
        s.append('logfile={}'.format(self.parameters_['logfile']))
        
        # and turn off the GUI and warnings
        s.append('nowarnings')
        s.append('notooltips')
        if not self.parameters_['visible']:
            s.append('novisible')
        
        # return the concatenated string
        return join.join(s)
        
    def fit(self):
        """
        """
        # fist build the string to create the output command
        cmd = self.build_cmd()
        
        # then run the dang thing
        if type(cmd) is str:
            prnt.status('starting maxent run')
            prnt.status('  samples: {}'.format(self.parameters_['samples']))
            prnt.status('  outputs: {}'.format(self.parameters_['model_dir']))
            
            run(cmd)
        
        # if the build_cmd failed, send nothin' back    
        else:
            return None