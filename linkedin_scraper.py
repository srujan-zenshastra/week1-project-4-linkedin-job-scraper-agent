from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def scrape_linkedin_jobs(job_title, location, num_pages=5):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # LinkedIn Jobs URL
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"
    driver.get(search_url)
    time.sleep(5)  # Wait for page to load

    jobs_data = []
    scraped_links = set()  # Track unique job links

    for _ in range(num_pages):
        # Scroll down multiple times to ensure jobs load
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):  # Increased scroll count
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(3)  # Increased wait time
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop scrolling if no new content loads
            last_height = new_height

        # Extract job postings
        job_cards = driver.find_elements(By.CLASS_NAME, "base-card")
        
        for job in job_cards:
            try:
                title_element = job.find_element(By.CLASS_NAME, "base-search-card__title")
                company_element = job.find_element(By.CLASS_NAME, "base-search-card__subtitle")
                location_element = job.find_element(By.CLASS_NAME, "job-search-card__location")
                link_element = job.find_element(By.TAG_NAME, "a")
                
                title = title_element.text.strip() if title_element else "N/A"
                company = company_element.text.strip() if company_element else "N/A"
                location = location_element.text.strip() if location_element else "N/A"
                link = link_element.get_attribute("href") if link_element else "N/A"
                
                if link not in scraped_links:  # Avoid duplicates
                    scraped_links.add(link)
                    jobs_data.append({
                        "Title": title,
                        "Company": company,
                        "Location": location,
                        "Link": link
                    })
            except Exception as e:
                print("Error extracting job details:", e)
    
        time.sleep(3)  # Allow new jobs to load before scrolling again

    driver.quit()
    
    # Save jobs to CSV
    df = pd.DataFrame(jobs_data)
    df.to_csv("linkedin_sde_jobs.csv", index=False)
    print(f"Scraped {len(jobs_data)} unique jobs and saved to linkedin_sde_jobs.csv")

# Run the scraper for Software Engineer jobs in India
scrape_linkedin_jobs("Software%20Engineer", "India", num_pages=5)
