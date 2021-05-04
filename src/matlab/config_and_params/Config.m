classdef Config
    % Class which stores basic config for scripts, such as repo path
    
    properties (Constant)
        
        % path to coma_EEG_alice_zhan repository
        repo_dir = '~/coma_EEG_alice_zhan/';
        %repo_dir = '~/eeg/coma_EEG_alice_zhan/';

        % where to save script output
        output_dir = '~/coma_EEG_alice_zhna/src/6S897_results/output_dir/';
        %output_dir = '~/NFS/script_output/';

        % where to save scripts/visualize output
        save_images_dir = '~/coma_EEG_alice_zhan/src/6S897_results/images/';
        %save_images_dir = '~/eeg/images/';

        % path to file containing list of paths to edfs to process
        todo_files_list = '~/coma_EEG_alice_zhan/src/sample_data/bs/test_subset_files.txt';
        %todo_files_list = '~/eeg/patient_file_lists/all_readable_split_2/bi0_all.txt';
    end
    
    methods(Static)
        function varargout = get_configs(varargin)
            for i = 1:length(varargin)
                varargout{i} = getfield(Config, varargin{i});
            end
        end
    end
end

