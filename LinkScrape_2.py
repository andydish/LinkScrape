from pathlib import Path
from staffspy import LinkedInAccount, SolverType
from flask import Flask, request, render_template, redirect, url_for, debughelpers
import os
import webbrowser
from threading import Timer
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from linkedin_api import Linkedin

def get_linkedin_page(keyword):
    urls_to_drop = ['https://support.google.com/websearch?p=ws_settings_location&hl=en',
                    'https://support.google.com/websearch?p=ws_settings_location&hl=en-CA']
    url = f"https://www.google.com/search?q={keyword}+linkedin"
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first link in the response and extract the actual LinkedIn URL
    for link in soup.find_all('a', href=True):
        parsed_link = urlparse(link['href'])
        query_string = parse_qs(parsed_link.query)
        actual_url = query_string.get('q')  # 'q' is typically the key for the actual URL in Google's redirect URLs

        if actual_url:
            actual_url = actual_url[0]  # 'q' returns a list, but we want the first (and usually only) element
            # Check if the URL is a LinkedIn URL and not in the drop list
            if "linkedin.com" in actual_url and actual_url not in urls_to_drop:
                print(actual_url)
                return actual_url

def find_similar_companies(limit, company_name: str):
    try:
        # Initialize the LinkedIn API client with your credentials
        linkedin = Linkedin(username='andrewdish@gmail.com', password='Apple1994jacks!')

        # Define keywords for the search; you might want to refine these keywords based on your needs
        keywords = [company_name]

        # Search for companies using the provided keywords
        companies = linkedin.search_companies(limit, keywords=keywords)

        # Process and return the search results
        return companies

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

app = Flask(__name__)

def get_downloads_path():
    """Returns the default downloads path for the current user."""
    if os.name == 'nt':  # Windows
        return str(Path.home() / "Downloads")
    else:  # MacOS, Linux, etc.
        return str(Path.home() / "Downloads")

@app.route("/")
def splash():
    return render_template('splash.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['Linkedin Login Email']
        password = request.form['Password']
        if email and password:
            session_file = Path(__file__).resolve().parent / "session.pkl"
            global account
            account = LinkedInAccount(
                username=email,
                password=password,
                # solver_api_key="CAP-6D6A8CE981803A309A0D531F8B4790BC",  # optional but needed if hit with captcha
                # solver_service=SolverType.CAPSOLVER,
                session_file=str(session_file),  # save login cookies to only log in once (lasts a week or so)
                log_level=1,  # 0 for no logs
            )
            return redirect(url_for('scrape'))
        else:
            error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/scrape', methods=['POST', 'GET'])
def scrape():
    if request.method == 'GET':
        return render_template('scrape.html')

    if 'account' not in globals():
        return redirect(url_for('login'))

    industry = request.form['search_industry']
    industry_limit = request.form['industry_limit']
    company_name = request.form['company_name']
    search_term = request.form['search_term']
    location = request.form['location']
    extra_profile_data = request.form.get('extra_profile_data') == 'on'
    max_results = int(request.form['max_results'])
    user_ids = request.form['user_ids'].split(',')
    save_path = get_downloads_path()

    rows_saved = 0
    if industry:
        industry_search = str(industry) + " companies"
        similar_companies = find_similar_companies(company_name = industry_search, limit = industry_limit)
        print(similar_companies)
        for company in similar_companies:
            print(company['name'])
            # linkedin_url = get_linkedin_page(company['name'])
            # path = urlparse(linkedin_url).path  # Extracts the path '/path/to/resource'
            # company_name_from_page = path.split('/')[-1]
            # print(company_name_from_page)
            try:
                company_name_industry = str(company['name'])
                staff = account.scrape_staff(
                    company_name=company_name_industry,
                    search_term=search_term,
                    location=location,
                    extra_profile_data=extra_profile_data,
                    max_results=max_results,
                )
                if not staff.empty:
                    staff_file = Path(save_path) / f"linkscrape_results_staff_{company_name_industry}.csv"
                    staff.to_csv(staff_file, index=False)
                    rows_saved += len(staff)
                else:
                    print(f"No data to save for {company_name_industry}. Skipping save.")

            except Exception as e:
                print(e)
                continue

    if company_name:
        staff = account.scrape_staff(
            company_name=company_name,
            search_term=search_term,
            location=location,
            extra_profile_data=extra_profile_data,
            max_results=max_results,
        )
        staff_file = Path(save_path) / "linkscrape_results_staff.csv"
        staff.to_csv(staff_file, index=False)
        rows_saved += len(staff)

    if user_ids:
        users = account.scrape_users(
            user_ids=user_ids
        )
        users_file = Path(save_path) / "linkscrape_results_users.csv"
        users.to_csv(users_file, index=False)
        rows_saved += len(users)

    return redirect(url_for('results', rows_saved=rows_saved))


@app.route('/results/<int:rows_saved>')
def results(rows_saved):
    return render_template('results.html', rows_saved=rows_saved)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5001")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(port=5001)

