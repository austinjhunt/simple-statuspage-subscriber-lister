# Atlassian StatusPage Per-Component Subscriber Lister

The Atlassian StatusPage product does offer a REST API but it is somewhat limited. We received a key question, "who is subscribed to a given component?" and were unable to answer via the UI or the API. The [get_subscribers_for_component.py](./get_subscribers_for_component.py) script in this project addresses this question. 

## Setup to Run Locally
1. Clone this project. 
2. Install Python 3 if you do not have it installed. 
3. Create and activate a virtual environment: `python3 -m venv venv && source venv/bin/activate`
4. Install Python requirements: `pip install -r requirements.txt`
5. Create your own `.env` by copying `.env-sample` and changing the values to your own. This is critical because otherwise your script will not know which StatusPage environment to use or how to authenticate. 

## Get subscribers for a given component by component name

This script can be run from the command line as follows:
`python get_subscribers_for_component.py --component-name "Your Component Name"` 

## Get subscribers for a given component by component id

This script can be run from the command line as follows:
`python get_subscribers_for_component.py --component-id "Your Component ID"`
 
You can also pass `--out-json <filename>` or `--out-csv <filename>` if you would like to save the results to a CSV or JSON file for sharing.