# Job Scraping Application

This Python application is designed to scrape job data from various websites (LinkedIn Jobs, LinkedIn Posts, Indeed.com, Internshala.com), compile the data, and save it into an Excel file. It also features a graphical user interface (GUI) for user input of job designation and city.

## Project Structure

- `job_scraper_project/`: Main directory for the application code.
  - `main.py`: Entry point for the application; initializes the GUI and WebDriver.
  - `gui.py`: Contains the Tkinter-based GUI for user interaction.
  - `scraper.py`: Houses all the web scraping logic for different job sites using Selenium and BeautifulSoup.
  - `excel_handler.py`: Manages the creation of the Excel file from scraped data using pandas.
- `requirements.txt`: Lists necessary Python packages.
- `README.md`: This file.

## Setup and Installation

1.  **Python:** Ensure Python 3.10 or newer is installed.
2.  **Clone Repository:** (If applicable) `git clone <repository_url>`
3.  **Navigate to Project Root:** `cd <project_directory>`
4.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
5.  **Install Dependencies:**
    ```bash
    pip install -r job_scraper_project/requirements.txt
    ```
6.  **WebDriver:**
    - Download the appropriate ChromeDriver for your version of Google Chrome.
    - Ensure `chromedriver.exe` (or `chromedriver` on Linux/macOS) is either:
      - In your system's PATH.
      - In the same directory as `main.py` (or where the final executable would reside).

## Intended Usage

To run the application with the GUI:
```bash
python job_scraper_project/main.py
```
Enter the desired job "Designación" (Designation) and "Ciudad" (City) in the input fields and click "Buscar" (Search). The application will then scrape data from the configured websites, and if successful, save the results in an Excel file named `job_listings_[DESIGNATION]_[CITY]_[TIMESTAMP].xlsx` in the root project directory.

## Known Issues and Limitations (IMPORTANT)

This project was developed in a restricted cloud environment, which led to several critical issues:

1.  **GUI Functionality (Tkinter):**
    - **Error:** `ModuleNotFoundError: No module named 'tkinter'` was encountered persistently in the development environment.
    - **Impact:** The graphical user interface could not be tested or verified. The code for `gui.py` has been written as per requirements but may need debugging in a standard Python environment with a working Tkinter installation.

2.  **Executable Creation (.exe with PyInstaller):**
    - **Error:** PyInstaller failed with `PythonLibraryNotFoundError: ERROR: Python library not found: libpython3.10.so`. This is in addition to the Tkinter issue which would also affect GUI executables.
    - **Impact:** A standalone executable (`.exe`) could not be created.

3.  **Scraper Functionality:**
    - **Indeed.com:** The scraper for Indeed.com (`scrape_indeed`) is **currently not functional**. It fails to find job listings, likely due to outdated HTML selectors or advanced anti-scraping measures (e.g., JavaScript challenges, CAPTCHA, IP blocking). This requires significant updates to its selectors and potentially more robust scraping techniques.
    - **LinkedIn Posts:** The `scrape_linkedin_posts` function is very basic. Reliable scraping of LinkedIn posts typically requires an **authenticated (logged-in) session**, which is not handled by this script. Results may be limited or inaccurate.
    - **General Scraper Fragility:** All web scrapers are susceptible to breaking if the target websites change their HTML structure. The selectors in `scraper.py` may need frequent updates.

4.  **WebDriver Dependency:** The application relies on an external `chromedriver` executable. This must be correctly set up by the user.

## Development Notes

- The scraping logic for LinkedIn Jobs and Internshala showed initial promise during component testing but should also be regularly verified.
- The `excel_handler.py` module for saving data to Excel was tested and functions correctly.
- The application is structured to run scraping tasks in a separate thread to keep the GUI responsive (this aspect is untested due to the Tkinter issue).

---
This `README.md` provides a summary. For detailed code, please refer to the respective `.py` files.
