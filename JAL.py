# import pandas as pd
import requests

# import bokeh
# import hvplot.pandas
import panel as pn

import os

# import datetime

pn.extension()


def MaterializeRawHtml(linkedin_job_code):
    html_filename = f"{linkedin_job_code}.html"
    url = f"https://www.linkedin.com/jobs/view/{linkedin_job_code}"
    jobs_directory = "jobs"

    if not os.path.exists(jobs_directory):
        os.mkdir(jobs_directory)

    if os.path.exists(os.path.join(jobs_directory, html_filename)):
        with open(os.path.join(jobs_directory, html_filename), "rb") as f:
            contents = f.read()
    else:
        response = requests.get(url)
        with open(os.path.join(jobs_directory, html_filename), "wb") as f:
            f.write(response.content)
            contents = response.content
    return contents


def ParseLinkedInData(job_description):
    linkedin_re = r"(.*)\n([^·]+)· ([^\(]+)\((.*)\).*\n(\$[^\(]+) \(from job description\) · ([^·]+) · (.+)\n([^·]+) · (.+)\n.*"

    search_results = re.search(linkedin_re, job_description)
    job_data = {
        "job_title": search_results.group(1).strip(),
        "company_name": search_results.group(2).strip(),
        "location": search_results.group(3).strip(),
        "job_type": search_results.group(4).strip(),
        "salary_range": search_results.group(5).strip(),
        "work_amount": search_results.group(6).strip(),
        "employment_level": search_results.group(7).strip(),
        "company_size": search_results.group(8).strip(),
        "industry": search_results.group(9).strip(),
    }
    return job_data


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
    main useage block
"""
)
useage_md.width = 920
useage_md.margin = 10

m = pn.pane.Markdown("")
job_code = pn.widgets.TextInput()
job_details = pn.widgets.TextAreaInput()
button = pn.widgets.Button(name="Add Job", button_type="primary")


def b(event):
    if len(MaterializeRawHtml(job_code.value)) > 0:
        m.object = "job description loaded"
    else:
        m.object = "something went wrong"


button.on_click(b)

bootstrap.sidebar.append(pn.Spacer(height=20))
bootstrap.sidebar.append(sidebar_md)

bootstrap.main.append(useage_md)
bootstrap.main.append(pn.Spacer(height=20))
bootstrap.main.append(
    pn.Row(
        pn.Column("LinkedIn Job Code", "LinkedIn Job Details"),
        pn.Column(job_code, job_details, button),
    )
)
bootstrap.main.append(m)

bootstrap.servable()
