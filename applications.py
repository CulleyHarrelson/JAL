import panel as pn
import json
from bokeh.models.widgets.tables import DateFormatter, HTMLTemplateFormatter
from JAL import initialize_dataframe, jal_template

pn.extension("tabulator")
pn.extension(notifications=True)

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

status_button_group = pn.widgets.RadioButtonGroup(
    name="Applcation Status",
    value="Open",
    options=["Open", "Closed"],
)


def edit_application(event):
    # pn.state.location.pathname = f"/edit_application?job_code={event.item.job_code}"

    # access the Tabulator Dataframe and put the job_code for this row into a variable
    #
    


    row = event.row
    # df = jobs_data_table.value
    # job_code = df.loc[row, "job_code"]
    # pn.state.location.pathname = f"/edit_application?job_code={job_code}"
    # return

    # df = jobs_data_table.DataTabulator
    # job_code = df.loc[row, "job_code"]
    # when the button column is clicked grab the job code and redirect to the edit page
    # pn.state.location.pathname = f"/edit_application?job_code={event.item.job_code}"
    pn.state.notifications.info(f"{event}", duration=2000)
    return


def load_data_table(status):
    # pn.state.notifications.info(f"loading data for {status}", duration=2000)
    jobs_data_table = pn.widgets.Tabulator(jal_df.loc[jal_df["status"] == status])
    jobs_data_table.selectable = True
    jobs_data_table.buttons = {"edit": '<i class="fas fa-pen"></i>'}
    jobs_data_table.show_index = False
    jobs_data_table.sorters = [{"field": "application_date", "dir": "desc"}]
    jobs_data_table.formatters = {
        "application_date": DateFormatter(),
        "edit": {
            "type": "link",
            "urlPrefix": "edit_application?job_code=",
            "urlField": "job_code",
        },
    }
    jobs_data_table.titles = {
        "job_title": "Job Title",
        "job_code": "Job Code",
        "company_name": "Company Name",
        "location": "Location",
        "application_date": "Application Date",
        "applicants": "Applicants",
    }
    jobs_data_table.hidden_columns = [
        "starting_salary_range",
        "ending_salary_range",
        "experience_level",
        "job_type",
        "company_size",
        "industry",
        "hourly_rate",
        "status",
    ]
    if status == "Open":
        jobs_data_table.hidden_columns.append("closure_date")
    else:
        jobs_data_table.titles["closure_date"] = "Closure Date"
    jobs_data_table.on_click(edit_application)

    return jobs_data_table


jobs_data_table = pn.bind(load_data_table, status_button_group)
# json_editor = pn.bind(load_editor, search_company)

# status_button_group.on_click(lambda event: print(event))


bootstrap.main.append(applications_page_header)
bootstrap.main.append(status_button_group)
bootstrap.main.append(jobs_data_table)

pn.extension("ace", "jsoneditor")

# read a single json file from jobs/json and feed it into the below json_editor
# json_editor = pn.widgets.JSONEditor(
#     value=jal_df.to_json(orient="records"),
#     width=400,
# )
#


bootstrap.servable()
