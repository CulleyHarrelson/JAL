import pandas as pd
import os
import panel as pn
import json
import re
import requests


pn.extension()
pn.config.notifications = True

# pn.state.notifications.position = "bottom-center"

jobs_directory = "jobs"


def get_directories():
    return_dict = {}
    jobs_directory = "jobs"
    return_dict["html"] = os.path.join(jobs_directory, "html")
    return_dict["raw"] = os.path.join(jobs_directory, "raw")
    return_dict["json"] = os.path.join(jobs_directory, "json")

    if not os.path.exists(jobs_directory):
        os.mkdir(jobs_directory)

    if not os.path.exists(return_dict["html"]):
        os.mkdir(return_dict["html"])

    if not os.path.exists(return_dict["raw"]):
        os.mkdir(return_dict["raw"])

    if not os.path.exists(return_dict["json"]):
        os.mkdir(return_dict["json"])
    return return_dict


directories = get_directories()


def materialize_job_details(linkedin_job_code, job_details):
    raw_filename = f"{linkedin_job_code}.txt"

    if not os.path.exists(os.path.join(directories["raw"], raw_filename)):
        with open(os.path.join(directories["raw"], raw_filename), "w") as f:
            f.write(job_details)
            f.close()
    return job_details


def parse_job_details(job_details):
    linkedin_re = r"(.*)\n([^·]+)· (.*, [A-Z]{2}) .*\n(\$[^\(]+) \(from job description\) · ([^·]+) · (.+)\n([^·]+) · (.+)\n.*"

    search_results = re.search(linkedin_re, job_details)
    job_data = {
        "job_title": search_results.group(1).strip(),
        "company_name": search_results.group(2).strip(),
        "location": search_results.group(3).strip(),
        "salary_range": search_results.group(4).strip(),
        "work_amount": search_results.group(5).strip(),
        "employment_level": search_results.group(6).strip(),
        "company_size": search_results.group(7).strip(),
        "industry": search_results.group(8).strip(),
    }
    return {"job": job_data}


def MaterializeRawHtml(linkedin_job_code):
    html_filename = f"{linkedin_job_code}.html"
    url = f"https://www.linkedin.com/jobs/view/{linkedin_job_code}"

    if os.path.exists(os.path.join(directories["html"], html_filename)):
        with open(os.path.join(directories["html"], html_filename), "rb") as f:
            contents = f.read()
    else:
        response = requests.get(url)
        with open(os.path.join(directories["html"], html_filename), "wb") as f:
            f.write(response.content)
            contents = response.content
    return contents


# def ParseLinkedInData(job_description):
def materialize_json(linkedin_job_code, job_details):
    json_filename = f"{linkedin_job_code}.json"

    if os.path.exists(os.path.join(directories["json"], json_filename)):
        with open(os.path.join(directories["json"], json_filename), "r") as f:
            job_data = json.load(f)
            return job_data
    job = parse_job_details(job_details)

    with open(os.path.join(directories["json"], json_filename), "w") as f:
        json_file = open(os.path.join(directories["json"], json_filename), "w")
        json.dump(job, json_file, indent=6)
        json_file.close()
    return job


bootstrap = pn.template.BootstrapTemplate(
    title="JAL ~ Job Application Log",
    header_background="lightblue",
)

sidebar_md = pn.pane.Markdown(
    """
describe this dashboard

"""
)

useage_md = pn.pane.Markdown(
    """
To save job details to the log you need two pieces of data:

#### LinkedIn Job Code

The **Job Code** can be found in the url for the job listing. In this example:

https://www.linkedin.com/jobs/view/1234

**1234** is the job code.

#### LinkedIn Job Details

describe job details

"""
)
useage_md.width = 920
useage_md.margin = 10

m = pn.pane.Markdown("")
job_code = pn.widgets.TextInput()
job_details = pn.widgets.TextAreaInput()
button = pn.widgets.Button(name="Add Job", button_type="primary")


def AddJobButton(event):
    if len(job_code.value) == 0:
        pn.state.notifications.error("Please enter a LinkedIn job code", duration=2000)
        return

    if len(job_details.value) == 0:
        pn.state.notifications.error(
            "Please enter a LinkedIn job details", duration=2000
        )
        return

    if len(MaterializeRawHtml(job_code.value)) > 0:
        pn.state.notifications.info(
            f"job description saved for {job_code.value}", duration=2000
        )

    if len(materialize_job_details(job_code.value, job_details.value)) > 0:
        pn.state.notifications.info(
            f"job details saved for {job_code.value}", duration=2000
        )
    else:
        pn.state.notifications.error("Unable to Parse", duration=2000)

    if len(materialize_json(job_code.value, job_details.value)) > 0:
        pn.state.notifications.info(
            f"JSON record saved for {job_code.value}", duration=2000
        )
    else:
        pn.state.notifications.error(
            "Unable to extract data for JSON record.", duration=2000
        )

    job_code.value = ""
    job_details.value = ""


button.on_click(AddJobButton)

bootstrap.sidebar.append(pn.Spacer(height=20))
bootstrap.sidebar.append(sidebar_md)

bootstrap.main.append(useage_md)
bootstrap.main.append(pn.Spacer(height=20))
bootstrap.main.append(
    pn.Row(
        pn.Column("LinkedIn Job Code", "LinkedIn Job Details"),
        pn.Column(job_code, job_details, button),
        # pn.Column(useage_md),
    )
)
bootstrap.main.append(m)

bootstrap.servable()
