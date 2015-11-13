# Tax and Expenditure Limitations
## New Debt Issues
This project seeks to evaluate the implications of tax and expenditure limitations for local government debt activity.  Specifically, we ask if tax and expenditure limitations influence the volume of new debt issued by a number of governmental entities, after controlling for a vector of socioeconomic characteristics.

The unit of analysis is the county, with all relevant subsets of debt aggregated across all constituent governments.  Tax and expenditure limitations are modeled in a manner commensurate with their varied impact on differing jurisdictions, given varied implementation schemes.  I guess you will have to read the paper if you want anything more specific.

The schema of this project seeks to ease navigation for those who want to reproduce this analysis.

+ **`code/` ** holds the Notebooks and other scripts used to conduct both data management and the statistical analysis itself.
+ **`data/`** holds only the interim (that is, processed to some extent) and final data in this analysis.  The raw data are proprietary unfortunately, but feel free to contact us for methods of purchase.
+ **`doc/`** holds random documents that may or may not be of some relevance.  Note that the data management and analytic narrative is largely contained within the Notebooks themselves.
+ **`figures/`** contains the exhibits (as generated) to be used in the paper, as well as presentation of the work.

### [Jupyter](http://jupyter.org/) Notebooks

There are a number of Notebooks, so some organizational commentary may be useful.  The main workflow travels through three Notebooks:

1. *`sas2csv`* is concerned with converting SAS datasets to CSV for use in *`DebtDataSeries`*.  It takes on the related yet auxiliary task of getting the raw COSTAT data to play nice with all other sets.  (Honestly, Census, you could probably make this easier.)  The output of this script is a set (`tel_data.csv` in the **`data/`** folder) that is a three part join.  The 'left' set is a custom set of selected COSTAT and PUMS variables.  It has year-county resolution.  The second set captures institutional factors (TELs and whatnot), and it has year-state resolution.  Therefore, the first join matches TEL factors from the second set to all counties in each state.  The third set covers (largely) derivative variables calculated with input variables from the raw COSTAT data.  *Note that the data between observed values is interpolated and exterior values are simple pads (that is, repeated from the last known value).*
2. *`DebtDataSeries`* takes on task of building a time series from the raw debt data.  (The script used to convert this data from a questionable fixed width format to CSV is `debt_data2csv.py`.)  A major portion of this effort is identifying the FIPS codes for each issue.  At the current time, the match rate is approximately 98%.  (Do not run *`DebtDataSeries`* if unnecessary.  If the Google API must be accessed again, this will 1) cost money, and 2) take an hour or more.)  After the construction of this set, these data are joined with the output of *`sas2csv`*.  The output set is called `debt_out.csv`.  The resolution is year-county.
3.  *`Debt_onTEL`* is the modeling Notebook.  Nothing of note yet.  The modeling task revealed gaps in the preparatory Notebooks.

The other Notebooks serve auxiliary purposes related to data exploration and construction of figures.