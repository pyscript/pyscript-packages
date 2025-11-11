"""
This is a VERY simple script to build the static JSON data files used by the
package support detail page in the PyScript documentation site.

How?

1. It uses requests to fetch and parse the Pyodide package support data JSON
files found here:

https://raw.githubusercontent.com/pyscript/polyscript/refs/heads/main/rollup/pyodide_graph.json

Then iterates over them to generate individual package JSON files used by
the package support detail page. These end up in the /data/ directory.

2. It also grabs the download stats for PyPI and creates a JSON description
including info about the top 100 packages by download count and whether
they are supported in Pyodide.

3. Finally, it fetches community contributed package status updates from a
Google Sheets document (published as CSV) and uses those to override the
generated data files as needed.

This is a DELIBERATELY simple script without much error handling or
sophistication. It is intended to be run occasionally by hand to refresh
the data files. Since this website is advertised as being "curated" this
manual step is REQUIRED, so that we can review the changes before pushing
them live via a git based PR.
"""

import requests
import json
import datetime
import csv
import os
from io import StringIO


############################################
# Step 1: Generate per-package JSON files from Pyodide data.
############################################
print("Generating per-package JSON files from Pyodide data...")


# Grab the raw JSON data
response = requests.get(
    "https://raw.githubusercontent.com/pyscript/polyscript/refs/heads/main/rollup/pyodide_graph.json"
)
response.raise_for_status()
package_data = response.json()


# To hold the per-package data to later be turned into JSON files.
packages = {}

# Iterate over the releases of Pyodide
for release, package_list in package_data.items():
    print(f"Processing release: {release}")
    for package_name, version in package_list.items():
        print(f"  Processing package: {package_name}")
        if package_name not in packages:
            packages[package_name] = {}
        # Add the supported version of this package for the given release of
        # Pyodide.
        packages[package_name][release] = version


updated_by = "automated script"
updated_at = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
# Write out the per-package JSON files
for package_name, data in packages.items():
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if response.status_code != 200:
        print(
            f"Warning: Could not fetch PyPI metadata for package '{package_name}'. Skipping."
        )
        continue
    pypi_metadata = response.json()
    summary = pypi_metadata.get("info", {}).get(
        "summary", "No summary available."
    )
    if not summary:
        # Some packages have an empty string or Noneas summary.
        summary = "No summary available."
    pyodide_versions = [f"`{version}`" for version in data.keys()]
    notes = f"""This package is [officially supported in Pyodide](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

To use it in PyScript simply add it to the `packages` section of your TOML configuration like this:

```
packages = ["{package_name}" ]
```

Or if you're using a JSON configuration, like this:

```
{{
    packages: ["{package_name}"]
 }}
```

Read more about using packages in PyScript [in our documentation](https://docs.pyscript.net/latest/user-guide/configuration/#packages).

Specifically, the following versions of the package are available for the following Pyodide releases:

Pyodide version: package name (version)
"""
    notes += "\n".join(
        [
            f"* `{k}`: `{package_name} ({data[k]})`"
            for k in sorted(data.keys(), reverse=True)
        ]
    )
    output = {
        "status": "green",
        "notes": notes,
        "supported_versions": data,
        "updated_by": updated_by,
        "updated_at": updated_at,
        "summary": summary,
    }
    filename = os.path.join("api", "package", f"{package_name}.json")
    print(f"Writing data for package '{package_name}' to '{filename}'")
    with open(filename, "w") as f:
        json.dump(output, f, indent=4)

#############################################
# Step 2: Generate top_100_pypi_packages.json
#############################################
print("Generating top_100_pypi_packages.json...")

# HugoVK generates these stats each month.
url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages.json"
response = requests.get(url)
response.raise_for_status()
top_pypi_data = response.json()

last_updated = top_pypi_data.get("last_update", "unknown")
top100 = top_pypi_data.get("rows", [])[:100]

# Create a summary JSON file for the top 100 packages. Include a check of the
# Pyodide support status from the previously generated data in the /data/
# directory, if it exists. Otherwise, default to "amber" status.
summary = {"last_updated": last_updated, "packages": []}
for entry in top100:
    package_name = entry.get("project")
    print("Processing top package: ", package_name)
    downloads = entry.get("download_count", 0)
    # Check for support data
    try:
        with open(os.path.join("api", "package", f"{package_name}.json"), "r") as f:
            support_data = json.load(f)
            status = support_data.get("status", "amber")
            desc = support_data.get("summary", "No summary available.")
    except FileNotFoundError:
        status = "amber"
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            pypi_metadata = response.json()
            desc = pypi_metadata.get("info", {}).get(
                "summary", "No summary available."
            )
        else:
            desc = "No summary available."
    summary["packages"].append(
        {
            "package_name": package_name,
            "downloads": downloads,
            "status": status,
            "summary": desc,
        }
    )

# Write out the summary JSON file
with open(os.path.join("api", "top_100_pypi_packages.json"), "w") as f:
    json.dump(summary, f, indent=4)
print("Generated top_100_pypi_packages.json")


#############################################
# Step 3: Process community contributed package status updates.
#############################################
print("Processing community contributed package status updates...")


# Discover when the script was last run to avoid overwriting newer data.
if os.path.exists(os.path.join("api", "last_run.json")):
    with open(os.path.join("api", "last_run.json"), "r") as f:
        last_run_data = json.load(f)
    last_run_time = datetime.datetime.fromisoformat(
        last_run_data.get("last_run")
    )
else:
    last_run_time = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRcJ_Co69zrLdxbOi7b5zlO7fuqooypL5ejpVPe59YC1CPXHWA-MpLhJBpGJ44FkM0ewmwMo7yq27Z/pub?output=csv"
response = requests.get(CSV_URL)
response.raise_for_status()
csv_file = StringIO(response.text)
reader = csv.DictReader(csv_file)
for row in reader:
    timestamp = datetime.datetime.strptime(
        row.get("Timestamp"), "%d/%m/%Y %H:%M:%S"
    ).replace(tzinfo=datetime.timezone.utc)
    if timestamp <= last_run_time:
        # This update is older than the last run of the script, so skip it.
        continue
    package_name = row.get("Package name (e.g. pandas, numba, my-cool-lib)")
    print(f"Processing community update for package: {package_name}")
    status = row.get("Suggested status").lower()
    if "red" in status:
        status = "red"
    elif "green" in status:
        status = "green"
    else:
        status = "amber"
    notes = row.get("Comments about status (Markdown allowed)")
    filename = os.path.join("api", "package", f"{package_name}.json")
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"supported_versions": {}, "summary": None}
    if not data["summary"]:
        # Try to fetch the summary from PyPI.
        pypi_url = f"https://pypi.org/pypi/{package_name}/json"
        pypi_response = requests.get(pypi_url)
        if pypi_response.status_code == 200:
            pypi_data = pypi_response.json()
            data["summary"] = pypi_data["info"].get("summary", "")
        else:
            data["summary"] = ""
    data["status"] = status
    if notes:
        data["notes"] = notes
    data["updated_by"] = "Community contribution via Google Forms"
    data["updated_at"] = timestamp.isoformat()
    print(
        f"Updating package '{package_name}' with community status '{status}'"
    )
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Record when the script was last run.
with open(os.path.join("api", "last_run.json"), "w") as f:
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print(f"Recording last run time: {now}")
    json.dump({"last_run": now}, f)


# Generate a final all.json file in the API directory containing details of
# all packages for easy access.
all_packages = {}
for filename in os.listdir(os.path.join("api", "package")):
    if filename.endswith(".json"):
        package_name = filename[:-5]
        with open(os.path.join("api", "package", filename), "r") as f:
            data = json.load(f)
        all_packages[package_name] = data
with open(os.path.join("api", "all.json"), "w") as f:
    json.dump(all_packages, f, indent=4)
print("Generated api/all.json")