import requests
import constants
import openai
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import bs4
from bs4.element import Comment


def tag_visible(element):
    if element.parent.name in ["style", "script", "head", "[document]"]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def url_to_plaintext(url):
    response = requests.get(url)
    contents = response.content

    soup = bs4.BeautifulSoup(contents, "html.parser")

    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)

    return plaintext


# jd = beautiful_soup_test('jobs/html/3656898068.html')
# jd = html_to_plaintext('jobs/html/3634670029.html')


# contains an iframe, cant find location
# jd = url_to_plaintext('https://c3.ai/job-description/?gh_jid=4112793002')
def main():
    jd = url_to_plaintext("https://careers.roblox.com/jobs/5024558")
    # jd = url_to_plaintext('https://careers.adobe.com/us/en/job/R137607/Associate-Senior-Legal-Counsel-EDX-DEALS-group')

    tools = load_tools(["serpapi"], llm=llm)

    llm = OpenAI(openai_api_key=constants.APIKEY, temperature=0.9)
    prompt_text = """The text that follows is a job description from a company careers page. BeautifulSoup4
    has been used to remove the html.  At the top is the meta tags and page title, followed by the body of the web page.
    Return a json dictionary with these fields: company_name, city_state, job_title, low_salary_range, high_salary_range
    Here is the job description {job_description}"""
    prompt = PromptTemplate.from_template(prompt_text)
    chain = LLMChain(llm=llm, prompt=prompt)
    job_data = chain.run(jd)
    # agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    # jd
    job_data


if __name__ == "__main__":
    # execute only if run as a script
    main()

# jd
