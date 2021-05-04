import numpy as np

### Classes which collect similarity output#######

class OutputCollector:        
    def add_patient_all_sims(self, patient_all_sims, outcome=None):
        pass
    def done(self):
        pass
    
class PercentileCollector(OutputCollector):
    def __init__(self):
        self.percentiles_list = []
    def add_patient_all_sims(self, patient_all_sims, outcome=None):
        if len(patient_all_sims)==0:
            percentiles_sim = np.full(11, np.nan)
        else:
            percentiles_sim = np.percentile(patient_all_sims, np.linspace(0,100, 11))
        self.percentiles_list.append(percentiles_sim)
    def done(self):
        self.percentiles_list = np.array(self.percentiles_list)
        
class MeanCollector(OutputCollector):
    def __init__(self):
        self.means_list = []
    def add_patient_all_sims(self, patient_all_sims, outcome=None):
        if len(patient_all_sims)==0:
            mean_sim = np.nan
        else:
            mean_sim = np.mean(patient_all_sims)
        self.means_list.append(mean_sim)
    def done(self):
        self.means_list = np.array(self.means_list)
        
class HistogramCollector(OutputCollector):
    def __init__(self, outcome_predicate, bin_size=0.002):
        self.counts_list = []
        self.min_bin = 0
        self.max_bin = 1.0
        self.bin_size = bin_size
        self.outcome_predicate = outcome_predicate
        
    def roundup(self, x):
        return x+self.bin_size-x%self.bin_size
    
    def rounddown(self, x):
        if x%self.bin_size==0:
            return x - self.bin_size
        else:
            return x-x%self.bin_size        
        
    def add_patient_all_sims(self, patient_all_sims, outcome=None):
        if not self.outcome_predicate(outcome):
            return
        if len(patient_all_sims)==0:
            return
        min_sim, max_sim = np.min(patient_all_sims), np.max(patient_all_sims)
        
        min_sim_rounded = self.rounddown(min_sim)
        max_sim_rounded = self.roundup(max_sim)
        self.min_bin = min(self.min_bin, min_sim_rounded)
        self.max_bin = max(self.max_bin, max_sim_rounded)
        # 1.5 so we get max_sim_rounded+self.bin_size as the highest bin value. 
        # 2 should work, but weird floating point errors happen sometimes
        bin_high_lim = max_sim_rounded + 1.5*self.bin_size 
        bins = np.arange(min_sim_rounded, bin_high_lim, self.bin_size)
        counts, bins = np.histogram(patient_all_sims, bins=bins)
        self.counts_list.append((counts, min_sim_rounded, max_sim_rounded))
        
    def done(self):
        # get the histograms_list to have the same bins for all patients
        count_len = int((self.max_bin + 1*self.bin_size-self.min_bin)/self.bin_size)
        self.histogram_matrix = np.zeros((len(self.counts_list), count_len))
        for i, (counts, min_bin, max_bin) in enumerate(self.counts_list):
            if self.min_bin < min_bin:
                extend_amt = int(round((min_bin - self.min_bin)/self.bin_size))
                counts = np.concatenate((np.zeros(extend_amt), counts))
            if self.max_bin > max_bin:
                extend_amt = int(round((self.max_bin - max_bin)/self.bin_size))
                counts = np.concatenate((counts, np.zeros(extend_amt)))
            try:
                self.histogram_matrix[i] = counts
            except ValueError as e:
                print 'value error, i={}, counts.shape={}, min_bin={}, self_min_bin={}, max_bin={}, self_max_bin={}, extend_amt={}'.format(
                    i, counts.shape, min_bin, self.min_bin, max_bin, self.max_bin, extend_amt)
                raise
        self.bins = np.arange(self.min_bin, self.max_bin+2*self.bin_size, self.bin_size)
        
    def normalize(self):
        # ONLY USE AFTER DONE IS CALLED
        row_sums = self.histogram_matrix.sum(axis=1)
        normalized_histogram_matrix = self.histogram_matrix / row_sums[:, np.newaxis]
        return normalized_histogram_matrix
    
    def aggregate_histograms(self, normalize_row=False, normalize_final=False):
        if normalize_row:
            normalize_final = True
        if normalize_row:
            histogram_matrix = self.normalize()
        else:
            histogram_matrix = self.histogram_matrix
        matrix_sum = histogram_matrix.sum(axis=0)
        if normalize_final:
            matrix_sum = matrix_sum / sum(matrix_sum)
        # TODO
        # return the normalized thing back to counts (when normalize_row=True):
        # divide by the smallest non-zero number in matrix_sum
        return matrix_sum
    
class BSOutcomeCollector(OutputCollector):   
    def __init__(self):
        self.bs_count = 0
        self.bs_outcome = []
        self.has_bs = []
    def add_patient_all_sims(self, patient_all_sims, outcome=None):
        if len(patient_all_sims) > 0:
            self.bs_count +=1
            self.bs_outcome.append(outcome)
            self.has_bs.append(True)
        else:
            self.has_bs.append(False)
            
class OutcomeCollector(OutputCollector):
    def __init__(self):
        self.outcomes = []
    def add_patient_all_sims(self, patient_all_sims, outcome=None):
        self.outcomes.append(outcome)    