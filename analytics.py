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

jal_df = initialize_dataframe()


pn.extension()
pn.extension("tabulator")
pn.config.notifications = True


bootstrap = pn.template.BootstrapTemplate(
    title="JAL ~ Job Application Log",
    header_background="lightblue",
)

sidebar_md = pn.pane.Markdown(
    """* [**New Application**](new)
* [**Applications**](applications)
* **Analytics**
"""
)

useage_md = pn.pane.Markdown(
    """
**Data Recorded:**

#### Application Date

The date of the application defaults to today, but you can back date applications that were submitted in the past.

#### LinkedIn Job Code

The **Job Code** can be found in the url for the job listing. In this example:

https://www.linkedin.com/jobs/view/1234

**1234** is the job code.

#### LinkedIn Job Details

describe job details

"""
)
# useage_md.width = 920
useage_md.margin = 10


add_job_header = pn.pane.Markdown(
    """
    **Add a Job Application to Log:**
    """
)


refresh_button = pn.widgets.Button(name="Refresh Data")  # , button_type="primary")
date_range_slider = pn.widgets.DateRangeSlider(
    name="Reporting Range",
    # start=dt.datetime(2017, 1, 1),
    start=jal_df["application_date"].min().to_pydatetime(),
    end=jal_df["application_date"].max().to_pydatetime(),
    value=(
        jal_df["application_date"].min().to_pydatetime(),
        jal_df["application_date"].max().to_pydatetime(),
    ),
    step=24 * 3600 * 2 * 1000,
)
# ,


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


company_size_summary = jal_df.groupby("company_size")["job_code"].count()
company_size_summary = pd.DataFrame(company_size_summary).reset_index()
company_size_summary.rename(columns={"job_code": "Count"}, inplace=True)

company_size_donut_chart = (
    alt.Chart(company_size_summary)
    .mark_arc(innerRadius=65)
    .encode(
        theta="Count",
        color=alt.Color("company_size:N", sort=company_sizes()).legend(
            title="Company Size",
            orient="right",
        ),
        size="Count",
    )
    # .properties(width=100)
)

ca_step_one = jal_df.groupby(["application_date"]).count()
ca_step_two = ca_step_one.cumsum()
ca_step_two.reset_index(inplace=True)
ca_step_two.rename(columns={"index": "application_date"}, inplace=True)
ca_step_two["application_date"] = pd.to_datetime(ca_step_two["application_date"])


cumulative_application_chart = (
    alt.Chart(ca_step_two.reset_index())
    .mark_line(interpolate="step-after")
    .encode(
        x=alt.X("application_date:T", axis=alt.Axis(labelAngle=-45), title="Date"),
        y=alt.Y("job_code", title="Cumulative Applications"),
        tooltip=["application_date", "job_code"],
    )
    .properties(width=800, height=400)
)


pd.options.mode.chained_assignment = None
starting = jal_df[["location", "starting_salary_range"]]
starting.rename(columns={"starting_salary_range": "salary"}, inplace=True)
ending = jal_df[["location", "ending_salary_range"]]
ending.rename(columns={"ending_salary_range": "salary"}, inplace=True)
location_box_plot_df = pd.concat([starting, ending])
location_salary_box_plot = (
    alt.Chart(location_box_plot_df)
    .mark_boxplot(extent="min-max")
    .encode(
        x=alt.X("location:O", title="Location", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("salary:Q", title="Salary"),
    )
    .properties(width=400)
)
# q: what is the key combination for switching between tabs?


delta = (dt.date.today() - jal_df["application_date"].min().date()).days
if delta == 0:
    delta = 1
daily_application_average = jal_df["job_code"].count() / delta


bootstrap.sidebar.append(sidebar_md)
# bootstrap.sidebar.append(date_range_slider)
# bootstrap.sidebar.append(refresh_button)

daily_average = pn.indicators.Number(
    name="Daily Average",
    value=round(daily_application_average, 2),
    default_color="darkgreen",
)
application_count = pn.indicators.Number(
    name="Application Count",
    value=jal_df["job_code"].nunique(),
    default_color="darkred",
)
location_count = pn.indicators.Number(
    name="Location Count",
    value=jal_df["location"].nunique(),
    default_color="green",
)
industry_count = pn.indicators.Number(
    name="Industry Count", value=jal_df["industry"].nunique(), default_color="orange"
)
bootstrap.sidebar.append(daily_average)
bootstrap.sidebar.append(application_count)
bootstrap.sidebar.append(location_count)
bootstrap.sidebar.append(industry_count)

analysis = pn.Column(
    pn.Row(pn.Spacer(height=20)),
    pn.Row(cumulative_application_chart),
    pn.Row(company_size_donut_chart, location_salary_box_plot),
)

bootstrap.main.append(analysis)

bootstrap.servable()
