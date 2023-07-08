import pandas as pd
import os
import panel as pn
import json
import re
import requests
import datetime as dt
from bokeh.models.widgets.tables import DateFormatter
import altair as alt

jobs_directory = "jobs"
df_filename = "JAL.json"


def directories():
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


def company_sizes():
    company_sizes = [
        "51-200 employees",
        "201-500 employees",
        "501-1,000 employees",
        "1,001-5,000 employees",
        "5,001-10,000 employees",
        "10,000+ employees",
    ]
    return company_sizes


def job_types():
    job_types = [
        "Full-time",
        "Contract",
        "Volunteer",
        "Other",
        "Part-time",
        "Temporary",
        "Internship",
    ]
    return job_types


def columns():
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
    return df_columns


directories = directories()
job_types = job_types()


def compile_dataframe():
    df = pd.DataFrame(columns=columns())
    for file in os.listdir(directories["json"]):
        if file.endswith(".json"):
            with open(os.path.join(directories["json"], file)) as f:
                new_data = pd.read_json(
                    os.path.join(directories["json"], file), orient="index"
                )
                df = pd.concat([df, new_data])
    df.to_json(df_filename, orient="index", indent=6)
    return initialize_dataframe()


def initialize_dataframe():
    if os.path.exists(df_filename):
        df = pd.read_json(df_filename, orient="index")
    else:
        df = compile_dataframe()
    # df.set_index("job_code", inplace=True, drop=False)
    df["application_date"] = pd.to_datetime(df["application_date"])
    # df["job_type"] = df["job_type"].astype("category")
    # df["company_size"] = df["company_size"].astype("category")
    # df["industry"] = df["industry"].astype("category")
    df["job_code"] = df["job_code"].astype("str")
    return df


def read_job_record(linkedin_job_code: str):
    json_filename = f"{linkedin_job_code}.json"

    if os.path.exists(os.path.join(directories["json"], json_filename)):
        with open(os.path.join(directories["json"], json_filename), "r") as f:
            job_data = json.load(f)
            f.close()

        return job_data


def write_job_record(job_data: json):
    json_filename = f"{job_data['job']['job_code']}.json"

    with open(os.path.join(directories["json"], json_filename), "w") as f:
        json_file = open(os.path.join(directories["json"], json_filename), "w")
        json.dump(job_data, json_file, indent=6)
        json_file.close()

    if os.path.exists(df_filename):
        os.remove(df_filename)
    return job_data


def materialize_job_details(linkedin_job_code, job_details):
    raw_filename = f"{linkedin_job_code}.txt"

    if not os.path.exists(os.path.join(directories["raw"], raw_filename)):
        with open(os.path.join(directories["raw"], raw_filename), "w") as f:
            f.write(job_details)
            f.close()
    return job_details


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

    if "Remote" in line2_data[1]:
        job_data["location"] = "Remote"
    else:
        search_results = re.search(r"(.*, [A-Z]{2}) .*", line2_data[1])
        if search_results:
            job_data["location"] = search_results.group(1).strip()
        else:
            job_data["location"] = "Remote"

    search_results = re.search(r"(\d+) applicants.*", line2_data[2])
    job_data["applicants"] = search_results.group(1).strip()

    # Line 3
    line3_data = lines[2].split("·")

    if len(line3_data) == 3:
        job_data["job_type"] = line3_data[1].strip()
        job_data["experience_level"] = line3_data[2].strip()
        job_data.update(parse_salary_range(line3_data[0].strip()))
    elif len(line3_data) == 1:
        if line3_data[0].strip() in job_types:
            job_data["job_type"] = line3_data[0].strip()
        else:
            job_data["experience_level"] = line3_data[0].strip()
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

    job = read_job_record(linkedin_job_code)
    if job:
        return None

    job = parse_job_details(job_details)
    job["job"]["application_date"] = application_date.strftime("%Y-%m-%d")
    job["job"]["status"] = "Open"
    job["job"]["job_code"] = linkedin_job_code
    job = write_job_record(job)

    return job


def jal_template():
    bootstrap = pn.template.BootstrapTemplate(
        title="JAL ~ Job Application Log",
        header_background="lightblue",
    )

    return bootstrap
