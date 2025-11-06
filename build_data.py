"""
Uses requests to fetch and parse the Pyodide package support data JSON files
found here:

https://raw.githubusercontent.com/pyscript/polyscript/refs/heads/main/esm/interpreter/pyodide_graph.js

Then iterates over them to generate individual package JSON files used by
the package support detail page. These end up in the /data/ directory.

It also grabs the download stats for PyPI and creates a JSON description
including info about the top 100 packages by download count and whether
they are supported in Pyodide.

TODO: Grab data from the Google Sheets document used to track package
support status, and use that to override the Pyodide data where appropriate.
"""
import requests
import json
import datetime

# Grab the data
response = requests.get("https://raw.githubusercontent.com/pyscript/polyscript/refs/heads/main/esm/interpreter/pyodide_graph.js")
response.raise_for_status()
data = response.text

# Extract the JSON part
raw_json = data.replace("export default ", "")  # remove 'export ' prefix
package_data = json.loads(raw_json.replace("'", '"'))


# To hold the per-package data to later be turned into JSON files.
packages = {}

# Iterate over the releases of Pyodide
for release, package_list in package_data.items():
    print(f"Processing release: {release}")
    for package_name, version in package_list.items():
        print(f"  Processing package: {package_name}")
        if package_name not in packages:
            packages[package_name] = {}
        # Add the supported version of this package for the given release of Pyodide.
        packages[package_name][release] = version


updated_by = "automated script"
updated_at = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
# Write out the per-package JSON files
for package_name, data in packages.items():
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if response.status_code != 200:
        print(f"Warning: Could not fetch PyPI metadata for package '{package_name}'. Skipping.")
        continue
    pypi_metadata = response.json()
    summary = pypi_metadata.get("info", {}).get("summary", "No summary available.")
    if not summary:
        # Some packages have an empty string or Noneas summary.
        summary = "No summary available."
    pyodide_versions = [f"`{version}`" for version in data.keys()]
    notes = f"""This package is officially supported in Pyodide.

Specifically, the following versions of the package are available for the following Pyodide releases:

Pyodide version: package name (version)
"""
    notes += "\n".join([f"* `{k}`: `{package_name} ({data[k]})`" for k in sorted(data.keys(), reverse=True)])
    output = {
        "status": "green",
        "notes": notes,
        "supported_versions": data,
        "updated_by": updated_by,
        "updated_at": updated_at,
        "summary": summary
    }
    filename = f"data/{package_name}.json"
    print(f"Writing data for package '{package_name}' to '{filename}'")
    with open(filename, "w") as f:
        json.dump(output, f, indent=4)



# Onto the top 100 PyPI packages by download count.
url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json"
response = requests.get(url)
response.raise_for_status()
top_pypi_data = response.json()

last_updated = top_pypi_data.get("last_update", "unknown")
top100 = top_pypi_data.get("rows", [])[:100]

# Create a summary JSON file for the top 100 packages. Include a check of the
# Pyodide support status from the previously generated data in the /data/ directory,
# if it exists. Otherwise, default to "amber" status.
summary = {
    "last_updated": last_updated,
    "packages": []
}
for entry in top100:
    package_name = entry.get("project")
    print("Processing top package: ", package_name)
    downloads = entry.get("download_count", 0)
    # Check for support data
    try:
        with open(f"data/{package_name}.json", "r") as f:
            support_data = json.load(f)
            status = support_data.get("status", "amber")
            desc = support_data.get("summary", "No summary available.")
    except FileNotFoundError:
        status = "amber"
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            pypi_metadata = response.json()
            desc = pypi_metadata.get("info", {}).get("summary", "No summary available.")
        else:
            desc = "No summary available."
    summary["packages"].append({
        "package_name": package_name,
        "downloads": downloads,
        "status": status,
        "summary": desc
    })

# Write out the summary JSON file
with open("top_100_pypi_packages.json", "w") as f:
    json.dump(summary, f, indent=4)
print("Generated top_100_pypi_packages.json")