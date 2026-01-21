"""
A script for the home page of the PyScript Packages site.

It fetches the top 100 PyPI packages and displays them with their
PyScript support status.
"""
import js
from pyscript import fetch
from pyscript.web import page, a

def get_package_name():
    """
    Extract the package name from the query string.

    Package names are case insensitive, so we convert to lowercase.
    """
    query_string = js.window.location.search
    url_params = js.URLSearchParams.new(query_string)
    package_name = url_params.get("q")
    if package_name:
        return package_name.strip().lower()
    return None

package_name = get_package_name()

if package_name:
    js.window.location.replace(f"./package?package={package_name}")

top100 = await fetch("./api/top_100_pypi_packages.json").json()

target = page["#top100"]

for pkg in top100["packages"]:
    status = pkg.get("status", "unknown")
    if status == "green":
        status_badge = '<span class="status-badge green">✅</span>'
    elif status == "amber":
        status_badge = '<span class="status-badge amber">⚠️</span>'
    else:
        status_badge = '<span class="status-badge red">❌</span>'
    
    package_item = a(f'''
  <div class="package-header">
    <span class="package-name">{pkg["package_name"]}</span>
    {status_badge}
  </div>
  <p class="package-desc">{pkg["summary"]}</p>
''', href=f"./package?package={pkg["package_name"]}", classes=["package-item", f"status-{status}"])
    target.append(package_item)