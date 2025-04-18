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
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
import tempfile
from selenium.webdriver import Remote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions


required_envs = ["ADMIN_USERNAME", "ADMIN_PASSWORD", "TENANT_URL", "EXTENSION_PATH"]
missing = [key for key in required_envs if not os.getenv(key)]

# if missing:
#     raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")


#########################################################################################
# # Load environment variables from the .env file
# env_path = Path("./config_data.env")
# load_dotenv(dotenv_path=env_path)

# Get environment variables
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
tenant_name = "onsqrx"
tenant_url = os.getenv("TENANT_URL")

assigned_username = os.getenv("ASSIGNED_USERNAME")
assigned_password = os.getenv("ASSIGNED_PASSWORD")

# extension_path = os.getenv("EXTENSION_PATH")
firefox_extension_path = os.getenv("EXTENSION_PATH_FIREFOX")
policy_type = os.getenv("POLICY_TYPE")
browser = os.getenv("BROWSER", "chrome").lower()
#########################################################################################
tag = "Site Visit"
ai_prompt = "Monitor social media websites"
policy = "page.url.category"
##############################################################################
websites = [
        'https://chatgpt.com/',
        'https://www.deepseek.com/', 
        'https://www.perplexity.ai/',
        'https://copilot.microsoft.com/',
        'https://gemini.google.com/'
    ]

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
    extension_dir = "../onsqrx-20250404/"

    # Extract the extension name by splitting based on the last backslash
    extension_name = "SquareX BDM"

    # # Print the extension name
    print("Extension Used:", extension_name)
    print("--------------------------------------------------------------------------------------------------")
##############################################################################
driver = None

if browser == "chrome":
    grid_url = "http://localhost:4444/wd/hub"
    options = ChromeOptions()
    
    # Add all Chrome arguments BEFORE creating the driver
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    # Load extension if needed
    with open("extension_base64.txt", "r") as f:
        encoded = f.read()
    options.add_encoded_extension(encoded)

    # Create Remote WebDriver with configured options
    driver = webdriver.Remote(command_executor=grid_url, options=options)

elif browser == "edge":
    edge_driver = EdgeChromiumDriverManager().install()  # Get the EdgeDriver executable
    options = webdriver.EdgeOptions()
    options.add_argument(f"--load-extension={extension_path}")  # Load Edge extension
    driver = webdriver.Edge(service=EdgeService(edge_driver), options=options)

elif browser == "firefox":
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    from webdriver_manager.firefox import GeckoDriverManager
    xpi_path = os.path.abspath("../build.xpi")
    
    options = Options()
    options.set_preference("xpinstall.signatures.required", False)  # Disable signature requirement
    options.set_preference("extensions.legacy.enabled", True)  # Enable legacy extensions
    options.set_preference("extensions.install.requireBuiltInCerts", False)  # Allow any XPI install
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    # Install the extension temporarily
    driver.install_addon(xpi_path, temporary=True)           


else:
    print(f"Unsupported browser: {browser}. Please choose chrome or edge")
    exit(1)

# def verify_extension_loaded(extension_name: str):
#     driver.get("chrome://extensions/")
#     time.sleep(2)  # let the page render
#     page_source = driver.page_source
#     return extension_name.lower() in page_source.lower()

# if verify_extension_loaded("SquareX BDM"):
#     print("✅ Extension is loaded and visible in chrome://extensions/")
# else:
#     print("❌ Extension not found — it may have failed to load.")

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

    try:
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
            wait = WebDriverWait(driver, 10)   # # Proceed to delete the existing policy
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
    except:
        print("No detections")

##############################################################################
def site_visit_policies_creation():
    site_visit = "/enterprise/#/site.visit/policy"

    site_visit_page = tenant_url + site_visit

    driver.get(site_visit_page)

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

  

    select_member = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button//div[text()='Select member']"))
    )
    

    # Scroll to the element using JavaScript
    driver.execute_script("arguments[0].scrollIntoView();", select_member)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(select_member))
    select_member.click()

    time.sleep(2)

    assign_member = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="search"]'))
    )

    # Click the search input
    assign_member.click()

    # Enter text into the search input
    assign_member.send_keys(assigned_username)

    time.sleep(2)



    check_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[role="checkbox"]'))
    )

    # Click the button

    check_box.click()

    

    time.sleep(2)
    
    select_property = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button//div[text()='Select Property']"))
    )
    

    # Scroll to the element using JavaScript
    driver.execute_script("arguments[0].scrollIntoView();", select_property)
    select_property.click()

    time.sleep(2)

    assign_property = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search..."]'))
    )

    assign_property.click()


    # Enter text into the search input
    assign_property.send_keys("page.url.category")

    time.sleep(2)

    result_property = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "page.url.category")]'))
    )

    result_property.click()

    time.sleep(2)
    # # -----------------------------------------------------------------------------------------------------------------------------

    select_category = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located(
        (By.XPATH, "//button//div[text()='Select Value']"))
    )

    # Scroll to the element using JavaScript
    driver.execute_script("arguments[0].scrollIntoView();", select_category)
    select_category.click()

    time.sleep(2)

    assign_category = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search..."]'))
    )

    assign_category.click()

    # Enter text into the search input
    assign_category.send_keys("Generative AI")

    time.sleep(2)

    result_category = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Generative AI")]'))
    )

    result_category.click()

    time.sleep(2)

    #------------------------------------------------------------------------------------------------------------------------------

    policy_name = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/main/div[3]/div[2]/div/div[1]/input'))
    )

    policy_name.send_keys("Block all Generative Sites")

    time.sleep(1)

    policy_id = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/main/div[3]/div[2]/div/div[2]/input'))
    )

    policy_id.send_keys("")

    time.sleep(1)

    policy_description = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/main/div[3]/div[2]/div/div[4]/textarea'))
    )

    policy_description.send_keys("Block all Generative AI Sites")

    time.sleep(2)

   # Wait for the select_effect button to be clickable

  # Initialize WebDriverWait with a timeout
    wait = WebDriverWait(driver, 10)
    dropdown_button2 = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[1]/div/div[2]/main/div[3]/div[2]/div/div[6]/button")
    ))
    dropdown_button2.click()  # Click the dropdown button

    # Wait for the value option to be clickable
    value_click2 = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@dir='ltr']//div[3]")
    ))
    value_click2.click()  # Click the value option
     
    rule_id = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#root > div > div.flex.flex-1.flex-col.overflow-auto.bg-background > main > div.rounded-xl.border.bg-card.text-card-foreground.shadow-sm.relative.mt-4 > div.p-5.pt-0.space-y-6 > div.relative > div > div.border.p-4 > div.grid.grid-cols-2.gap-4 > div:nth-child(1) > input'))
)

    rule_id.send_keys("block_generative_ai")
    
    time.sleep(2)
    # Wait for the dropdown button to be clickable
    dropdown_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div/div/div[2]/main/div[4]/div[2]/div[1]/div/div[3]/div[1]/div[2]/button")
    ))
    dropdown_button.click()  # Click the dropdown button

    # Wait for the value option to be clickable
    value_click = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@dir='ltr']//div[2]")
    ))
    value_click.click()  # Click the value option

    # Optional: Wait for the action to complete
    time.sleep(2)


    # -----------------------------------------------------------------------------------------------------------------------------


   

    save_button = driver.find_element(By.XPATH, "//button[normalize-space()='Save']")
    save_button.click()

    print("AI PROMPT::", ai_prompt)
    print("Policy Type::", tag)
    print(tag, "New Policy Created")
    print("   ")
    print("Policy::",policy)

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

def check_status(driver):
   
   
   try:
        main_title = driver.find_element(By.CSS_SELECTOR, "#main-title").text
        main_title == 'Content Blocked'
        blocked_url = driver.find_element(By.CSS_SELECTOR, "#url").text
        print("  ")
        print(blocked_url, " ", f"Website blocked by Square-X: {driver.current_url}")


   except NoSuchElementException:
        print("  ")
        print("********************************************")
        print(f"Website not blocked: {driver.current_url}")
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

        # Check status
        check_status(driver)
     
        # Close current tab and switch back
        # driver.close()
        driver.switch_to.window(driver.window_handles[0])

        time.sleep(2)

#########################################################################################
print_details()

login_function()
# check_for_existing_policies()
site_visit_policies_creation()

assigned_user_login()
open_sites(driver)


#########################################################################################
if driver:
    driver.quit()
    print("Browser closed.")
    # shutil.rmtree(temp_dir)
#########################################################################################
