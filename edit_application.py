import pandas as pd
import panel as pn
import json
import datetime as dt
import os

from JAL import initialize_dataframe, jal_template, directories

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
    json_file_name = f"{job_code}.json"

    if os.path.exists(os.path.join(directories["json"], json_file_name)):
        json_file = open(os.path.join(directories["json"], json_file_name), "r")
        json_file_contents = json.load(json_file)
        json_file.close()

        json_editor = pn.widgets.JSONEditor(
            value=json_file_contents, width=600, height=600
        )
        return json_editor
    else:
        return pn.pane.Markdown("No JSON file found for this company.")


json_editor = pn.bind(load_editor, search_company)


bootstrap.main.append(search_company)
bootstrap.main.append(json_editor)


bootstrap.servable()
