import pandas as pd
import panel as pn
import json
import datetime as dt
import os
import param

from JAL import (
    initialize_dataframe,
    jal_template,
    directories,
    read_job_record,
    write_job_record,
)

pn.extension(notifications=True)

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


class JobApplication(param.Parameterized):
    job_code = param.String(default="", doc="LinkedIn Job Code")
    application_date = param.Date(default=dt.date.today(), doc="Application Date")
    starting_salary_range = param.Integer(default=0, doc="Starting Salary Range")
    ending_salary_range = param.Integer(default=0, doc="Ending Salary Range")
    experience_level = param.String(default="", doc="Experience Level")
    applicants = param.Integer(default=0, doc="Number of Applicants")
    job_details = param.String(default="", doc="Job Details")
    company_name = param.String(default="", doc="Company Name")
    company_location = param.String(default="", doc="Company Location")
    company_industry = param.String(default="", doc="Company Industry")
    company_size = param.String(default="", doc="Company Size")
    job_title = param.String(default="", doc="Job Title")
    job_type = param.Selector(
        default="Full-time", objects=["Full-time", "Part-time", "Contract"]
    )
    hourly_rate = param.Number(default=0, doc="Hourly Rate")
    status = param.Selector(
        default="Open", objects=["Open", "Closed"], doc="Application Status"
    )

    # applicants = param.Integer(default=50000, bounds=(0, 3000))
    # unbounded_int = param.Integer(default=23)
    # hidden_parameter = param.Number(default=2.718, precedence=-1)
    # integer_range = param.Range(default=(3, 7), bounds=(0, 10))
    # dictionary = param.Dict(default={"a": 2, "b": 9})
    #


def load_job(company_name):
    search_data = jal_df.loc[jal_df["company_name"] == company_name]
    job_code = search_data["job_code"].iloc[0]

    if job_code:
        job = JobApplication
        job.job_code = job_code
        job.applicants = int(search_data["applicants"].iloc[0])
        job.application_date = search_data["application_date"].iloc[0]
        job.starting_salary_range = int(search_data["starting_salary_range"].iloc[0])
        job.ending_salary_range = int(search_data["ending_salary_range"].iloc[0])
        job.company_name = search_data["company_name"].iloc[0]
        job.location = search_data["location"].iloc[0]
        job.job_title = search_data["job_title"].iloc[0]
        job.industry = search_data["industry"].iloc[0]
        # if search_data["hourly_rate"].iloc[0] is not None:
        #     job.hourly_rate = float(search_data["hourly_rate"].iloc[0])
        # job.job_type = search_data["job_type"].iloc[0]
        # job.experience_level = search_data["experience_level"].iloc[0]
        # job.company_size = search_data["company_size"].iloc[0]
        # job.status = search_data["status"].iloc[0]
        # # job.closure_date = search_data["closure_date"].iloc[0]
        # if search_data["status"].iloc[0] is not "Open":
        #     job.closure_date = search_data["closure_date"].iloc[0]

        return job


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
job_editor = pn.bind(load_job, search_company)


def save_record(event):
    # if not x:
    pn.state.notifications.error("No JSON data found.", duration=2000)
    return

    job_data = job_editor.value
    # job = write_job_record(job_data)
    # pn.state.notifications.info(job_data, duration=2000)
    pn.state.notifications.info("job details saved", duration=2000)
    return job_data


save_button.on_click(save_record)


class Stage1(param.Parameterized):
    # a = param.Integer(default=2, bounds=(0, 10))
    # b = param.Integer(default=3, bounds=(0, 10))
    company_name = param.ObjectSelector(
        default="Meta", objects=jal_df["company_name"].unique().tolist()
    )

    @param.output(("c", param.String))
    def output(self):
        return self.company_name.value

    @param.depends("company_name")
    def panel(self):
        return pn.Row(
            self.param,
        )


class Stage2(param.Parameterized):
    c = param.String(default="Meta", doc="A string")

    @param.depends("c")
    def view(self):
        pn.state.notifications.info("in stage2 view", duration=2000)
        return pn.Column(c.value, margin=(40, 10), styles={"background": "#f0f0f0"})

    def panel(self):
        return pn.Row(self.param, self.view)


# bootstrap.main.append(search_company)
# bootstrap.main.append(job_editor)
# bootstrap.main.append(JobApplication)
# bootstrap.main.append(save_button)
stage1 = Stage1()
stage2 = Stage2()

pipeline = pn.pipeline.Pipeline()
pipeline.add_stage("Stage 1", Stage1)
pipeline.add_stage("Stage 2", Stage2)

bootstrap.main.append(pipeline)

bootstrap.servable()
