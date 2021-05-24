import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sim_utils.model import Model


class Replicator:
    """
    run_scenarios:
        For each scenario:
            -> run_trial (creates 'trial_output')
                -> single run (creates dictionary of results for each single run)
            -> unpack_trial_results (collates run results for each result type)
        pivot_results

    """

    def __init__(self, scenarios, replications):
        """Constructor class for Replicator
        """

        self.replications = replications
        self.scenarios = scenarios

        # Set up DataFrames for all trials results
        self.summary_global = pd.DataFrame()
        self.summary_occupancy = pd.DataFrame()
        self.summary_occupancy_percent = pd.DataFrame()
        self.summary_unit_occupancy_displaced_preferred = pd.DataFrame()
        self.summary_unit_occupancy_displaced_destination = pd.DataFrame()
        self.summary_unit_occupancy_preferred_waiting = pd.DataFrame()
        self.summary_unit_admissions = pd.DataFrame()

        # Set up pivot tables
        self.global_pivot = None
        self.occupancy_pivot = None
        self.occupancy_percent_pivot = None
        self.occupancy_displaced_preferred_pivot = None
        self.occupancy_displaced_destination_preferred_pivot = None
        self.occupancy_waiting_preferred_pivot = None

        # Set up variables for table keys
        self.global_keys = None
        self.occupancy_keys = None


    def pivot_results(self):
        """Summarise results across multiple scenario replicates. """

        def percentile_95(g):
            """Function for percentiles in pandas pivot table"""
            return np.percentile(g, 95)

        # Global results summary (summarises across all runs)
        df = self.summary_global.copy()
        df['result_type'] = df.index

        pivot = df.pivot_table(
            index = ['name'],
            values = self.global_keys,
            aggfunc = [np.min, np.mean, np.median, np.max, percentile_95],
            margins = False)

        pivot.rename(columns={'amin': 'min', 'amax': 'max'}, inplace=True)
        self.global_pivot = pivot.T

        # Occupancy summary (summarises across all runs)

        df = self.summary_occupancy.copy()
        df['result_type'] = df.index

        pivot = df.pivot_table(
            index = ['name'],
            values = self.occupancy_keys,
            aggfunc = [np.min, np.mean, np.median, np.max, percentile_95],
            margins = False)

        pivot.rename(columns={'amin': 'min', 'amax': 'max'}, inplace=True)
        self.occupancy_pivot = pivot.T

        # Occupancy percent summary (summarises across all runs)

        df = self.summary_occupancy_percent.copy()
        df['result_type'] = df.index

        pivot = df.pivot_table(
            index = ['name'],
            values = self.occupancy_keys,
            aggfunc = [np.min, np.mean, np.median, np.max, percentile_95],
            margins = False)

        pivot.rename(columns={'amin': 'min', 'amax': 'max'}, inplace=True)
        self.occupancy_percent_pivot = pivot.T

        # Occupancy displaced preferred unit summary (summarises across all runs)

        df = self.summary_unit_occupancy_displaced_preferred.copy()
        df['result_type'] = df.index

        pivot = df.pivot_table(
            index = ['name'],
            values = self.occupancy_keys,
            aggfunc = [np.min, np.mean, np.median, np.max, percentile_95],
            margins = False)

        pivot.rename(columns={'amin': 'min', 'amax': 'max'}, inplace=True)
        self.occupancy_displaced_preferred_pivot = pivot.T

        # Occupancy displaced destination unit summary (summarises across all runs)

        df = self.summary_unit_occupancy_displaced_destination.copy()
        df['result_type'] = df.index

        pivot = df.pivot_table(
            index = ['name'],
            values = self.occupancy_keys,
            aggfunc = [np.min, np.mean, np.median, np.max, percentile_95],
            margins = False)

        pivot.rename(columns={'amin': 'min', 'amax': 'max'}, inplace=True)
        self.occupancy_displaced_destination_pivot = pivot.T

        # Occupancy displaced preferred unit summary (summarises across all runs)

        df = self.summary_unit_occupancy_preferred_waiting.copy()
        df['result_type'] = df.index

        pivot = df.pivot_table(
            index = ['name'],
            values = self.occupancy_keys,
            aggfunc = [np.min, np.mean, np.median, np.max, percentile_95],
            margins = False)

        pivot.rename(columns={'amin': 'min', 'amax': 'max'}, inplace=True)
        self.occupancy_waiting_preferred_pivot = pivot.T

        # Unit admissions
        self.summary_unit_admissions_pivot = self.summary_unit_admissions.describe().T

    def print_results(self):

        pd.set_option('display.max_rows', None)
        pd.options.display.float_format = '{:,.1f}'.format

        # Global values
        print('\nGlobal results (mean)')
        print('---------------------')
        fields = ['total_patients', 'total_patients_asu', 'total_patients_displaced',
                  'total_patients_waited']
        print(self.global_pivot.loc['max'].loc[fields])

        # Unit admissions
        print('\nUnit admissions')
        print('------------------')
        print(self.summary_unit_admissions_pivot['mean'])

        # Unit occupancy
        print('\nUnit occupancy')
        print('-----------------')
        print(self.occupancy_pivot.loc['mean'])

        print('\nUnit occupancy(%)')
        print('-----------------')
        print(self.occupancy_percent_pivot.loc['mean'])

    def run_scenarios(self):
        
        # Run all scenarios
        scenario_count = len(self.scenarios)
        counter = 0
        for name, scenario in self.scenarios.items():
            counter += 1
            print(
                f'\r>> Running scenario {counter} of {scenario_count}', end='')
            scenario_output = self.run_trial(scenario)
            self.unpack_trial_results(name, scenario_output)
        
        # Clear progress output
        clear_line = '\r' + " " * 79
        print(clear_line, end = '')

        # Pivot results
        self.pivot_results()

        # Print results
        self.print_results()

        # save results
        self.save_results()
    
    def run_trial(self, scenario):
        trial_output = Parallel(n_jobs=-1)(delayed(self.single_run)(scenario, i) 
                for i in range(self.replications))
        
        return trial_output
        
    
    def save_results(self):
        
        self.global_pivot.to_csv('./output/global_pivot.csv')
        self.summary_global.to_csv('./output/global_trial.csv')

        self.occupancy_pivot.to_csv('./output/occupancy_pivot.csv')
        self.summary_occupancy.to_csv('./output/occupancy_trial.csv')

        self.occupancy_percent_pivot.to_csv('./output/occupancy_percent_pivot.csv')
        self.summary_occupancy_percent.to_csv('./output/occupancy_percent_trial.csv')

        self.occupancy_displaced_preferred_pivot.to_csv(
            './output/displaced_preferred_pivot.csv')
        self.summary_unit_occupancy_displaced_preferred.to_csv(
            './output/displaced_preferred_trial.csv')

        self.occupancy_displaced_destination_pivot.to_csv(
            './output/displaced_destination_pivot.csv')
        self.summary_unit_occupancy_displaced_destination.to_csv(
            './output/displaced_destination_trial.csv')

        self.occupancy_waiting_preferred_pivot.to_csv('./output/waiting_preferred_pivot.csv')
        self.summary_unit_occupancy_preferred_waiting.to_csv('./output/waiting_preferred_trial.csv')

        self.summary_unit_admissions_pivot.to_csv('./output/unit_admissions.csv')
    
    
    def single_run(self, scenario, i=0):
        print(f'{i}, ', end='' )
        model = Model(scenario)
        model.run()
        
        # Put results in a dictionary
        results = {
            'global': model.global_audit,
            'occupancy': model.occupancy_audit,
            'occupancy_percent': model.occupancy_percent_audit,
            'occupancy_displaced_preferred': model.unit_occupancy_displaced_preferred_audit,
            'occupancy_displaced_destination': model.unit_occupancy_displaced_destination_audit,
            'occupancy_waiting_preferred': model.unit_occupancy_waiting_preferred_audit,
            'unit_admissions': model.admissions_by_unit
                   }

        return results
        


    def unpack_trial_results(self, name, results):
        

        for run in range(self.replications):
            
            # Global summary
            result_item = results[run]['global']
            if run == 0:
                self.global_keys = list(result_item)
                self.global_keys.remove('index')
                self.global_keys.remove('time')
            result_item['run'] = run
            result_item['name'] = name
            self.summary_global = self.summary_global.append(result_item)

            # Occupancy summaries
            result_item = results[run]['occupancy']
            if run == 0:
                self.occupancy_keys = list(result_item)
            result_item['run'] = run
            result_item['name'] = name
            self.summary_occupancy = self.summary_occupancy.append(result_item)

            result_item = results[run]['occupancy_percent']
            if run == 0:
                self.occupancy_keys = list(result_item)
            result_item['run'] = run
            result_item['name'] = name
            self.summary_occupancy_percent = self.summary_occupancy_percent.append(result_item)

            result_item = results[run]['occupancy_displaced_preferred']
            result_item['run'] = run
            result_item['name'] = name
            self.summary_unit_occupancy_displaced_preferred = \
                self.summary_unit_occupancy_displaced_preferred.append(result_item)

            result_item = results[run]['occupancy_displaced_destination']
            result_item['run'] = run
            result_item['name'] = name
            self.summary_unit_occupancy_displaced_destination = \
                self.summary_unit_occupancy_displaced_destination.append(result_item)

            result_item = results[run]['occupancy_waiting_preferred']
            result_item['run'] = run
            result_item['name'] = name
            self.summary_unit_occupancy_preferred_waiting = \
                self.summary_unit_occupancy_preferred_waiting.append(result_item)

            # Admissions
            result_item = results[run]['unit_admissions']
            if run == 0:
                self.unit_admissions_keys = list(result_item.index)
            self.summary_unit_admissions = self.summary_unit_admissions.append(
                result_item, ignore_index=True)
