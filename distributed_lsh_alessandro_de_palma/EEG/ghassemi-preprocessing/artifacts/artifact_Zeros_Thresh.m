function [] = artifact_Zeros_Thresh( file_list, threshold )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here


    ptm=matfile(file_list,'Writable',true);
    
    %LOAD IN THE EEG FILE
    load(file_list);
    
    %Find Threshold
    artifacts = squeeze(max(EEG.data,[],2)) > threshold |...
                squeeze(min(EEG.data,[],2)) < -threshold;
    
    ptm.rejthresh = artifacts;
    
    %Find the Artifacts.
    artifacts = squeeze(sum(EEG.data,2) == 0);
    ptm.rejzeros = artifacts;  
    
    %'Done with subject' 
    %i
    
   



end

