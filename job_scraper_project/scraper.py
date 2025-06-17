"""Collection of web scraping utilities for job sites."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Added TimeoutException
from bs4 import BeautifulSoup
import time
import requests
from urllib.parse import quote_plus # Added for URL encoding

# Optional AI helpers for advanced text interpretation
try:
    from .ai_utils import (
        extract_fields_from_text,
        classify_content,
        translate_text,
        generalise_selector,
        normalise_date,
    )
except Exception:
    extract_fields_from_text = None  # type: ignore
    classify_content = None  # type: ignore
    translate_text = None  # type: ignore
    generalise_selector = None  # type: ignore
    normalise_date = None  # type: ignore

def initialize_driver(webdriver_path: str = 'chromedriver'):
    """Create and configure the Selenium WebDriver instance."""
    options = ChromeOptions()
    # options.add_argument("--headless") # Uncomment for headless browsing
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    # Add more options as needed, e.g., for proxies

    try:
        # For newer Selenium versions that might use Service object
        # Check if webdriver_path is needed or if it's in PATH
        # service = ChromeService(executable_path=webdriver_path)
        # driver = webdriver.Chrome(service=service, options=options)
        # For simplicity if chromedriver is in PATH or using WebDriverManager later:
        # Use the default chromedriver from PATH. In a real deployment the path
        # could be parameterised or managed by WebDriverManager.
        driver = webdriver.Chrome(options=options)
        print("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Please ensure that chromedriver is in your PATH or specify its location.")
        return None

def scrape_linkedin_jobs(driver, designation, city):
    """Scrape job listings from LinkedIn's public job board."""
    print(f"Scraping LinkedIn Jobs for: {designation} in {city}")
    job_data = []

    # Format for URL: keywords for designation, location for city
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(designation)}&location={quote_plus(city)}&f_TPR=r86400" # f_TPR=r86400 for past 24 hours

    try:
        driver.get(search_url)
        print(f"Navigated to: {search_url}")
        # Wait for job cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
        )
        print("Job results list found.")

        # Scroll to load more jobs
        for _ in range(3):  # Scroll a few times to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print("Scrolled down.")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("div", class_=["base-card", "job-card-container--clickable"])

        print(f"Found {len(job_cards)} job cards.")

        for card in job_cards:
            job_title_elem = card.find("h3", class_="base-search-card__title")
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            if not company_elem:
                company_elem = card.find("a", class_="hidden-nested-link")
            location_elem = card.find("span", class_="job-search-card__location")
            job_url_elem = card.find("a", class_="base-card__full-link")

            job_title = job_title_elem.get_text(strip=True) if job_title_elem else "N/A"
            company_name = company_elem.get_text(strip=True) if company_elem else "N/A"
            job_location = location_elem.get_text(strip=True) if location_elem else "N/A"
            job_url = job_url_elem['href'] if job_url_elem and job_url_elem.has_attr('href') else "N/A"

            if job_url != "N/A" and not job_url.startswith("http"):
                job_url = "https://www.linkedin.com" + job_url

            job_entry = {
                "Designación": job_title,
                "Nombre de la empresa": company_name,
                "Ciudad": job_location,
                "Email": "",
                "Teléfono": "",
                "URL de la oferta": job_url
            }
            job_data.append(job_entry)
            # print(f"Added job: {job_title}")

    except TimeoutException:
        print("Timeout waiting for LinkedIn job page elements to load.")
    except Exception as e:
        print(f"An error occurred while scraping LinkedIn Jobs: {e}")

    print(f"Finished scraping LinkedIn. Found {len(job_data)} jobs.")
    return job_data

def scrape_indeed(driver, designation, city):
    """Scrape job results from Indeed using requests with a fallback to Selenium."""
    print(f"Scraping Indeed for: {designation} in {city}")
    job_data = []
    search_url = f"https://www.indeed.com/jobs?q={quote_plus(designation)}&l={quote_plus(city)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    try:
        print(f"Attempting to fetch Indeed with requests: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        if soup.title and "Just a moment..." in soup.title.string:
            print("Indeed is presenting a 'Just a moment...' page with requests. Falling back to Selenium.")
            driver.get(search_url)
            print(f"Navigated to: {search_url} with Selenium")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2.jobTitle > a[data-jk], a.jcs-JobTitle")) # Common selectors for job links/titles
            )
            print("Indeed job titles/links found.")

            try:
                pop_up_close_button = driver.find_element(By.CSS_SELECTOR, "button.popover-x-button-close, button.icl-CloseButton, [aria-label='close'], [aria-label='Close']")
                if pop_up_close_button:
                    pop_up_close_button.click()
                    print("Closed a pop-up on Indeed.")
                    time.sleep(2)
            except Exception:
                print("No pop-up found or could not close it after Selenium load.")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            if soup.title and "Just a moment..." in soup.title.string:
                 print("Still on 'Just a moment...' page after Selenium attempt. Scraping might be blocked.")
                 return job_data

        job_cards = soup.find_all("div", class_="job_seen_beacon")
        if not job_cards:
            job_cards = soup.select('td.resultContent')
            if not job_cards:
                job_cards = soup.find_all("div", class_=lambda x: x and ("jobsearch-SerpJobCard" in x or "tapItem" in x))

        print(f"Found {len(job_cards)} job cards on Indeed.")

        for card in job_cards:
            job_title_elem = card.find("h2", class_=lambda x: x and "jobTitle" in x)
            if job_title_elem and job_title_elem.find("a"):
                job_title_elem = job_title_elem.find("a")
            elif job_title_elem and job_title_elem.find("span", {"aria-hidden": "true"}):
                job_title_elem = job_title_elem.find("span", {"aria-hidden": "true"})

            company_elem = card.find("span", {"data-testid": "company-name"})
            if not company_elem:
                company_elem = card.find("span", class_="companyName")

            location_elem = card.find("div", {"data-testid": "text-location"})
            if not location_elem:
                location_elem = card.find("div", class_="companyLocation")

            job_title = job_title_elem.get_text(strip=True) if job_title_elem else "N/A"
            company_name = company_elem.get_text(strip=True) if company_elem else "N/A"
            job_location = location_elem.get_text(strip=True) if location_elem else "N/A"

            job_url = "N/A"
            if job_title_elem and hasattr(job_title_elem, 'attrs') and 'href' in job_title_elem.attrs:
                 raw_url = job_title_elem['href']
                 if raw_url.startswith("/"):
                     job_url = "https://www.indeed.com" + raw_url
                 else:
                     job_url = raw_url
            elif card.select_one('h2.jobTitle > a[data-jk]'):
                job_url_elem = card.select_one('h2.jobTitle > a[data-jk]')
                raw_url = job_url_elem['href']
                if raw_url.startswith("/"):
                    job_url = "https://www.indeed.com" + raw_url
                else:
                    job_url = raw_url
            elif card.find("a", class_="jcs-JobTitle"):
                job_url_elem = card.find("a", class_="jcs-JobTitle")
                raw_url = job_url_elem['href']
                if raw_url.startswith("/"):
                    job_url = "https://www.indeed.com" + raw_url
                else:
                    job_url = raw_url

            job_entry = {
                "Designación": job_title,
                "Nombre de la empresa": company_name,
                "Ciudad": job_location,
                "Email": "",
                "Teléfono": "",
                "URL de la oferta": job_url
            }
            job_data.append(job_entry)

    except requests.exceptions.RequestException as e:
        print(f"Request to Indeed failed: {e}")
    except TimeoutException:
        print("Timeout waiting for Indeed job page elements to load.")
    except Exception as e:
        print(f"An error occurred while scraping Indeed: {e}")

    print(f"Finished scraping Indeed. Found {len(job_data)} jobs.")
    return job_data

def scrape_internshala(driver, designation, city):
    """Scrape internship opportunities from Internshala."""
    print(f"Scraping Internshala for: {designation} in {city}")
    job_data = []

    search_query = f"{designation} {city}".strip()
    search_url = f"https://internshala.com/internships/keywords-{quote_plus(search_query)}"

    try:
        driver.get(search_url)
        print(f"Navigated to: {search_url}")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "internship_list_container"))
        )
        print("Internshala internship list container found.")

        no_results_elem_tuple = (By.ID, "no_result_found_header")
        if driver.find_elements(*no_results_elem_tuple):
            print(f"No results found on Internshala for keywords: {search_query}")
            return job_data

        soup = BeautifulSoup(driver.page_source, "html.parser")
        internship_cards = soup.find_all("div", class_=lambda x: x and "individual_internship" in x.split())

        if not internship_cards:
             internship_cards = soup.select(".internship_meta")

        print(f"Found {len(internship_cards)} internship cards on Internshala.")

        for card in internship_cards:
            title_elem = card.find(["div", "h3"], class_=["profile", "heading_4_5", "job-internship-name"])
            company_elem = card.find(["div","a"], class_=["company_name", "heading_6", "link_display_like_text"])

            location_text = "N/A"
            location_container = card.find("div", id=lambda x: x and x.startswith("location_names"))
            if location_container:
                locations = location_container.find_all("a", class_="location_link")
                if locations:
                    location_text = ", ".join([loc.get_text(strip=True) for loc in locations])
                elif location_container.get_text(strip=True):
                    location_text = location_container.get_text(strip=True)
            elif card.find("a", class_="location_link"):
                location_text = card.find("a", class_="location_link").get_text(strip=True)

            url_elem = card.find("a", class_="view_detail_button")
            if not url_elem:
                title_link = title_elem.find("a") if title_elem else None
                if title_link and title_link.has_attr("href"):
                    url_elem = title_link
                elif card.has_attr("data-href"):
                     raw_url = card['data-href']
                     job_url = "https://internshala.com" + raw_url if raw_url.startswith("/") else raw_url
                elif card.find("a", href=True):
                    url_elem = card.find("a", href=True)

            job_title = title_elem.get_text(strip=True) if title_elem else "N/A"
            company_name = company_elem.get_text(strip=True).split('|')[0].strip() if company_elem else "N/A"

            job_url = "N/A"
            if url_elem and url_elem.has_attr('href'):
                raw_url = url_elem['href']
                if raw_url.startswith("/"):
                    job_url = "https://internshala.com" + raw_url
                else:
                    job_url = raw_url

            job_entry = {
                "Designación": job_title,
                "Nombre de la empresa": company_name,
                "Ciudad": location_text,
                "Email": "",
                "Teléfono": "",
                "URL de la oferta": job_url
            }
            job_data.append(job_entry)

    except TimeoutException:
        print(f"Timeout waiting for Internshala page elements for {search_query}.")
    except Exception as e:
        print(f"An error occurred while scraping Internshala: {e}")

    print(f"Finished scraping Internshala. Found {len(job_data)} items.")
    return job_data

def scrape_linkedin_posts(driver, designation, city):
    """Very lightweight scraping of public LinkedIn posts mentioning the role."""
    print(f"Scraping LinkedIn Posts for: {designation} in {city} (Basic Attempt)")
    job_data = []

    search_keywords = f"hiring {designation} {city}".strip()
    search_url = f"https://www.linkedin.com/search/results/content/?keywords={quote_plus(search_keywords)}&origin=GLOBAL_SEARCH_HEADER&sid=~"

    try:
        driver.get(search_url)
        print(f"Navigated to LinkedIn Posts search (may require login): {search_url}")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "reusable-search__entity-result-list"))
        )
        print("LinkedIn posts search results container found.")

        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print("Scrolled down on posts search.")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        post_elements = soup.select("li.reusable-search__result-container")
        if not post_elements:
            post_elements = soup.select("div.feed-shared-update-v2")

        print(f"Found {len(post_elements)} potential post elements.")

        for post_elem in post_elements[:10]:
            post_text_content = ""
            text_box = post_elem.find("div", class_=["feed-shared-update-v2__description-wrapper", "update-components-text"])
            if text_box:
                actual_text_span = text_box.find("span", dir="ltr")
                if actual_text_span:
                     post_text_content = actual_text_span.get_text(strip=True)

            if not post_text_content:
                post_text_content = post_elem.get_text(strip=True)

            post_url = "N/A"
            permalink_tag = post_elem.find("a", href=lambda href: href and ("urn:li:activity:" in href or "feed_highlight" in href) )
            if permalink_tag:
                raw_url = permalink_tag['href']
                if raw_url.startswith("/"):
                    post_url = "https://www.linkedin.com" + raw_url
                else:
                    post_url = raw_url

            extracted_company = "N/A (Post)"
            extracted_city = city

            if designation.lower() not in post_text_content.lower():
                pass

            job_entry = {
                "Designación": designation,
                "Nombre de la empresa": extracted_company,
                "Ciudad": extracted_city,
                "Email": "",
                "Teléfono": "",
                "URL de la oferta": post_url,
            }
            job_data.append(job_entry)

    except TimeoutException:
        print(f"Timeout waiting for LinkedIn Posts page elements for '{search_keywords}'. May require login or different selectors.")
    except Exception as e:
        print(f"An error occurred while scraping LinkedIn Posts: {e}")

    print(f"Finished scraping LinkedIn Posts (basic). Found {len(job_data)} potential items.")
    return job_data


def scrape_with_ai(driver, url, *, target_language: str = "English"):
    """Scrape an arbitrary page and analyse its contents using OpenAI.

    This helper is intended for pages that do not have consistent HTML
    structure.  It retrieves the full text of the page and asks the AI model to
    identify useful fields such as price, name, category or dates.  If the
    ``target_language`` differs from the page language the fields are translated
    as well.
    """

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    text_content = soup.get_text(separator="\n", strip=True)

    result = {}

    if extract_fields_from_text:
        try:
            result = extract_fields_from_text(text_content)
        except Exception as e:  # noqa: BLE001
            print(f"AI extraction failed: {e}")

    if classify_content:
        try:
            result["classification"] = classify_content(text_content)
        except Exception as e:  # noqa: BLE001
            print(f"AI classification failed: {e}")

    if target_language and translate_text:
        for key, value in list(result.items()):
            if isinstance(value, str) and value:
                try:
                    result[key] = translate_text(value, target_language=target_language)
                except Exception as e:  # noqa: BLE001
                    print(f"Translation failed for {key}: {e}")

    return result

# Example usage (for testing scraper.py directly)
if __name__ == '__main__':
    # This section is for individual scraper testing.
    # For full application, run main.py
    # test_driver = initialize_driver()
    # if test_driver:
    #     try:
            # Example: Test LinkedIn Jobs
            # print("\nTesting LinkedIn Jobs Scraper...")
            # linkedin_jobs = scrape_linkedin_jobs(test_driver, "Software Engineer", "United States")
            # if linkedin_jobs:
            #     print(f"Found {len(linkedin_jobs)} LinkedIn jobs.")
            #     print(f"Sample LinkedIn Job Data (first 2): {linkedin_jobs[:2]}")
            # else:
            #     print("No LinkedIn jobs found or an error occurred.")

            # Example: Test Indeed (known to have issues with bot detection)
            # print("\nTesting Indeed Scraper...")
            # indeed_jobs = scrape_indeed(test_driver, "Data Analyst", "New York")
            # if indeed_jobs:
            #     print(f"Found {len(indeed_jobs)} Indeed jobs.")
            #     print(f"Sample Indeed Job Data (first 2): {indeed_jobs[:2]}")
            # else:
            #     print("No Indeed jobs found or an error occurred.")

            # Example: Test Internshala
            # print("\nTesting Internshala Scraper...")
            # internshala_internships = scrape_internshala(test_driver, "Web Development", "Work From Home")
            # if internshala_internships:
            #     print(f"Found {len(internshala_internships)} Internshala items.")
            #     print(f"Sample Internshala Data (first 1): {internshala_internships[:1]}")
            # else:
            #     print("No Internshala items found or an error occurred.")

            # Example: Test LinkedIn Posts
            # print("\nTesting LinkedIn Posts Scraper (Basic)...")
            # linkedin_posts = scrape_linkedin_posts(test_driver, "Technical Writer", "Remote")
            # if linkedin_posts:
            #     print(f"Found {len(linkedin_posts)} LinkedIn posts.")
            #     print(f"Sample LinkedIn Post Data (first 1): {linkedin_posts[:1]}")
            # else:
            #     print("No LinkedIn posts found or an error occurred (login might be required).")
    #     finally:
    #         print("Quitting driver in main test.")
    #         test_driver.quit()
    # else:
    #     print("Failed to initialize WebDriver. Cannot run tests.")
    pass  # Keep the if __name__ == '__main__': block for potential future direct testing
