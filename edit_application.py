import pandas as pd
import panel as pn
import json
import datetime as dt
import os

from JAL import (
    initialize_dataframe,
    jal_template,
    directories,
    read_job_record,
    write_job_record,
)

pn.extension()
pn.config.notifications = True

jal_df = initialize_dataframe()

bootstrap = jal_template()

sidebar_md = pn.pane.Markdown(
    """* **Edit Application**
* [**Applications**](applications)
* [**Analytics**](analytics)
"""
)
bootstrap.sidebar.append(sidebar_md)
search_company = pn.widgets.Select(
    name="Select a Company",
    options=jal_df["company_name"].unique().tolist(),
)


def load_editor(company_name):
    search_data = jal_df.loc[jal_df["company_name"] == company_name]
    job_code = search_data["job_code"].iloc[0]

    if job_code:
        job = read_job_record(job_code)
        if job:
            json_editor = pn.widgets.JSONEditor(
                value=job, mode="code", width=600, height=600
            )
            return json_editor
        else:
            return pn.pane.Markdown("No JSON file found for this company.")


def load_job_code(company_name):
    search_data = jal_df.loc[jal_df["company_name"] == company_name]
    job_code = search_data["job_code"].iloc[0]

    if job_code:
        job = read_job_record(job_code)
        if job:
            job_code = pn.widgets.TextInput()
            job_code.value = job["job"]["job_code"]
            return job_code
        else:
            return pn.pane.Markdown("No JSON file found for this company.")


save_button = pn.widgets.Button(name="Save", button_type="primary")
json_editor = pn.bind(load_editor, search_company)
x = json_editor


def save_record(event):
    # if not x:
    pn.state.notifications.error("No JSON data found.", duration=2000)
    return

    job_data = json_editor.value
    # job = write_job_record(job_data)
    # pn.state.notifications.info(job_data, duration=2000)
    pn.state.notifications.info("job details saved", duration=2000)
    return job_data


save_button.on_click(save_record)

bootstrap.main.append(search_company)
bootstrap.main.append(json_editor)
bootstrap.main.append(save_button)


bootstrap.servable()
