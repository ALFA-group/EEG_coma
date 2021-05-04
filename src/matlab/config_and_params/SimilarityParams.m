classdef SimilarityParams
    %DETECTBS_PARAMS Parameters used to detect_bs
    
    properties (Constant)
        
        % min and max duration (secs) of a burst to be used in
        % similarity computation. If a burst is too long or short, we ignore
        % it. 
        min_burst_time = 0.1;
        max_burst_time = 5;
        
        % max duration (secs) to take from the beginning of each burst for use in 
        % computing similarity. 
        % Together with the min and max burst time defined above, we have:
        % Burst duration [0 to min_burst_time] - burst excluded
        % Burst duration [min_burst_time to burst_splice_time] - entire
        %                                                   burst used
        % Duration [burst_splice_time to max_burst_time] - burst is spliced
        %                   to include only first burst_splice_time seconds
        % Duration [max_burst_time and above] - burst excluded
        burst_splice_time = 0.5;
        
        % whether or not to normalize bursts before computing similarity
        normalize_bursts = 1;
        
        % Width of adjustment window for dtw 
        maxsamp = 200;
    end
    
    methods(Static)
        function varargout = get_params(varargin)
            for i = 1:length(varargin)
                varargout{i} = getfield(SimilarityParams, varargin{i});
            end
        end
    end
end

