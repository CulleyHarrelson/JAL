import pandas as pd
import os
import panel as pn
import json
import re
import requests
import datetime as dt

pn.extension()
pn.extension("tabulator")
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


df_filename = "JAL.json"
directories = get_directories()

job_types = [
    "Full-time",
    "Contract",
    "Volunteer",
    "Other",
    "Part-time",
    "Temporary",
    "Internship",
]


def compile_dataframe():
    df_columns = [
        "job_code",
        "job_title",
        "company_name",
        "location",
        "starting_salary_range",
        "ending_salary_range",
        "experience_level",
        "job_type",
        "company_size",
        "industry",
        "application_date",
        "applicants",
    ]
    df = pd.DataFrame(columns=df_columns)
    for file in os.listdir(directories["json"]):
        if file.endswith(".json"):
            with open(os.path.join(directories["json"], file)) as f:
                new_data = pd.read_json(
                    os.path.join(directories["json"], file), orient="index"
                )
                df = pd.concat([df, new_data])
    df.set_index("job_code", inplace=True, drop=False)
    df.to_json(df_filename, orient="index", indent=6)
    return initialize_dataframe()


def initialize_dataframe():
    if os.path.exists(df_filename):
        df = pd.read_json(df_filename, orient="index")
    else:
        df = pd.DataFrame()
    # df.set_index("job_code", inplace=True, drop=False)
    df["application_date"] = pd.to_datetime(df["application_date"])
    df["job_type"] = df["job_type"].astype("category")
    df["company_size"] = df["company_size"].astype("category")
    df["industry"] = df["industry"].astype("category")
    df["job_code"] = df["job_code"].astype("str")
    return df  # , df[["job_code", "job_title", "company_name", "application_date"]]


jal_df = initialize_dataframe()


def materialize_job_details(linkedin_job_code, job_details):
    raw_filename = f"{linkedin_job_code}.txt"

    if not os.path.exists(os.path.join(directories["raw"], raw_filename)):
        with open(os.path.join(directories["raw"], raw_filename), "w") as f:
            f.write(job_details)
            f.close()
    return job_details


# Contract Full-time
def parse_salary_range(salary_range):
    return_value = {}
    salary_re = r"(\$[^\(]+).*"
    search_results = re.search(salary_re, salary_range)
    salary = search_results.group(1).strip()
    if salary.endswith("/hr"):
        pattern = r"\$(\d+\.\d+)/hr"
        match = re.match(pattern, salary)
        return_value["hourly_rate"] = float(match.group(1))
    else:
        pattern = r"\$(\d+?,\d+)/yr - \$(\d+?,\d+)/yr"
        match = re.match(pattern, salary)

        return_value["starting_salary_range"] = match.group(1).replace(",", "")
        return_value["ending_salary_range"] = match.group(2).replace(",", "")
    return return_value


def parse_job_details(job_details):
    lines = job_details.splitlines()
    job_data = {}

    # Line 1
    job_data["job_title"] = lines[0].strip()

    # Line 2
    line2_data = lines[1].split("·")
    job_data["company_name"] = line2_data[0].strip()

    search_results = re.search(r"(.*, [A-Z]{2}) .*", line2_data[1])
    job_data["location"] = search_results.group(1).strip()

    search_results = re.search(r"(\d+) applicants.*", line2_data[2])
    job_data["applicants"] = search_results.group(1).strip()

    # Line 3
    line3_data = lines[2].split("·")

    if len(line3_data) == 3:
        job_data["job_type"] = line3_data[1].strip()
        job_data["experience_level"] = line3_data[2].strip()
        job_data.update(parse_salary_range(line3_data[0].strip()))
    else:
        if line3_data[0].strip() in job_types:
            job_data["job_type"] = line3_data[0].strip()
            job_data["experience_level"] = line3_data[1].strip()
        else:
            job_data.update(parse_salary_range(line3_data[0].strip()))
            if line3_data[1].strip() in job_types:
                job_data["job_type"] = line3_data[1].strip()
            else:
                job_data["experience_level"] = line3_data[1].strip()

    # Line 4
    line4_data = lines[3].split("·")
    job_data["company_size"] = line4_data[0].strip()
    job_data["industry"] = line4_data[1].strip()

    return {"job": job_data}


def materialize_html(linkedin_job_code):
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


def materialize_json(linkedin_job_code, job_details, application_date):
    json_filename = f"{linkedin_job_code}.json"

    if os.path.exists(os.path.join(directories["json"], json_filename)):
        with open(os.path.join(directories["json"], json_filename), "r") as f:
            job_data = json.load(f)
            return job_data
    job = parse_job_details(job_details)
    job["job"]["application_date"] = application_date.strftime("%Y-%m-%d")
    job["job"]["job_code"] = linkedin_job_code

    with open(os.path.join(directories["json"], json_filename), "w") as f:
        json_file = open(os.path.join(directories["json"], json_filename), "w")
        json.dump(job, json_file, indent=4)
        json_file.close()
    return job


bootstrap = pn.template.BootstrapTemplate(
    title="JAL ~ Job Application Log",
    header_background="lightblue",
)

sidebar_md = pn.pane.Markdown(
    """[**JAL Home**](https://github.com/CulleyHarrelson/JAL)
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

m = pn.pane.Markdown("")
job_code = pn.widgets.TextInput()
job_details = pn.widgets.TextAreaInput()
button = pn.widgets.Button(name="Save", button_type="primary")
application_date = pn.widgets.DatePicker(value=dt.date.today())
date_range_slider = pn.widgets.DateRangeSlider(
    name="Reporting Range",
    start=dt.datetime(2017, 1, 1),
    end=dt.datetime(2019, 1, 1),
    value=(dt.datetime(2017, 1, 1), dt.datetime(2018, 1, 10)),
    step=24 * 3600 * 2 * 1000,
)
# ,
jobs_data_table = pn.widgets.Tabulator(jal_df)


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
            "Unable to extract data for JSON record.", duration=2000
        )
    job_code.value = ""
    job_details.value = ""
    jal_df = compile_dataframe()


button.on_click(save_record)

bootstrap.sidebar.append(sidebar_md)
bootstrap.sidebar.append(date_range_slider)
application_count = pn.indicators.Number(
    name="Application Count", value=12, default_color="darkred"
)
location_count = pn.indicators.Number(
    name="Location Count", value=5, default_color="green"
)
industry_count = pn.indicators.Number(
    name="Industry Count", value=2, default_color="orange"
)
bootstrap.sidebar.append(application_count)
bootstrap.sidebar.append(location_count)
bootstrap.sidebar.append(industry_count)

bootstrap.main.append(pn.Spacer(height=20))
bootstrap.main.append(
    pn.Column(
        pn.Row(add_job_header),
        pn.Row(
            pn.Column("Application Date", "LinkedIn Job Code", "LinkedIn Job Details"),
            pn.Column(application_date, job_code, job_details, button),
            pn.Column(useage_md),
        ),
        pn.Row(jobs_data_table),
    )
)
bootstrap.main.append(m)

bootstrap.servable()
