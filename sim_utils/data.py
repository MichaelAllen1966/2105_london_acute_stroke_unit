import numpy as np
import pandas as pd


class Data(object):
    """
    
    methods
    -------
    __init__:
        Data constructor method
    load_data:
        Loads data
    order_by_time:
        Create a dataframe of units sorted by travel time for each LSOA
    
    attributes
    ----------
    admissions(DataFrame):
        Admissions by LSOA
    distance_matrix (DataFrame):
        Travel distance from LSOA to all stroke units
    time_matrix (DataFrame):
        Travel time from LSOA to all stroke units (estimated road travel time,
        clear road conditions)
    units (DataFrame):
        Information on stroke units (including mean length of stay)
    
    """

    def __init__(self):
        """Data constructor method"""

        # Load data
        self.admissions = pd.read_csv('data/admissions.csv', index_col='LSOA')
        self.pref_unit = pd.read_csv('data/pref_unit.csv', index_col='LSOA')
        self.units = pd.read_csv('data/hospitals.csv', index_col='Unit')
        self.time_matrix = pd.read_csv('data/time.csv', index_col='LSOA')
        self.distance_matrix = pd.read_csv('data/distance.csv',
                                           index_col='LSOA')

        # Add jitter to time matrix to randomise choice of units with same time
        jitter = np.random.random(self.time_matrix.shape) * 0.1
        self.time_matrix += jitter

        # Get list of used units and restrict data to used units
        mask = self.units['Use'] == 1
        used_unit_postcodes = list(self.units.loc[mask].Postcode)
        self.units = \
            self.units[self.units['Postcode'].isin(used_unit_postcodes)]
        self.time_matrix = self.time_matrix[used_unit_postcodes]
        self.distance_matrix = self.distance_matrix[used_unit_postcodes]

        # Add index to units
        number_of_units = self.units.shape[0]
        self.units['Index'] = range(number_of_units)

        # Create lists of information from units DataFrame
        self.units_index = list(self.units['Index'])
        self.units_name =  list(self.units.index)
        self.units_postcode = list(self.units['Postcode'])
        self.units_capacity = list(self.units['Capacity'])

        # Get preferred units by travel time from LSOAs to unit
        self.units_by_time = self.order_by_time(self.time_matrix)
        self.units_index_by_time = self.convert_unit_postocde_to_index()
        # Calculate admissions and probabilities by LSOA
        self.lsoa_count = self.admissions.shape[0]
        self.lsoa_list = list(self.admissions.index)
        self.total_admissions = self.admissions['admissions'].sum()
        self.interarrival_interval = 365 / self.total_admissions
        self.admission_probs = \
            np.array(self.admissions['admissions']) / self.total_admissions

        return

    def convert_unit_postocde_to_index(self):
        """Convert a table of unit postcode to unit index numbers"""

        # Create lookup DataFrame
        lookup = self.units[['Postcode', 'Index']]
        lookup.set_index('Postcode', inplace=True)
        # Apply lookup
        postcode_to_index = lambda x: lookup.loc[x]['Index']
        df = self.units_by_time.applymap(postcode_to_index)

        return df


    @staticmethod
    def order_by_time(matrix):
        """For each location, sort hospitals by travel time"""

        units = np.array(list(matrix))
        time = matrix.values
        argsorted = units[np.argsort(time, axis=1)]
        df = pd.DataFrame(argsorted, index=matrix.index)

        return df
