from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import subprocess
import sys
import random
import string

def randomString(stringLength=10):
    """Generiert einen zufälligen String der angegebenen Länge."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def bash_command(cmd):
    """Führt den angegebenen Bash-Befehl aus."""
    subprocess.Popen(cmd, shell=True, executable='/bin/bash')

chrome_options = Options()

# Erstellen Sie die DesiredCapabilities
capabilities = DesiredCapabilities.CHROME.copy()
# Fügen Sie die ChromeOptions zur Capabilities hinzu
capabilities.update(chrome_options.to_capabilities())

myusername = randomString(8)
mypassword = randomString(12)

if len(sys.argv) < 4:
    print('1. Provide the IP address for selenium remote server!')
    print('2. Provide the IP address for target DAST scan!')
    print('3. Provide the output location of html report!')
    sys.exit(1)

# Stellen Sie sicher, dass die URL korrekt ist
selenium_server_url = "http://3.71.166.230:4444/wd/hub"

driver = webdriver.Remote(command_executor=selenium_server_url, desired_capabilities=capabilities)


# Geht zur Login-Seite
driver.get(f"http://{sys.argv[2]}:10007/login")

# Registriert einen neuen Benutzer
register_button = driver.find_element_by_xpath("/html/body/div/div/div/form/center[3]/a")
register_button.click()

myusername = randomString(8)
mypassword = randomString(12)

username = driver.find_element_by_name("username")
password1 = driver.find_element_by_name("password1")
password2 = driver.find_element_by_name("password2")

username.send_keys(myusername)
password1.send_keys(mypassword)
password2.send_keys(mypassword)
password2.send_keys(Keys.RETURN)

# Loggt sich mit dem neuen Benutzer ein
driver.get(f"http://{sys.argv[2]}:10007/login")
username = driver.find_element_by_name("username")
password = driver.find_element_by_name("password")

username.send_keys(myusername)
password.send_keys(mypassword)
password.send_keys(Keys.RETURN)

# Extrahiert Cookies für den DAST-Scan
nikto_string = "STATIC-COOKIE="
cookies_list = driver.get_cookies()
for cookie in cookies_list:
    nikto_string += f"\"{cookie['name']}\"=\"{cookie['value']}\";"

# Fügt den Cookie-String zur Nikto-Konfigurationsdatei hinzu
bash_command(f"echo '{nikto_string}' > ~/nikto-config.txt")

# Führt den Nikto-Scan durch
bash_command(f"nikto -ask no -config ~/nikto-config.txt -Format html -h http://{sys.argv[2]}:10007/gossip -output {sys.argv[3]}")

driver.quit()
