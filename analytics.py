import pandas as pd
import panel as pn
import datetime as dt
from bokeh.models.widgets.tables import DateFormatter
import altair as alt

from JAL import company_sizes, initialize_dataframe, jal_template


jal_df = initialize_dataframe()

pn.extension("vega")

bootstrap = jal_template()

sidebar_md = pn.pane.Markdown(
    """* [**New Application**](new)
* [**Applications**](applications)
* **Analytics**
"""
)
bootstrap.sidebar.append(sidebar_md)

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
        color=alt.Color("company_size:N", sort=company_sizes).legend(
            title="Company Size",
            orient="right",
        ),
        size="Count",
    )
    .properties(width=400)
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

ca_step_one = jal_df.groupby(["application_date"])["applicants"].sum()
ca_step_two = pd.DataFrame(ca_step_one.cumsum())

other_application_chart = (
    alt.Chart(ca_step_two.reset_index())
    # .mark_line(interpolate="step-after")
    .mark_line(interpolate="monotone")
    .encode(
        x=alt.X("application_date:T", axis=alt.Axis(labelAngle=-45), title="Date"),
        y=alt.Y("applicants:Q", title="Cumulative Applicants"),
        tooltip=["application_date"],
    )
    .properties(width=800, height=400)
)


pd.options.mode.chained_assignment = None
starting = jal_df[["location", "starting_salary_range"]]
starting.rename(columns={"starting_salary_range": "salary"}, inplace=True)
ending = jal_df[["location", "ending_salary_range"]]
ending.rename(columns={"ending_salary_range": "salary"}, inplace=True)
location_box_plot_df = pd.concat([starting, ending])
# concat in hourly_rate, converting it to annual salary, assuming 40 hours per week, 48 weeks per year
# hourly = location_box_plot_df["hourly_rate"] * 40 * 48
# ending = jal_df[["location", "hour"]]
# location_box_plot_df = pd.concat([location_box_plot_df, hourly])

location_salary_box_plot = (
    alt.Chart(location_box_plot_df)
    .mark_boxplot(extent="min-max")
    .encode(
        x=alt.X("location:O", title="Location", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("salary:Q", title="Salary"),
    )
    .properties(width=600)
)
# q: what is the key combination for switching between tabs?


delta = (dt.date.today() - jal_df["application_date"].min().date()).days
if delta == 0:
    delta = 1
daily_application_average = jal_df["job_code"].count() / delta

total_applicants = pn.indicators.Number(
    name="Total Applicants",
    value=jal_df["applicants"].sum(),
    default_color="darkblue",
)

total_applications_open = pn.indicators.Number(
    name="Open Applications",
    value=jal_df[jal_df["status"] == "Open"]["job_code"].nunique(),
    default_color="darkred",
)
total_applications_closed = pn.indicators.Number(
    name="Closed Applications",
    value=jal_df[jal_df["status"] == "Closed"]["job_code"].nunique(),
    default_color="darkblue",
)


average_applicants = pn.indicators.Number(
    name="Average Applicants",
    value=round(jal_df["applicants"].sum() / jal_df["job_code"].nunique()),
    default_color="darkcyan",
)

daily_average = pn.indicators.Number(
    name="Daily Average",
    value=round(daily_application_average, 2),
    default_color="darkgreen",
)
# application_count = pn.indicators.Number(
#     name="Application Count",
#     value=jal_df["job_code"].nunique(),
#     default_color="darkred",
# )
location_count = pn.indicators.Number(
    name="Location Count",
    value=jal_df["location"].nunique(),
    default_color="green",
)
industry_count = pn.indicators.Number(
    name="Industry Count", value=jal_df["industry"].nunique(), default_color="orange"
)

salary_df = pd.DataFrame(jal_df[jal_df["starting_salary_range"].notnull()])
salary_df["average_salary"] = (
    salary_df["starting_salary_range"] + salary_df["ending_salary_range"]
) / 2
# salary_df = salary_df[["applicants", "average_salary"]]
salary_df = pd.concat(
    [
        salary_df,
        jal_df[jal_df["hourly_rate"].notnull()]  # [["applicants", "hourly_rate"]]
        .rename(columns={"hourly_rate": "average_salary"})
        .assign(average_salary=lambda df: jal_df.hourly_rate * 40 * 52),
    ]
)
# using altair create a scatter plot of salary vs applicants
# salary_df = salary_df[salary_df["average_salary"].notnull()]
salary_scatter = (
    alt.Chart(salary_df)
    .mark_point()
    .encode(
        x=alt.X("average_salary:Q", title="Salary"),
        y=alt.Y("applicants:Q", title="Applicants"),
        tooltip=["company_name", "job_title", "applicants"],
        # size="applicants:Q",
    )
    .properties(width=800, height=400)
)


# bootstrap.sidebar.append(application_count)
bootstrap.sidebar.append(total_applications_open)
bootstrap.sidebar.append(total_applications_closed)
bootstrap.sidebar.append(daily_average)
bootstrap.sidebar.append(average_applicants)
bootstrap.sidebar.append(total_applicants)
bootstrap.sidebar.append(location_count)
bootstrap.sidebar.append(industry_count)

analysis = pn.Column(
    pn.Row(pn.Spacer(height=20)),
    pn.Row(cumulative_application_chart),
    pn.Row(other_application_chart),
    pn.Row(location_salary_box_plot),
    pn.Row(company_size_donut_chart),
    pn.Row(salary_scatter),
)

bootstrap.main.append(analysis)

bootstrap.servable()
