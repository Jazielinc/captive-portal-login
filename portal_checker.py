import time
import socket
import requests
from bs4 import BeautifulSoup
import logging

# Default Apple reliable endpoint for captive portals
CHECK_URL = "http://captive.apple.com/hotspot-detect.html"
EXPECTED_CONTENT = "Success"

def is_connected():
    """Checks if there is any internet connection by resolving a reliable DNS."""
    try:
        # Check if we can resolve a google DNS
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except socket.error as ex:
        return False

def check_captive_portal():
    """
    Checks if we are behind a captive portal.
    Returns:
        (has_internet, is_captive, portal_url, response)
    """
    if not is_connected():
        return False, False, None, None

    try:
        # We must use follow_redirects=False or evaluate the history because
        # captive portals return a 302 or just a 200 with an HTML form.
        response = requests.get(CHECK_URL, timeout=5, allow_redirects=True)
        
        # Apple's check returns a very specific tiny HTML page with "Success"
        if EXPECTED_CONTENT in response.text:
            return True, False, None, response
            
        # If we got here, we got internet, but the content wasn't "Success"
        # It's highly likely a captive portal intercepting the HTTP request.
        return True, True, response.url, response

    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking portal: {e}")
        return False, False, None, None

def auto_login(portal_response):
    """
    Attempts to parse the captive portal page and click the one button.
    """
    if not portal_response:
        return False
        
    url = portal_response.url
    html = portal_response.text
    
    logging.info(f"Attempting to log into portal at: {url}")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find a form
    forms = soup.find_all('form')
    
    if not forms:
        # If no form, try looking for a standard link that looks like a login/accept
        links = soup.find_all('a')
        for link in links:
            text = link.text.lower()
            if 'accept' in text or 'login' in text or 'connect' in text:
                href = link.get('href')
                if href:
                    target_url = href if href.startswith('http') else url + href
                    logging.info(f"Clicking link: {target_url}")
                    try:
                        requests.get(target_url, timeout=5)
                        return True
                    except requests.RequestException:
                        pass
        logging.error("No forms or valid links found. Checking for specific vendor portals...")
        
        # Unifi Hotspot Fallback
        if 'unifi' in html.lower() or '/guest/s/' in url.lower():
            logging.info("Detected Unifi captive portal. Attempting Unifi specific login...")
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            # e.g. path_parts = ['', 'guest', 's', 'default', '']
            if 'guest' in path_parts and 's' in path_parts:
                s_index = path_parts.index('s')
                if len(path_parts) > s_index + 1:
                    site = path_parts[s_index + 1]
                    login_path = f"/guest/s/{site}/login"
                    login_url = f"{parsed.scheme}://{parsed.netloc}{login_path}"
                    if parsed.query:
                        login_url += f"?{parsed.query}"
                    
                    logging.info(f"Unifi login URL inferred as: {login_url}")
                    try:
                        # Unifi expects form-data, not JSON, and requires the query params (id, ap, etc)
                        res = requests.post(login_url, data={'by': 'free'}, timeout=5)
                        logging.info(f"Unifi login returned status: {res.status_code}")
                        return True
                    except Exception as e:
                        logging.error(f"Error in Unifi login: {e}")
                        
        return False

    # Take the first form (since user mentioned it's a 1-click portal)
    form = forms[0]
    action = form.get('action')
    method = form.get('method', 'get').lower()
    
    # Construct target URL
    if not action:
        target_url = url
    elif action.startswith('http'):
        target_url = action
    elif action.startswith('/'):
         # Extract base url
         from urllib.parse import urlparse
         parsed_uri = urlparse(url)
         base_url = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
         target_url = base_url + action
    else:
        # Relative path
        target_url = url + '/' + action if not url.endswith('/') else url + action

    # Collect form inputs
    data = {}
    inputs = form.find_all('input')
    for input_tag in inputs:
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        if name:
            data[name] = value

    logging.info(f"Submitting form to: {target_url} using {method} with data: {data}")
    
    try:
        if method == 'post':
             response = requests.post(target_url, data=data, timeout=5)
        else:
             response = requests.get(target_url, params=data, timeout=5)
             
        logging.info(f"Login request returned status: {response.status_code}")
        return True
    except requests.RequestException as e:
         logging.error(f"Error submitting login form: {e}")
         return False

def run_portal_check():
    """Runs a single check and login cycle."""
    logging.info("Checking for captive portal...")
    has_internet, is_captive, portal_url, response = check_captive_portal()
    success = None
    if has_internet:
        if is_captive:
            logging.info("Captive portal detected!")
            success = auto_login(response)
            if success:
                 logging.info("Auto-login completed.")
            else:
                 logging.info("Auto-login failed.")
    
    return has_internet, is_captive, success

if __name__ == "__main__":
    # Test run
    run_portal_check()
