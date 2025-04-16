import os
import time
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
#########################################################################################
# Load environment variables from the .env file
env_path = Path("config_data.env")
load_dotenv(dotenv_path=env_path)

# Get environment variables
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
tenant_name = os.getenv("TENANT_NAME")
tenant_url = os.getenv("TENANT_URL")

assigned_username = os.getenv("ASSIGNED_USERNAME")
assigned_password = os.getenv("ASSIGNED_PASSWORD")

extension_path = os.getenv("EXTENSION_PATH")
firefox_extension_path = os.getenv("EXTENSION_PATH_FIREFOX")
policy_type = os.getenv("POLICY_TYPE")
browser = os.getenv("BROWSER", "chrome").lower()
#########################################################################################
tag = "File Download"
ai_prompt = "Block file downloads from github"
policy = "file.download.url.domain"
##############################################################################
websites = ['https://github.com/Ishan-creed/Coin-API/blob/main/router/router.js']


def print_details():
    current_file = os.path.basename(__file__)
    capabilities = driver.capabilities
    browser_name = capabilities['browserName']
    browser_version = capabilities['browserVersion'] if 'browserVersion' in capabilities else capabilities['version']
    platform_name = capabilities['platformName'] if 'platformName' in capabilities else capabilities['platform']
    now = datetime.now()

    # Format the date and time to include AM/PM
    formatted_date = now.strftime("%d-%m-%Y")
    formatted_time = now.strftime("%I:%M:%S %p")

    # Print details
    print("--------------------------------------------------------------------------------------------------")
    print("Script Execution Date :", formatted_date)
    print("Script Execution Time :", formatted_time)

    print(f"Current file name: {current_file}")
    print(f"Browser name: {browser_name}")
    print(f"Browser version: {browser_version}")
    print(f"Platform name: {platform_name}")
    # Extract the directory containing the extension name


    # Extract the extension name by splitting based on the last backslash
    extension_name = "SquareX BDM"

    # # Print the extension name
    print("Extension Used:", extension_name)
    print("--------------------------------------------------------------------------------------------------")


##############################################################################
driver = None

if browser == "chrome":
    extension_path = "../onsqrx-20250404/"
    options = webdriver.ChromeOptions()
    
    # Add extension (path must match container's filesystem)
    options.add_argument(f"--load-extension={extension_path}") 
    print("Extension installed")
    
    # Configure for Docker environment
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Connect to Selenium Grid in Docker container
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=options
    )
elif browser == "edge":
    edge_driver = EdgeChromiumDriverManager().install()  # Get the EdgeDriver executable
    options = webdriver.EdgeOptions()
    options.add_argument(f"--load-extension={extension_path}")  # Load Edge extension
    driver = webdriver.Edge(service=EdgeService(edge_driver), options=options)

elif browser == "firefox":
    gecko_driver = GeckoDriverManager().install()  # Get the GeckoDriver executable
    options = webdriver.FirefoxOptions()
    extension_path = os.path.abspath(extension_path)  # Ensure this is the correct path to your extension

    # Disable signature requirement and allow legacy extensions
    options.set_preference("xpinstall.signatures.required", False)
    options.set_preference("extensions.legacy.enabled", True)
    options.set_preference("extensions.install.requireBuiltInCerts", False)

    # Initialize the Firefox driver
    driver = webdriver.Firefox(service=Service(gecko_driver), options=options)

    # Install the extension (this is the correct method for Firefox)
    driver.install_addon(extension_path, temporary=True)


else:
    print(f"Unsupported browser: {browser}. Please choose chrome or edge")
    exit(1)

#########################################################################################
def login_function():
    driver.maximize_window()
    driver.get(tenant_url)

    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email address']"))
    )
    email_field.send_keys(admin_username)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
    )
    password_field.send_keys(admin_password)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    print("Logged In")
    print("Current URL ::", tenant_url)
    print("Admin Email ::", admin_username)

    header_element = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Detections']"))
    )

    policy_list_page_url = "/enterprise/#/policy"
    policy_page = tenant_url + policy_list_page_url

    driver.get(policy_page)

    header_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@class='text-lg font-semibold text-primary']"))
    )

    print("Navigated to Policy List Page")


##############################################################################
def check_for_existing_policies():
    tbody = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        '#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.mt-2.max-h-96.overflow-auto.rounded-md.border.bg-card > table > tbody'))
    )

    # Scroll the tbody to ensure all rows are loaded (for virtualized tables)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", tbody)

    time.sleep(2)

    # JavaScript code to find the number of rows in the tbody
    js_code = """
        const tbody = document.querySelector('#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.mt-2.max-h-96.overflow-auto.rounded-md.border.bg-card > table > tbody');
        return tbody ? tbody.querySelectorAll('tr').length : -1;  // -1 if tbody not found
    """

    # Execute JavaScript in the context of the current page
    row_count = driver.execute_script(js_code)

    # Check the result in Python and print output accordingly
    if row_count == -1:
        print("No existing policies.")

    else:
        print(f"Number of Existing Policies: {row_count}")
        wait = WebDriverWait(driver, 10)  # # Proceed to delete the existing policy
        top_check_box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='root']/div/div[2]/main/div[6]/table/thead/tr/th[1]/button"))
        )
        top_check_box.click()

        three_dot_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='root']/div/div[2]/main/div[5]/div/button"))
        )
        three_dot_button.click()

        delete_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Delete')]"))
        )
        delete_button.click()

        confirm_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Confirm')]"))
        )
        confirm_button.click()

        print(f"{row_count} existing polices deleted.")


##############################################################################
def file_download_policies_creation():
    file_download = "/enterprise/#/file.download/policy"

    file_download_page = tenant_url + file_download

    driver.get(file_download_page)

    new = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR,
                                          "#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > button"))
    )
    new.click()

    if policy_type == "LUA":
        policy_selection = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              "button[class='flex h-9 items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1 right-5 top-5 w-32']"))
        )
        policy_selection.click()

        lua_option = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[text()='LUA script']"))
        )
        lua_option.click()

        print("-------------------")
        print("LUA Method Selected")
        print("-------------------")

    else:
        print("---------------------")
        print("Ruler Method Selected")
        print("---------------------")
      ###################################################
        wait = WebDriverWait(driver, 10)
        policy_type_text = wait.until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div/div/div[2]/main/div[1]/button")))

        print("Policy Type Selected:", policy_type_text.text)
        ###############################################

        #######Assigned user selection ##########
        select_member = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div/div/div[2]/main/div[3]/div[2]/div/div[8]/div/button")))
        select_member.click()

        search_keys = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search...']")))
        search_keys.send_keys(assigned_username)

        time.sleep(2)

        check_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[@role='checkbox']")))
        check_box.click()

        assigned_username_clicking = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),assigned_username)]")))
        assigned_username_clicking.click()

        #################################################################################
        ##### Manual method policy created  ########
        #################################################################################
        ########  RULER METHOD CODE ##################
        ## NAME YOUR POLICY
        wait = WebDriverWait(driver, 10)
        # policy_name
        policy_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='policy']")))
        policy_input.send_keys("Block GitHub Downloads")

        # Description
        desc_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@id='desc']")))
        desc_input.send_keys(
            "Block file downloads from GitHub")

        # 1 ID
        input_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[1]/div[1]/input")))
        input_element.send_keys("block_github_downloads_rule")

        # 1 Effect selection
        dropdown_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[1]/div[2]/button")))
        dropdown_button.click()

        # 1 Block effect click
        value_click = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@dir='ltr']//div[2]")))
        value_click.click()

        # 1 Conditions AND or OR
        condition_and_or = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[1]/button")))
        condition_and_or.click()

        or_click = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@dir='ltr']//div[3]")))
        or_click.click()

        # 1 select property
        select_property = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                 "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[1]/div/button/div")))
        select_property.click()

        # 1 select property input
        input_element_input = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                         "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/div/div/div[1]/input")))
        input_element_input.send_keys("page.url.domain")
        input_element_input.send_keys(Keys.ENTER)

        file_extension_value_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[4]/input")))
        file_extension_value_input.send_keys("github.com")
        time.sleep(1)

        # 1 Add condition Button
        add_condition_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/button")))
        add_condition_button.click()

        # 1 select property
        select_property_two = driver.find_element(By.CSS_SELECTOR,
                                                  "#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.rounded-xl.border.bg-card.text-card-foreground.shadow-sm.relative.mt-4 > div.p-5.pt-0.space-y-6 > div.relative > div > div.border.p-4 > div.mt-6.border-l.pl-2 > div.mt-4.space-y-4 > div:nth-child(2) > div.flex.w-full.max-w-4xl.items-center.justify-between.gap-3 > div:nth-child(1) > div > button")
        select_property_two.click()

        # 1 select property input
        input_element_input = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                         "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div/div/div/div/div[1]/input")))
        input_element_input.send_keys("file.download_url.domain")
        input_element_input.send_keys(Keys.ENTER)

        file_extension_value_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[4]/input")))
        file_extension_value_input.send_keys("github.com")

        time.sleep(1)
        # 1 Add condition Button
        add_condition_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/button")))
        add_condition_button.click()

        # 1 select property
        select_property_three = driver.find_element(By.CSS_SELECTOR,
                                                  "#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.rounded-xl.border.bg-card.text-card-foreground.shadow-sm.relative.mt-4 > div.p-5.pt-0.space-y-6 > div.relative > div > div.border.p-4 > div.mt-6.border-l.pl-2 > div.mt-4.space-y-4 > div:nth-child(3) > div.flex.w-full.max-w-4xl.items-center.justify-between.gap-3 > div:nth-child(1) > div > button")
        select_property_three.click()

        # 1 select property input
        input_element_input = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                         "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[3]/div[2]/div[1]/div/div/div/div/div[1]/input")))
        input_element_input.send_keys("file.final_download_url.domain")
        input_element_input.send_keys(Keys.ENTER)

        file_extension_value_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[2]/div[2]/div[3]/div[2]/div[4]/input")))
        file_extension_value_input.send_keys("github.com")
        time.sleep(1)




    save_button = driver.find_element(By.XPATH, "//button[normalize-space()='Save']")
    save_button.click()
#################################################################################################

    print("AI PROMPT::", ai_prompt)
    print("Policy Type::", tag)
    print(tag, "New Policy Created")
    print("   ")
    print("Policy::", policy)

    policy_list_page_url = "/enterprise/#/policy"
    policy_page = tenant_url + policy_list_page_url

    driver.get(policy_page)


##############################################################################
def assigned_user_login():
    driver.delete_all_cookies()
    driver.get(tenant_url)

    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email address']"))
    )
    email_field.send_keys(assigned_username)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
    )
    password_field.send_keys(assigned_password)

    continue_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@id='login-email-btn']"))
    )
    continue_button.click()

    print("                           ")
    print("Logged In As Admin User")
    print("Current URL ::", tenant_url)
    print("Assigned User Email ::", admin_username)


#####################################################################################################################
def click_element(driver, xpath: str, scroll: bool = True, timeout: int = 10):
    """
    Waits for an element to be present and clicks it. If not interactable, executes JavaScript click.

    Args:
        driver: Selenium WebDriver instance.
        xpath: XPath of the element to be clicked.
        scroll: Whether to scroll the element into view before clicking.
        timeout: Maximum wait time for the element to appear.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        if scroll:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
        try:
            element.click()
        except ElementNotInteractableException:
            driver.execute_script("arguments[0].click();", element)
        return element
    except TimeoutException:
        print(f"Timeout: Element with XPath '{xpath}' not found.")
        return None


def check_status():

    try:
        time.sleep(3)

        script = """
        try {
            let shadowHost = document.querySelector('body > sqrx-shdw-dialog');
            if (!shadowHost) return null;
            let shadowRoot = shadowHost.shadowRoot;
            let titleElement = shadowRoot.querySelector('main > div > div.modal-title > h3');
            let contentElement = shadowRoot.querySelector('main > div > div.modal-content > p');
            if (!titleElement || !contentElement) return null;
            return [titleElement.textContent, contentElement.textContent];
        } catch (error) {
            return null;
        }
        """

        # Execute the script and store results
        result = driver.execute_script(script)

        if result is None:
            print("********************************************")
            print(f"Download not blocked: {driver.current_url}")
            print("********************************************")
            return  # Exit the function early

        title_text, content_text = result

        if title_text == "Download Blocked":
            print(f"Download Blocked by Square-X: {driver.current_url}")
            print(title_text)
            print(content_text)
            print("")
        else:
            print("********************************************")
            print("\nDownload not blocked in", driver.current_url)
            print("********************************************")
            print("")

    except (NoSuchElementException, TimeoutException) as e:
        print("  ")
        print("********************************************")
        print(f"Download not blocked: {driver.current_url}")
        print("********************************************")


def open_sites(driver):
    """
    Opens websites in new tabs, checks their status, and closes the tabs.

    Args:
        driver: Selenium WebDriver instance.
    """
    time.sleep(2)
    time.sleep(3)

    for count, website in enumerate(websites):
        print(f"Opening website: {website}")

        # Open new tab
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        driver.get(website)
        time.sleep(3)  # Wait for the website to load

        try:
            download_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='download-raw-button']"))
            )

            # Click the download button
            download_button.click()
            print("Download button clicked!")
            time.sleep(2)
        except Exception as e:

            print(e)

        # Check status
        check_status()

        # Close current tab and switch back
        # driver.close()
        driver.switch_to.window(driver.window_handles[0])

        time.sleep(2)


#########################################################################################
print_details()

login_function()
# check_for_existing_policies()
file_download_policies_creation()

assigned_user_login()
open_sites(driver)

#########################################################################################
if driver:
    # driver.quit()
    print("Browser closed.")

#########################################################################################
