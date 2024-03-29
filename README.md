# LION - Log Intelligence and Optimization Network 🦁

> This is a stable version

Put simply, there's a lack of love for logs 😥. Developers and enterprises primiarily look at logs for root-cause analysis, but *there's so much more!* From understanding code structure and system state to identifying user activity and weaknesses across log files, LION is our solution to generate powerful insights into log files. 

Our goal? Can we do this in a *zero-shot, conversational* approach with current technology? 

Continue reading to find out! 

&nbsp; &nbsp;

## GPT Integration (W.I.P) 

These are the current methods we have that are documented with docstrings. Ready to go for GPT-calling!

`/frontend`

* `colE.py`
    * `df = extract_unique_events(df)`
    * `fig = generate_individual_timeseries_plot(df, event_id)`

* `colL.py`

* `colR.py`

* `colV.py`
    * `fig = get_histogram_given_col_title(df, title)`

`/gateway`

* `logparser.py`
    * `mask = get_df_mask_from_filtering_string(df, filtering_string)`
    * `df = log_csv_to_df(path, filtering_string=None)`

*  `matrix_profile.py`
    * `class MatrixProfileAnalyzer()`
        * `MatrixProfileAnalyzer() object = __init__(self, df)`
        * `profile, discords = get_discords(self, k=4, windows=None, subset=None)`
        * `profile, motifs = get_motifs(self, k=4, subset=None)`
        * `subset_list = get_arr_subset(self, time_arr, event_arr, range)`
        * `df_slice = get_df_entries(self, target, window=5, after=False)`
        * `plot_timeseries(self, dir)`
        * `visualize_profile(self, profile, dir)`

* `openai_summ.py`
    * `text = generate_log_summary(api_key, log_data)`

* `parse_log.py`

>   * ***Coming soon!***


&nbsp; &nbsp;

## Installation 

Simply clone this repository. Simple as that! 

Setup Python virtual environment using the command

`python<version> -m venv <environment_name>`

Activate environement using the command 

`source <environment_name/bin/activate`

Install requirements

`pip install -r requirements.txt`


***IMPORTANT: Run `pip install streamlit` and `pip install protobuf==3.20.0`, as streamlit and matrixprofile are not compatible otherwise***

Once all necessary pacakges are installed, this project should run with ease! 



&nbsp; &nbsp;

## Usage 

> **Make sure to add your OpenAI API Key to line 9 of `const.py` prior to running!**

To launch the analyzer, simply run `streamlit run main.py`

A demo video (SetupProcessVideo.webm) with instructions on features/usage. 

More log files can be found at loghub. Currently, robust support for OpenSSH logs.


## Contributing & Future Directions

> We have several TODO's spread out throughout our files! We will continue working in these directions to improve LION, adjusting as needed based on our user's feedback

We intend to add functionalities to the log analysis for unsupervised log analysis. 

If you wish to contribute or suggest any additional funtionalities, please check out [Contributing Guidelines](/CONTRIBUTING.md)

## License

Please check out the [License](/LICENSE.md)for details on the License.

