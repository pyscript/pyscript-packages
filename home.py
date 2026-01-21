"""
A script for the home page of the PyScript Packages site.

It fetches the top 100 PyPI packages and displays them with their
PyScript support status.
"""
from pyscript import fetch
from pyscript.web import page, a

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