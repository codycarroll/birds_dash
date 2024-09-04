# NorCal Bird Dash 
The [dashboard is located at this link](https://birds-dash-547zxcr6ea-uc.a.run.app/),
with a [backup hosted on Dash here](https://bird-dash-slssljz5da-uc.a.run.app/).

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Repository Description](#repository-description)
- [Requirements](#requirements)
- [Local Installation](#local-installation)
- [Global Installation](#global-installation)

## Project Overview
This repository contains a dashboard designed to visualize bird prevalence trends over different seasons across 260 species, with data sourced from iNaturalist and eBird.


## Repository Description
This repository contains the code for the NorCal Bird Dash application, a Dash app that monitors seasonality patterns of birds in Northern California.
```
├── Dockerfile          # Dockerfile for app build
├── LICENSE             # Liscensing info for repo
├── README.md           # Instructions about repository
├── app.py              # Script for deploying the dashboard
├── assets/             # Contains style formatting of dashboard
├── birds_dash.Rmd      # A prototype in R
├── birds_dash.html
├── data/               # Directory contain all data
│   ├── raw/            # Sub-directory contain all RAW data
│   └── smoothed/       # Sub-directory contain all SMOOTHED data
├── figures.py          # Script for each figure in the dashboard
├── images/             # Directory of images used in ReadMe instructions
└── requirements.txt    # Requirements needed for deploying application

```
## Requirements

To run the app globally, you will need a Google Cloud account.

### Google Cloud

To run the app globally, ensure you have:

- A [Google Cloud account](https://cloud.google.com/) with billing enabled.
- Google Cloud Command Line Interface (CLI) installed on your computer. See [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install) for more information.


## Local Installation

To install this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/codycarroll/birds_dash.git
    ```

2. Navigate to the project directory:
    ```bash
    cd birds_dash
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the app:
    ```bash
    python app.py
    ```


