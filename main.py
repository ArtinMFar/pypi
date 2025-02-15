from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route("/")
def find_packages():
    # Get the 'find' query parameter, e.g. ?find=(Flask)%20(requests)
    find_param = request.args.get("find", "")
    if not find_param:
        return "No package names provided. Please use the format ?find=(PackageName) and try again."

    # Extract package names wrapped in parentheses.
    packages = re.findall(r"\((.*?)\)", find_param)
    if not packages:
        return "No valid package names were found in your request. Please enclose package names in parentheses like (Flask)."
    
    results = ""
    for pkg in packages:
        results += f"Start of {pkg}\n\n"
        url = f"https://pypi.org/project/{pkg}/"
        try:
            resp = requests.get(url)
        except Exception as e:
            results += f"An error occurred while fetching package '{pkg}': {e}\n\n"
            continue

        if resp.status_code != 200:
            results += f"Package '{pkg}' does not exist on PyPI. Please try another package.\n\n"
            continue
        
        # Parse the PyPI page using BeautifulSoup.
        soup = BeautifulSoup(resp.text, "html.parser")
        # Try to find the project description. PyPI usually places it in a div with class "project-description"
        desc_div = soup.find("div", class_="project-description")
        if desc_div:
            description = desc_div.get_text(separator="\n", strip=True)
        else:
            description = "No description available."
        
        results += description + "\n\n"
    
    # Return the results as plain text.
    return Response(results, mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
