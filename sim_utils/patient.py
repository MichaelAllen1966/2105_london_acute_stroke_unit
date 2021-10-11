import numpy as np


class Patient(object):
    """
    Patient object

    methods
    -------
    __init__:
        Constructor method

    attributes
    ----------
    id (int):
        patient id

    """

    def __init__(self, patient_dict, params):
        """Constructor method for patient"""

        # Set parameters from patient dictionary
        self.id = patient_dict['id']
        self.lsoa_index = patient_dict['lsoa_index']
        self.lsoa = patient_dict['lsoa']
        self.pref_unit_postcode = patient_dict['pref_unit_postcode']
        self.pref_unit_name = patient_dict['pref_unit_name']
        self.pref_unit_index = patient_dict['pref_unit_index']
        self.patient_region = patient_dict['patient_region']

        # Set default values
        self.assigned_asu_index = None
        self.assigned_asu_postcode = None
        self.assigned_asu_name = None
        self.waiting_for_asu = None
        self.displaced = None  # Not in preferred ASU
        self.los_asu = None
        self.los_esd = None
        self.time_in = None
        self.time_asu_allocated = None
        self.time_waiting_for_asu = None
        self.time_asu_end = None
        self.waited_for_asu = None

        # Set link to model parameters
        self._params = params

        # Set use of ASU and ESD
        self.use_asu = (True if np.random.rand() < self._params.require_asu
                        else False)

        self.use_esd = (True if np.random.rand() < self._params.esd_use
                        else False)
