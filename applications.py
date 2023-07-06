import panel as pn
from bokeh.models.widgets.tables import DateFormatter
from JAL import initialize_dataframe, jal_template

pn.extension("tabulator")
jal_df = initialize_dataframe()
bootstrap = jal_template()

sidebar_md = pn.pane.Markdown(
    """* [**New Application**](new)
* **Applications**
* [**Analytics**](analytics)
"""
)

bootstrap.sidebar.append(sidebar_md)

applications_page_header = pn.pane.Markdown(
    """
    # Job Applications
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

bootstrap.main.append(applications_page_header)
bootstrap.main.append(jobs_data_table)

pn.extension("ace", "jsoneditor")

# read a single json file from jobs/json and feed it into the below json_editor
# json_editor = pn.widgets.JSONEditor(
#     value=jal_df.to_json(orient="records"),
#     width=400,
# )


bootstrap.servable()
