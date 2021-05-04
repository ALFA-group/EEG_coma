# Quick start guide for how to run the entire pipeline and create the figures seen in the thesis:
## Run the pipeline in MATLAB
See section C.2.2 of the appendix of the thesis, particularly subsection `scripts/run`
### Create a list of files to process
1. Create a `todo_files_list`, or a txt file where each line is the path to an EDF you wish to process
### Edit the configuration and parameters
2. Edit `src/matlab/config_and_params/Config.m` to match your local configuration
3. Edit any parameters you like in `src/matlab/config_and_params/...Params.m`
### Run the pipeline
4. Go to `src/python/run_matlab_scripts`. Run `python run_matlab_script.py run/write_similarities.m sample_run`
## Create the plots in python
Refer to C.2.4 of the thesis appendix for details.
### Edit the patient outcome info
5. Edit any files necessary in `patient_outcome_info` to match your dataset. 
### Run the plotting notebooks
6. Open up the following notebooks:
(To open up these notebooks, you must jupyter installed. Run `jupyter notebook`, and navigate to the folder containing the notebook you wish to open)
- src/python/plotting_notebooks/describe_bs/bsr_zs_over_time_heatmap.ipynb
- src/python/plotting_notebooks/describe_bs/describe_bs_histograms.ipynb
- src/python/plotting_notebooks/similarity/similarity_over_time.ipynb
- src/python/plotting_notebooks/similarity/similarity_analysis.ipynb
Each of these notebooks creates some of the figures seen in the thesis. 
