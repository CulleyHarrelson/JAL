import pandas as pd
import os
import panel as pn
import json
import re
import requests
import datetime as dt
from bokeh.models.widgets.tables import DateFormatter
import altair as alt

from JAL import *

pn.extension()
pn.extension("tabulator")
pn.config.notifications = True

# pn.state.notifications.position = "bottom-center"

jal_df = initialize_dataframe()

bootstrap = pn.template.BootstrapTemplate(
    title="JAL ~ Job Application Log",
    header_background="lightblue",
)

sidebar_md = pn.pane.Markdown(
    """* [**New Application**](new)
* **Applications**
* [**Analytics**](analytics)
"""
)

applications_page_header = pn.pane.Markdown(
    """
    # Job Application Datatable
    """
)

applications_page_header.width = 920

jobs_data_table = pn.widgets.Tabulator(jal_df)
jobs_data_table.show_index = False
jobs_data_table.sorters = [{"field": "application_date", "dir": "desc"}]
jobs_data_table.formatters = {"application_date": DateFormatter()}
jobs_data_table.titles = {
    "job_title": "Job Title",
    "job_code": "Job Code",
    "company_name": "Company Name",
    "location": "Location",
    "application_date": "Application Date",
}
jobs_data_table.hidden_columns = [
    "starting_salary_range",
    "ending_salary_range",
    "experience_level",
    "job_type",
    "company_size",
    "industry",
    "applicants",
]

bootstrap = pn.template.BootstrapTemplate(
    title="JAL ~ Job Application Log",
    header_background="lightblue",
)

bootstrap.sidebar.append(sidebar_md)

bootstrap.main.append(applications_page_header)
bootstrap.main.append(jobs_data_table)

bootstrap.servable()
