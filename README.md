# Job Application Log - JAL

The goal of this project is to allow for quickly saving the job description details associated with a job application and then to do analysis on the data collected.

The notebook JobAppLog.ipynb compliments the main JAL.py dashboard - it is used for development and testing.

To start the dashboard, open your terminal, navigate to a good folder and execute these commands:

git clone https://github.com/CulleyHarrelson/JAL.git
cd JAL
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
panel serve --show --autoreload JAL.py
