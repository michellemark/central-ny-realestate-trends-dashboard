# Central New York Real Estate Analytics Dashboard

- Part of 2 part capstone project
- Author: Michelle Mark
- For: Bachelors of Science in Computer Science, SUNY Poly
- Copyright: All rights reserved, 2025

## CNY Real Estate Analytics Dashboard Overview

### Visualize Data For Central New York Real Estate Analytics App

This repository contains a user-friendly Streamlit web application designed 
to visualize and provide analytics on property assessment data for CNY counties.  
Data is sourced from an SQLite database hosted on Amazon S3, and acquired with 
the [etl-pipeline](https://github.com/michellemark/etl-pipeline.git) 
part of this capstone project.

#### Project Objectives

- Provide an intuitive interface for analyzing property records, including market values, assessment ratios, and geographical
  trends.
- Allow easy access and interactive exploration of large databases without excessive memory requirements, optimized
  for deployment on Streamlit Cloud.

#### Features

- **Efficient Data Loading**: Streams property data from a remote SQLite database stored on AWS S3, utilizing caching mechanisms
  to optimize resource usage.
- **Dynamic Filtering**: Users can interactively filter data by county, school districts, property classifications, and more.
- **Analytics & Visualization**: Interactive visualizations prepared with Plotly to show property valuations, assessments, and
  distribution insights (mean, median, quartile analysis, standard deviation, etc.).
- **Pagination**: Implements a server-side pagination mechanism to manage memory usage and effectively handle large volumes of
  data within Streamlit Cloud memory constraints.

## Development

This repository uses Python 3.12, managed by [pyenv](https://github.com/pyenv/pyenv) and dependencies managed
with [Poetry](https://python-poetry.org/docs/).

Before you start, make sure you have:

- `pyenv` installed and Python version 3.12.8 set as the current global or local Python version.
- `poetry` installed for dependency management.

To install dependencies using Poetry (including dev dependencies):

```shell
poetry install --no-root
```

### Activating Virtual Environment

To activate the virtual environment managed by Poetry, run the following command (recommended):

```shell
poetry env activate
```

Alternatively, you can run individual commands without activating the shell explicitly:

```shell
poetry run <command>
```

### Deployment

This project is re-deployed onto Streamlit Cloud automatically each time the main branch
is updated in GitHub.

### Running Streamlit Dashboard Locally

```shell
streamlit run streamlit_app.py
```
