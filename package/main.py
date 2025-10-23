"""
A MicroPython based script for checking PyScript package support.

It does four things:

1. Extracts the package name from the query string (e.g. `/package?package=<package_name>`).
2. Grabs the package metadata from PyPI (e.g. https://pypi.org/pypi/<package_name>/json).
3. Grabs the package support status from the /data/<package_name>.json file.
4. If step 3 fails, it falls back to a default "amber" status and attempts to make a simple
   Pyodide import test for the package, along with an embedded Google form for user feedback.

That's it!

The static JSON data files in this website are of the form:
{
    "status": "red" | "amber" | "green",
    "notes": "Some notes about the package support status as Markdown.",
    "updated_by": "A name or handle of the person who last updated this file.",
    "updated_at": "ISO 8601 timestamp of when this file was last updated."
}
"""
from pyscript import fetch, js_import
from pyscript.web import page
import js


marked = None
purify = None


async def load_js_modules():
    """
    Load the marked and dompurify JS modules.
    """
    global marked, purify
    (marked, purify) = await js_import(
        "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js",
        "https://esm.run/dompurify",
    )


def get_package_name():
    """
    Extract the package name from the query string.
    """
    query_string = js.window.location.search
    url_params = js.URLSearchParams.new(query_string)
    package_name = url_params.get("package")
    if package_name:
        return package_name
    return None


def from_markdown(raw_markdown):
    """
    Convert markdown to sanitized HTML.
    """
    result = raw_markdown
    global marked, purify
    if marked:
        result = purify.default().sanitize(marked.parse(raw_markdown))
    return result


async def get_json(url):
    """
    Fetch JSON data from a URL.
    """
    response = await fetch(url)
    if response.status == 200:
        data = await response.json()
        return data
    return None


async def fetch_pypi_metadata(package_name):
    """
    Fetch package metadata from PyPI.
    """
    pypi_url = f"https://pypi.org/pypi/{package_name}/json"
    return await get_json(pypi_url)


async def fetch_package_data(package_name):
    """
    Fetch package support data from the /data/<package_name>.json file.
    """
    data_url = f"/data/{package_name}.json"
    return await get_json(data_url)

async def main():
    """
    Main function to handle the package support check.
    """
    target = page["#app"]
    await load_js_modules()
    package_name = get_package_name()
    if not package_name:
        target.innerHTML = "<h2>No package specified.</h2>"
        return

    pypi_metadata = await fetch_pypi_metadata(package_name)
    if not pypi_metadata:
        target.innerHTML = f"<h2>Package '{package_name}' not found on PyPI.</h2>"
        return
    
    # Extract relevant metadata
    package_info = pypi_metadata.get("info", {})
    package_author = package_info.get("author", "unknown")
    package_author_email = package_info.get("author_email", "unknown")
    package_classifiers = package_info.get("classifiers", [])
    package_description = package_info.get("description", "No description available.")
    package_urls = package_info.get("project_urls", {})
    package_summary = package_info.get("summary", "No summary available.")
    package_version = package_info.get("version", "unknown")

    urls = "<br/>".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in package_urls.items())

    metadata = f"""
    <h2>{package_name} ({package_version})</h2>
    <p><strong>Author:</strong> {package_author} ({package_author_email})</p>
    <p><strong>Summary:</strong> {package_summary}</p>
    <p><details><summary><strong>Description:</strong></summary> {from_markdown(package_description)}</details></p>
    <p><details><summary><strong>Classifiers:</strong></summary> {'<br/>'.join(package_classifiers)}</details></p>
    <p><strong>Project URLs:</strong> {urls}</p>
    <hr>
    """


    package_data = await fetch_package_data(package_name)
    if not package_data:
        # Default to amber status if no data file exists
        package_data = {
            "status": "amber",
            "notes": "No support data available. Please help us improve this by submitting feedback below.",
            "updated_by": "N/A",
            "updated_at": "N/A",
        }
    


    status = package_data.get("status", "amber")
    notes_markdown = package_data.get("notes", "")
    notes_html = from_markdown(notes_markdown)

    target.innerHTML = f"""
    <h2>Package: {package_name}</h2>
    <h3>Status: {status.upper()}</h3>
    {metadata}
    <div>{notes_html}</div>
    """
    if status == "amber":
        target.innerHTML += """
        <hr>
        <h3>Submit Feedback</h3>
        <p>GOOGLE FORM EMBED HERE</p>
        """
    
await main()