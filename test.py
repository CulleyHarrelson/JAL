import panel as pn
import param
import JAL
import datetime as dt

pn.extension(notifications=True)


class JobApplication(param.Parameterized):
    application_date = param.CalendarDate(
        default=dt.date.today(), doc="Date of resume submission"
    )
    url = param.String(
        default="",
        doc="The direct url to the job listing on the company site (not LinkedIn)",
    )
    job_title = param.String(default="", doc="Job Title")
    job_type = param.Selector(
        default=JAL.job_types[0], objects=JAL.job_types, doc="The type of role"
    )
    # experience_level = param.String(default="", doc="Experience Level")
    company_name = param.String(default="", doc="Company Name")
    company_location = param.String(default="", doc="Company Location")
    company_industry = param.String(default="", doc="Company Industry")
    company_size = param.Selector(
        default=JAL.company_sizes[0], objects=JAL.company_sizes, doc="Company Size"
    )
    starting_salary_range = param.Number(
        default=0, doc="Starting Salary Range - the low end of the range"
    )
    ending_salary_range = param.Number(
        default=0, doc="Ending Salary Range - the high end of the range"
    )
    hourly_rate = param.Number(default=0, doc="Hourly Rate")
    status = param.Selector(
        default="Open", objects=["Open", "Closed"], doc="Application Status"
    )
    applicants = param.Integer(
        default=0, doc="Number of other applicants. This is usually an estimated value"
    )

    # applicants = param.Integer(default=50000, bounds=(0, 3000))
    # unbounded_int = param.Integer(default=23)
    # hidden_parameter = param.Number(default=2.718, precedence=-1)
    # integer_range = param.Range(default=(3, 7), bounds=(0, 10))
    # dictionary = param.Dict(default={"a": 2, "b": 9})
    #


template = JAL.jal_template()

# generate a UI from the parameters in JobApplication
job = JobApplication()
job_panel = pn.Param(job)
# job_panel.show_labels = False

template.main.append(job_panel)

template.servable()
