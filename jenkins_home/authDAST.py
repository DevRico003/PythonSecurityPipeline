from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import subprocess
import sys
import random
import string

def randomString(stringLength=10):
    """Generiert einen zufälligen String der angegebenen Länge."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def bash_command(cmd):
    """Führt einen Bash-Befehl aus."""
    subprocess.Popen(cmd, shell=True, executable='/bin/bash')

if len(sys.argv) < 4:
    print('1. Geben Sie die IP-Adresse des Selenium Remote-Servers an!')
    print('2. Geben Sie die IP-Adresse für den Ziel-DAST-Scan an!')
    print('3. Geben Sie den Speicherort der HTML-Ausgabedatei an!')
    sys.exit(1)

# Konfigurieren Sie Chrome-Optionen nach Bedarf
chrome_options = Options()
# Beispiel: Führen Sie Chrome im Headless-Modus aus
chrome_options.add_argument("--headless")

# Erstellen des WebDriver-Objekts mit Remote-Optionen
driver = webdriver.Remote(
    command_executor=f"http://{sys.argv[1]}:4444/wd/hub",
    options=chrome_options
)

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
