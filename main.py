from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

# Set up Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode for faster performance
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# Set up WebDriver service
service = Service("chromedriver.exe")  # Replace with the path to your ChromeDriver

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open the target website
    url = "https://fvgc.ca/membership-list/"
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "et_pb_row"))
    )

    print("Page loaded successfully.")

    # Prepare CSV file
    with open("membership_list.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Region", "Organization Type", "Organization Name", "Link"])

        # Loop through the target classes et_pb_row_4 to et_pb_row_14
        for i in range(4, 15):
            row_class = f"et_pb_row_{i}"
            try:
                # Locate the row element
                row_element = driver.find_element(By.CLASS_NAME, row_class)

                # Extract the region (use JavaScript if text is not accessible directly)
                region_element = row_element.find_element(By.TAG_NAME, "h2")
                region = driver.execute_script("return arguments[0].innerText;", region_element).strip()

                # Extract organization sections (h3 tags)
                h3_elements = row_element.find_elements(By.TAG_NAME, "h3")
                for section in h3_elements:
                    org_type = driver.execute_script("return arguments[0].innerText;", section).strip()
                    
                    if org_type == "":
                        continue

                    # Find the table under each section
                    table = section.find_element(By.XPATH, "following-sibling::table")
                    rows = table.find_elements(By.TAG_NAME, "tr")

                    for row in rows:
                        try:
                            cell = row.find_element(By.TAG_NAME, "td")
                            org_name = cell.text.strip()

                            # Extract the link text and href
                            link_element = cell.find_element(By.TAG_NAME, "a") if cell.find_elements(By.TAG_NAME, "a") else None
                            link_href = link_element.get_attribute("href") if link_element else "N/A"
                            link_text = link_element.get_attribute("innerText") if link_element else "N/A"

                            # Write to CSV
                            writer.writerow([region, org_type, link_text, link_href])
                        except Exception as e:
                            print(f"Error extracting row data: {e}")
            except Exception as e:
                print(f"Error processing row {row_class}: {e}")

finally:
    # Close the WebDriver
    driver.quit()

print("Data extraction complete. Results saved to membership_list.csv.")
