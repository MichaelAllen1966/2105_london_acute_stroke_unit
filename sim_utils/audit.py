class Audit(object):

    def __init__(self):
        """
        Constructor method for audit.

        Attributes
        ==========
        global_audit (dictionary):
            Audit of high level metrics
        unit_audit (dictionary):
            Audit at unit level



        """
        # Initialise global audits
        self.global_audit_index_count = 0
        self.global_audit = []
        self.audit_unit_occupancy = []
        self.audit_unit_occupancy_percent = []
        self.audit_unit_occupancy_displaced_preferred = []
        self.audit_unit_occupancy_displaced_destination = []
        self.audit_unit_occupancy_waiting_preferred = []

    def perform_global_audit(self, _model):
        """
        Perform audit of high level model parameters/metrics
        """
        
        while True:
            if _model.env.now >= _model.params.sim_warmup:
                # Global tracker audit
                self.global_audit_index_count += 1
                item = dict()
                item['index'] = self.global_audit_index_count
                item['time'] = _model.env.now
                item['total_patients'] = _model.tracker['total_patients']
                item['total_patients_asu'] = _model.tracker['total_patients_asu']
                item['total_patients_waited'] = _model.tracker['total_patients_waited']
                item['total_patients_displaced'] = _model.tracker['total_patients_displaced']
                item['current_patients'] = _model.tracker['current_patients']
                item['asu_patients_all'] = _model.tracker['current_asu_patients_all']
                item['asu_patients_allocated'] = _model.tracker['current_asu_patients_allocated']
                item['asu_patients_unallocated'] = _model.tracker['current_asu_patients_unallocated']
                item['asu_patients_displaced'] = _model.tracker['current_asu_patients_displaced']
                self.global_audit.append(item)

                # Occupancy, displaced and waiting patients
                self.audit_unit_occupancy.append(_model.unit_occupancy)
                self.audit_unit_occupancy_percent.append(
                    (_model.unit_occupancy/_model.data.units_capacity)*100)
                self.audit_unit_occupancy_displaced_preferred.append(
                    _model.unit_occupancy_displaced_preferred )
                self.audit_unit_occupancy_displaced_destination.append(
                    _model.unit_occupancy_displaced_destination)
                self.audit_unit_occupancy_waiting_preferred .append(
                    _model.unit_occupancy_waiting_preferred)

                # Wait for next audit
            yield _model.env.timeout(1)
            
