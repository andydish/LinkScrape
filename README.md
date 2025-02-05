# LinkedIn Scraper with Flask

This repository contains a small Flask web application that authenticates with LinkedIn, performs staff searches for specified companies, and provides CSV export of the results. It uses the [`staffspy`](https://github.com/spencerroberts/staffspy) library and the [`linkedin_api`](https://github.com/tomquirk/linkedin-api) library.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Endpoints](#endpoints)
- [Configuration](#configuration)
- [License](#license)

---

## Features
1. **LinkedIn Login**: Logs in to LinkedIn using credentials supplied by the user.
2. **Scraping Staff Profiles**:
   - Searches for companies similar to a given target (using the `linkedin_api`).
   - Scrapes staff profiles for either a single specified company or a list of discovered companies.
3. **Scraping Specific Users**: Optionally scrape details for specific user IDs.
4. **CSV Export**: Stores the scraped data in CSV files in the user's Downloads folder (or the corresponding path depending on the operating system).
5. **Simple Flask UI**: A minimal HTML interface to control the scraping process.

---

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/<YourGitHubUsername>/linkedin-flask-scraper.git
    cd linkedin-flask-scraper
    ```

2. **Create & Activate a Virtual Environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Unix systems
    # or on Windows:
    # venv\Scripts\activate
    ```

3. **Install the Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

   Your `requirements.txt` might look like:
   ```
   Flask
   staffspy
   requests
   beautifulsoup4
   linkedin_api
   ```

4. **Set up LinkedIn credentials** (if needed):
   - By default, the code attempts to log into LinkedIn with the email and password provided in the UI.
   - If you encounter captchas often, you can configure a solver API key (e.g., `CAPSOLVER` or 2captcha) by passing them to the `LinkedInAccount` constructor.

---

## Usage

### Running the Application

1. **Start the Flask server**:
    ```bash
    python app.py
    ```
2. The server will start on port `5001` by default, and the application will open automatically in your browser at `http://127.0.0.1:5001`.

### Endpoints

| Endpoint          | Method | Description                                                                 |
|-------------------|--------|-----------------------------------------------------------------------------|
| `/`               | GET    | Splash page with a button to start.                                         |
| `/login`          | GET/POST | Displays login form. After POST with valid credentials, redirects to `/scrape`. |
| `/scrape`         | GET/POST | Displays a form for specifying the search parameters. On POST, executes the scraping and redirects to `/results/<rows_saved>`. |
| `/results/<int:rows_saved>` | GET | Shows how many rows of data were saved as a result of the scraping operation. |
| `/shutdown`       | POST   | Shuts down the Flask server (handy for local usage).                         |

**Flow**:
1. Visit the main page (`/`).
2. Click “Login” to go to `/login`.
3. Enter your LinkedIn credentials, redirect to `/scrape`.
4. Enter your search parameters:
   - Company Name
   - Industry & Limit (optional)
   - Search Term (role or position, e.g., "engineer", "marketing", etc.)
   - Location
   - Whether to gather extra profile data
   - Max results to scrape
   - User IDs (comma-separated, if you have any specific LinkedIn user IDs to scrape directly)
5. After hitting **Submit**, you’ll be redirected to the `/results/<int:rows_saved>` page indicating how many rows were saved.
6. CSV files will be saved in your Downloads folder (or corresponding path if on Windows).

---

## Configuration

The primary options to configure are:
- **LinkedIn Credentials**:
  You will be prompted to enter your email and password. 
- **Captcha Solver** *(Optional)*:
  If you need to solve captchas automatically, pass a solver API key to the `LinkedInAccount` constructor:
  ```python
  account = LinkedInAccount(
      username=email,
      password=password,
      solver_api_key="YOUR_CAPSOLVER_API_KEY",
      solver_service=SolverType.CAPSOLVER,
      session_file=str(session_file),  
      log_level=1
  )
  ```
- **Download Path**:
  By default, CSV files are saved to your system’s Downloads folder. If you need to customize this, adjust the `get_downloads_path()` function.

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as needed.

---

### Acknowledgments
- [Flask](https://flask.palletsprojects.com/) - Lightweight Python web framework.
- [staffspy](https://github.com/spencerroberts/staffspy) - Library used for staff scraping.
- [linkedin_api](https://github.com/tomquirk/linkedin-api) - Library for interacting with LinkedIn unofficially.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Library for parsing HTML and XML documents.
- [requests](https://docs.python-requests.org/) - HTTP library for Python.

---

**Enjoy Scraping Responsibly!**  
_Always comply with LinkedIn’s terms of service and scrape responsibly to avoid blocking._
