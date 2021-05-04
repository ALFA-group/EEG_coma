function [ global_stats ] = compute_population_statistics( stats_cellarray )
%compute_population_statistics Compute the statistics for the entire
%population.
%   The output is a struct with the following format (comments below in the
%   code).
%   eye_upper
%   eye_lower
%   mean_kurt
%   std_kurt
%   muscle_upper
%   muscle_lower
%   mean_skew
%   std_skew
%   mean_variance
%   std_variance
  

    %% Preliminaries.
    N_PATIENTS = length(stats_cellarray);    


    %% Compute statistics.
    power_0_2_band_patient_mean = cell(N_PATIENTS);
    power_20_40_band_patient_mean = cell(N_PATIENTS);
    kurtosis_array = [];  % Used to concatenate linearizations of patient matrices.
    skew_array = [];
    variance_array = [];
    % Iterate through patients.
    for i = 1:length(stats_cellarray)
        n_epochs = size(stats_cellarray{i}.kurtosis, 2);
        n_channels = size(stats_cellarray{i}.kurtosis, 1);


        power_0_2_band_patient_mean{i} = mean(mean(stats_cellarray{i}.power_0_2_band));  % Compute mean of power in 0-2 Hz band across channels and epochs.
        power_20_40_band_patient_mean{i} = mean(mean(stats_cellarray{i}.power_20_40_band));  % Compute mean of power in 20-40 Hz band across channels and epochs.
        kurtosis_array = cat(2, kurtosis_array, reshape(stats_cellarray{i}.kurtosis, 1, n_epochs * n_channels));  % Linearize matrix for each patient and append it.        
        skew_array = cat(2, skew_array, reshape(stats_cellarray{i}.skew, 1, n_epochs * n_channels));
        variance_array = cat(2, variance_array, reshape(stats_cellarray{i}.variance, 1, n_epochs * n_channels));
    end

    % Eye_Movements artifacts are where an epoch +/- 50 db from the mean (over both channels and
    % patients) in 0-2Hz Band.
    global_stats.eye_upper = mean(power_0_2_band_patient_mean) * db2pow(50); % Mohammad had 316, i.e., db2mag(50), instead (not compliant with reference).
    global_stats.eye_lower = mean(power_0_2_band_patient_mean) * db2pow(-50);  

    % Compute mean and std of kurtosis on the population, for kurtosis artifacts. 
    global_stats.mean_kurt = mean(kurtosis_array);
    global_stats.std_kurt = std(kurtosis_array);

    % Muscle artifacts are where an epoch is + 25 or -100 db from the mean in 20-40Hz
    % band.
    global_stats.muscle_upper = mean(power_20_40_band_patient_mean)*db2pow(25);
    global_stats.muscle_lower = mean(power_20_40_band_patient_mean)*db2pow(-100);

    % Compute mean and std of skewness on the population, for skewness artifacts. 
    global_stats.mean_skew = mean(skew_array);
    global_stats.std_skew = std(skew_array);

    % Compute mean and std of variance on the population, for variance artifacts. 
    global_stats.mean_variance = mean(variance_array);  % Mohammad is excluding the entries equal to 0 from these stats, for some reason.
    global_stats.std_variance = std(variance_array);

end

