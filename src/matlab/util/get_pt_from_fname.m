function [pt_id] = get_pt_from_fname(fname)
% GET_PT_FROM_FNAME
%      fname - string, name of an edf file that we want to process
%      returns pt_id - string, name of the patient id that corresponds to
%                       this edf
% eg. get_pt_from_fname('CA_MGH_13_1_0_20110222_123122.edf') -> 'CA_MGH_13'

[~,fname,~] = fileparts(fname);
pieces = strsplit(fname, '_');
pid_pieces = {};
if contains(fname, 'CA_BIDMC') || contains(fname, 'CA_MGH')
    pid_pieces = pieces(1:3); 
else
    pid_pieces = pieces(1:2);
end
pt_id = strjoin(pid_pieces, '_');
end
