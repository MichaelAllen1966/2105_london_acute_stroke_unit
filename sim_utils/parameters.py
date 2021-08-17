class Scenario(object):
    """Model scenario parameters

    esd_use (float):
        Proportion of ASU users who are discharged to early supported discharge
    esd_asu_los_reduction (float):
        Reduction in ASU los (days) if using ESD
    los_cv (float):
        cv (std dev /mean) of length of stay
    require_asu (float):
        Proportion of HASU admissions requiring ASU admissions
    scale_admissions (float):
        Scale default admission numbers to model change in demand
    sim_duration (float):
        Duration of simulation data collection phase
    sim_warmup (float):
        Duration of simulation warm-up

    """

    def __init__(self, *initial_data, **kwargs):
        """Default  parameters"""
        # Simulation parameters
        self.sim_warmup = 100
        self.sim_duration = 365

        # Scale admissions
        self.scale_admissions = 1.0

        # Patient flow
        self.require_asu = 0.57
        self.esd_use = 0.
        self.esd_asu_los_reduction = 7.0
        self.los_cv = 0.3
        self.allow_non_preferred_asu = False

        # Overwrite default values

        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
