import numpy as np
import pandas as pd
import simpy

from sim_utils.audit import Audit
from sim_utils.data import Data
from sim_utils.patient import Patient

import warnings

warnings.filterwarnings("ignore")


class Model(object):

    def __init__(self, scenario):
        """


        """
        self.env = simpy.Environment()
        self.params = scenario
        self.data = Data()
        self.audit = Audit()
        self.patients = []

        self.patient_id_count = 0
        # Set up 1D NumPy array for patient counts per unit
        number_hospitals = self.data.units.shape[0]
        self.unit_occupancy = np.zeros(number_hospitals)
        self.unit_admissions = np.zeros(number_hospitals)

        # Count displaced patients
        self.unit_occupancy_displaced_preferred = np.zeros(number_hospitals)
        self.unit_occupancy_displaced_destination = np.zeros(number_hospitals)
        self.unit_occupancy_waiting_preferred = np.zeros(number_hospitals)

        # Set up tracker dictionary (total patients updated after warmup)
        self.tracker = {
            'total_patients': 0,
            'total_patients_asu': 0,
            'total_patients_waited': 0,
            'total_patients_displaced': 0,
            'current_patients': 0,
            'current_asu_patients_all': 0,
            'current_asu_patients_allocated': 0,
            'current_asu_patients_unallocated': 0,
            'current_asu_patients_displaced': 0,
            'patient_waiting_time': []
        }

    def assign_asu_los(self, patient):
        """Assign length of stay based on assigned ASU unit"""

        los_mean = self.data.units.iloc[patient.assigned_asu_index]['los_mean']
        los_sd = los_mean * self.params.los_cv
        los = max(np.random.normal(los_mean, los_sd), 0.01)
        patient.los_asu = los

        return

    def end_run_routine(self):
        """
        Data handling at end of run
        """
        self.global_audit = pd.DataFrame(self.audit.global_audit)

        self.occupancy_audit = pd.DataFrame(
            self.audit.audit_unit_occupancy, columns=self.data.units_name)

        self.admissions_by_unit = pd.Series(
            self.unit_admissions, index=self.data.units_name)

        self.occupancy_percent_audit = pd.DataFrame(
            self.audit.audit_unit_occupancy_percent, 
            columns=self.data.units_name)

        self.unit_occupancy_displaced_preferred_audit = pd.DataFrame(
            self.audit.audit_unit_occupancy_displaced_preferred,
            columns=self.data.units_name)

        self.unit_occupancy_displaced_destination_audit = pd.DataFrame(
            self.audit.audit_unit_occupancy_displaced_destination,
            columns=self.data.units_name)

        self.unit_occupancy_waiting_preferred_audit = pd.DataFrame(
            self.audit.audit_unit_occupancy_waiting_preferred,
            columns=self.data.units_name)
        
        if len(self.tracker['patient_waiting_time']) > 0:
            self.average_wait_time_all = (np.sum(
                self.tracker['patient_waiting_time']) /
                self.tracker['total_patients_asu'])
        else:
            self.average_wait_time_all = 0
        
        if len(self.tracker['patient_waiting_time']) > 0:
                self.average_wait_time_waiters = np.mean(
               self.tracker['patient_waiting_time'])
        else:
            self.average_wait_time_waiters = 0
        
        if len(self.tracker['patient_waiting_time']) > 0:
            self.maximum_wait_time = np.max(
                self.tracker['patient_waiting_time'])   
        else: self.maximum_wait_time = 0        

    def generate_patient_arrival(self):
        """SimPy process. Generate patients. Assign unit and length of stay.
        Pass patient to hospital bed allocation"""

        # Continuous loop of patient arrivals
        while True:
            # Put patient attributes in a dictionary, and pass to Patient object
            patient_dict = dict()
            self.patient_id_count += 1
            if self.env.now >= self.params.sim_warmup:
                self.tracker['total_patients'] += 1
            patient_dict['id'] = self.patient_id_count
            patient_dict['lsoa_index'] = np.random.choice(
                range(self.data.lsoa_count), p=self.data.admission_probs)
            patient_dict['lsoa'] = \
                self.data.lsoa_list[patient_dict['lsoa_index']]
            patient_dict['pref_unit_postcode'] = (
                self.data.pref_unit.loc[patient_dict['lsoa']][
                    'Preferred_unit_postcode'])
            patient_dict['pref_unit_name'] = (
                self.data.pref_unit.loc[patient_dict['lsoa']]
                ['Preferred_unit_name'])
            patient_dict['pref_unit_index'] = (
                self.data.units.loc[patient_dict['pref_unit_name']]['Index'])
            patient_dict['patient_region'] = (
                self.data.units.loc[patient_dict['pref_unit_name']]['region'])
            patient = Patient(patient_dict, self.params)
            self.patients.append(patient)

            # Pass patient to patient journey
            process = self.patient_journey(patient)
            self.env.process(process)

            # Wait for next patient arrival
            time_to_next = (self.data.interarrival_interval /
                            self.params.scale_admissions)
            yield self.env.timeout(time_to_next)
            # Return to top of while loop

    def patient_journey(self, patient):
        """
        Patient journey:
        1) Check if acute care is needed
        2) Acute care (find appropriate place)
        3) ESD
        """

        self.tracker['current_patients'] += 1

        patient.time_in = self.env.now

        if patient.use_asu:
            if self.env.now >= self.params.sim_warmup:
                self.tracker['total_patients_asu'] += 1
            self.tracker['current_asu_patients_all'] += 1
            self.tracker['current_asu_patients_unallocated'] += 1
            self.unit_occupancy_waiting_preferred[patient.pref_unit_index] += 1

            # Look to allocate patient to unit
            unallocated = True
            while unallocated:
                # Check if preferred unit has capacity
                capacity = self.data.units_capacity[patient.pref_unit_index]
                occupied_beds = self.unit_occupancy[patient.pref_unit_index]
                spare_beds = capacity - occupied_beds

                if spare_beds > 0:
                    # Spare capacity in preferred unit
                    self.unit_occupancy[patient.pref_unit_index] += 1
                    if self.env.now >= self.params.sim_warmup:
                        self.unit_admissions[patient.pref_unit_index] += 1
                    patient.assigned_asu_index = patient.pref_unit_index
                    patient.assigned_asu_postcode = \
                        self.data.units_postcode[patient.pref_unit_index]
                    patient.assigned_asu_name = \
                        self.data.units_name[patient.pref_unit_index]
                    patient.waiting_for_asu = False
                    patient.displaced = False
                    unallocated = False

                # Check other units if allowed
                elif self.params.allow_non_preferred_asu:
                    choice_order = list(
                        self.data.units_index_by_time.loc[patient.lsoa])
                    for unit in choice_order:
                        # Check if limited to regions and unit in region
                        if (self.params.restrict_non_preferred_to_regions and 
                            self.data.unit_region[unit] != patient.patient_region):
                            # Skip remainder of loop if unit not in patient region
                            continue
                        # Check unit is allowed for pool use
                        if self.data.allow_pool_use[unit] == 0:
                            continue
                        # Calculate number of spare beds
                        capacity = self.data.units_capacity[unit]
                        occupied_beds = self.unit_occupancy[unit]
                        spare_beds = capacity - occupied_beds
                        if spare_beds > 0:
                            # Bed available in alternative unit
                            self.unit_occupancy[unit] += 1
                            patient.assigned_asu_index = unit
                            patient.assigned_asu_postcode = \
                                self.data.units_postcode[unit]
                            patient.assigned_asu_name = \
                                self.data.units_name[unit]
                            patient.waiting_for_asu = False
                            patient.displaced = True
                            unallocated = False
                            self.unit_occupancy_displaced_preferred[
                                patient.pref_unit_index] += 1
                            self.unit_occupancy_displaced_destination[unit] += 1
                            if self.env.now >= self.params.sim_warmup:
                                self.tracker['total_patients_displaced'] += 1
                                self.unit_admissions[unit] += 1
                            # End loop
                            break

                # Wait for 0.25 day before searching again (if necessary)
                if unallocated:
                    yield self.env.timeout(0.25)

            # Unit allocated; adjust trackers and patient values
            self.tracker['current_asu_patients_allocated'] += 1
            self.tracker['current_asu_patients_unallocated'] -= 1
            if patient.displaced:
                self.tracker['current_asu_patients_displaced'] += 1
            self.unit_occupancy_waiting_preferred[patient.pref_unit_index] -= 1
            patient.time_asu_allocated = self.env.now
            patient.time_waiting_for_asu = \
                patient.time_asu_allocated - patient.time_in
            patient.waited_for_asu = \
                True if patient.time_waiting_for_asu > 0 else False
            if patient.waited_for_asu:
                if self.env.now >= self.params.sim_warmup:
                    self.tracker['total_patients_waited'] += 1
                    self.tracker['patient_waiting_time'].append(
                        patient.time_waiting_for_asu)

            # Stay in ASU
            self.assign_asu_los(patient)
            yield self.env.timeout(patient.los_asu)

            # End of ASU; adjust trackers
            self.tracker['current_asu_patients_all'] -= 1
            self.tracker['current_asu_patients_allocated'] -= 1
            self.unit_occupancy[patient.assigned_asu_index] -= 1

            if patient.displaced:
                self.unit_occupancy_displaced_preferred[
                patient.pref_unit_index] -= 1
                self.unit_occupancy_displaced_destination[
                patient.assigned_asu_index] -= 1
                self.tracker['current_asu_patients_displaced'] -= 1

        # TODO Add ESD?

        # End of patient journey
        self.tracker['current_patients'] -= 1
        self.patients.remove(patient)
        del patient

    def run(self):
        # Initialise processes that will run on model run.
        self.env.process(self.generate_patient_arrival())
        self.env.process(self.audit.perform_global_audit(self))

        # Run
        run_duration = self.params.sim_warmup + self.params.sim_duration
        self.env.run(until=run_duration)

        # End of run
        self.end_run_routine()
