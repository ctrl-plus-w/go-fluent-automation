"""Quick debug script to dump the activities container HTML after login."""
import os
from time import sleep
from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

load_dotenv()

options = Options()
driver = Firefox(options=options)
driver.maximize_window()

username = os.getenv("GOFLUENT_USERNAME")
password = os.getenv("GOFLUENT_PASSWORD")

# Login
driver.get("https://portal.gofluent.com/login/samlconnector")
sleep(3)

domain_input = driver.find_element(By.ID, "outlined-size-normal")
submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
domain_input.send_keys("esaip")
sleep(0.5)
submit_button.click()

# Wait for Microsoft or SSO
for _ in range(60):
    sleep(0.5)
    try:
        url = driver.current_url
    except Exception:
        continue
    if "login.microsoftonline.com" in url:
        break
    if "gofluent.com/app/" in url and "samlconnector" not in url:
        print("SSO bypass - already logged in")
        break

# Try Microsoft login
try:
    WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located((By.ID, "i0116"))
    )
    user_input = driver.find_element(By.ID, "i0116")
    user_input.send_keys(username)
    driver.find_element(By.ID, "idSIButton9").click()

    WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located((By.ID, "i0118"))
    )
    pwd_input = driver.find_element(By.ID, "i0118")
    pwd_input.send_keys(password)
    driver.find_element(By.ID, "idSIButton9").click()

    print("Submitted credentials. Waiting for MFA/redirect (up to 2 min)...")
except Exception as e:
    print(f"Skipping Microsoft login (maybe already on GoFluent): {e}")

# Wait for GoFluent
for i in range(240):
    sleep(0.5)
    try:
        url = driver.current_url
        if "gofluent.com/app/" in url and "samlconnector" not in url:
            print(f"On GoFluent: {url}")
            break
        # Click "Stay signed in" if present
        try:
            el = driver.find_element(By.XPATH, "//*[contains(text(), 'Stay signed in?')]")
            if el.is_displayed():
                driver.find_element(By.ID, "idSIButton9").click()
                print("Clicked 'Stay signed in'")
        except NoSuchElementException:
            pass
    except Exception:
        continue
else:
    print(f"Timeout waiting for GoFluent. URL: {driver.current_url}")
    driver.quit()
    exit(1)

sleep(3)

# Navigate to grammar page
print("Navigating to grammar page...")
driver.get("https://esaip.gofluent.com/app/dashboard/resources/grammar")
sleep(5)

print(f"On grammar page: {driver.current_url}")

# Try to find the activities list
try:
    container = driver.find_element(By.CSS_SELECTOR, ".browse-all-activities__list")
    html = container.get_attribute("outerHTML")
    with open("debug_activities_html.txt", "w") as f:
        f.write(html)
    print(f"Wrote {len(html)} chars to debug_activities_html.txt")
except Exception as e:
    print(f"Could not find .browse-all-activities__list: {e}")
    # Try alternative selectors
    for selector in [".browse-all-activities", "[class*='browse']", "[class*='activities']", "[class*='resource']"]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"  Selector '{selector}': found {len(els)} elements")
            if els:
                for i, el in enumerate(els[:3]):
                    print(f"    [{i}] tag={el.tag_name} class='{el.get_attribute('class')}' text='{el.text[:100]}'")
        except Exception:
            pass

    # Dump the whole page
    html = driver.page_source
    with open("debug_page_source.html", "w") as f:
        f.write(html)
    print(f"Wrote full page source ({len(html)} chars) to debug_page_source.html")

driver.quit()
