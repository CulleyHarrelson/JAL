import pandas as pd
import panel as pn
import json
import datetime as dt

from JAL import *

pn.extension(notifications=True)

jal_df = initialize_dataframe()

bootstrap = jal_template()

sidebar_md = pn.pane.Markdown(
    """* **New Application**
* [**Applications**](applications)
* [**Analytics**](analytics)
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


job_code = pn.widgets.TextInput()
job_details = pn.widgets.TextAreaInput()
add_button = pn.widgets.Button(name="Save", button_type="primary")
application_date = pn.widgets.DatePicker(value=dt.date.today())


def save_record(event):
    if len(job_code.value) == 0:
        pn.state.notifications.error("Please enter a LinkedIn job code", duration=2000)
        return

    if len(job_details.value) == 0:
        pn.state.notifications.error(
            "Please enter a LinkedIn job details", duration=2000
        )
        return

    if len(materialize_html(job_code.value)) > 0:
        pn.state.notifications.info(
            f"job description saved for {job_code.value}", duration=2000
        )

    if len(materialize_job_details(job_code.value, job_details.value)) > 0:
        pn.state.notifications.info(
            f"job details saved for {job_code.value}", duration=2000
        )
    else:
        pn.state.notifications.error("Unable to Parse", duration=2000)

    json = materialize_json(job_code.value, job_details.value, application_date.value)
    if len(json) > 0:
        pn.state.notifications.info(
            f"JSON record created for {job_code.value}", duration=2000
        )
    else:
        pn.state.notifications.error(
            "does this record already exist?  Save unsuccessful.", duration=2000
        )
    job_code.value = ""
    job_details.value = ""
    compile_dataframe()
    #bootstrap.param.trigger("object")


add_button.on_click(save_record)

bootstrap.sidebar.append(sidebar_md)

data_entry = pn.Column(
    pn.Row(pn.Spacer(height=20)),
    pn.Row(add_job_header),
    pn.Row(
        pn.Column("Application Date", "LinkedIn Job Code", "LinkedIn Job Details"),
        pn.Column(application_date, job_code, job_details, add_button),
        pn.Column(useage_md),
    ),
)

bootstrap.main.append(data_entry)

bootstrap.servable()
