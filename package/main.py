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
from pyscript import fetch, js_import, when
from pyscript.web import page, h3, script, iframe, p
import js
import asyncio


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
        return package_name.strip()
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
    await load_js_modules()
    target = page["#app"][0]
    loading_text = page["#loading-text"][0]
    metadata_target = page["#metadata"][0]
    smoketest_target = page["#smoketest"][0]
    feedback_target = page["#feedback"][0]
    package_name = get_package_name()
    if not package_name:
        target.innerHTML = "<h2>🤷 No package specified.</h2>"
        return
    pypi_metadata = await fetch_pypi_metadata(package_name)
    if not pypi_metadata:
        target.innerHTML = f"<h2>🤷 Package '{package_name}' not found on PyPI.</h2>"
        return
    # Remove the loading text.
    loading_text.remove()
    
    # Extract relevant metadata from PYPI.
    package_info = pypi_metadata.get("info", {})
    package_author = package_info.get("author", "unknown")
    package_summary = package_info.get("summary", "No summary available.")

    # Try to extract package support data and work out the status.
    package_data = await fetch_package_data(package_name)
    if not package_data:
        # Default to amber status if no data file exists
        package_data = {
            "status": "amber",
            "notes": "No support data available. Please help us improve this by running some tests and submitting feedback. 🤗",
            "updated_by": "N/A",
            "updated_at": "N/A",
        }
    status_values = {
        "red": "❌ Red - Not Supported",
        "amber": "⚠️ Amber - Partial Support / Unknown",
        "green": "✅ Green - Supported",
    }
    status = package_data.get("status", "amber")
    status_content = status_values[status]
    notes_markdown = package_data.get("notes", "")
    notes_html = from_markdown(notes_markdown)

    # Assemble the final HTML result.

    metadata_target.innerHTML = f"""
    <h2><a href="https://pypi.org/project/{package_name}/" target="_blank">{package_name}</a></h2>
    <h3>{status_content}</h3>
    <p><strong>Author:</strong> {package_author}</p>
    <p><strong>Summary:</strong> {package_summary}</p>
    <p><a href="https://pypi.org/project/{package_name}/" target="_blank">PyPI page</a> 📦 | <a href="https://pypistats.org/packages/{package_name}" target="_blank">PyPI stats</a> 📈</p>
    <hr />
    <div>{notes_html}</div>
    """

    if status == "amber":
        # We can try a simple Pyodide import test for amber packages.
        # Add a simple script to attempt the import.
        # Note: This is a very basic test and may not cover all cases.
        smoketest_target.append(h3(f"🔬 Pyodide <code>import {package_name}</code> check"))
        smoketest_target.append(p("The script below will attempt to import the package in Pyodide. If successful, you'll see a confirmation message. If there are issues, error messages will appear in the output."))
        smoketest_target.append(p("You can then add your own code to test the package further!"))
        smoketest_target.append(p("Mouseover the editor, then press the ▶️ Run button to execute the test script. This may take a few seconds as Pyodide loads the package."))
        code = f"""# Simple Pyodide import test for the {package_name} package.
import micropip
# Install the package via micropip.
await micropip.install("{package_name}")
# Now try to import it!
import {package_name.replace("-", "_")}
# If we reach this point, the import was successful.
print("✅ Successfully imported {package_name}!")
# If there was an error, it will be shown below in red.
# Now add some code of your own to exercise and test the package!
# Re-run the code and tell us what you find in the feedback form below. 💐
"""
        editor = script(code, type="py-editor", id="test-script")
        editor.setAttribute("config", '{"packages": ["micropip"]}')
        smoketest_target.append(editor)
        # Add a Google form for user feedback.
        example_description = js.encodeURIComponent(f"""I attempted to import the `{package_name}` package in Pyodide. I used the following code:

```
{code.strip()}
```

Here's a paste of the output:

<YOUR OUTPUT HERE>

My experience was: 

<DESCRIBE YOUR EXPERIENCE HERE>
""")
        feedback_target.append(h3("📝 Feedback"))
        feedback_target.append(p("Please help us improve the package support data by providing your feedback via this form. Let us know if the package worked, any issues you encountered, and any additional notes you'd like to share. Feel free to paste your code snippets or any error messages. Thank you! 🙏"))
        feedback_target.append(iframe(src=f"https://docs.google.com/forms/d/e/1FAIpQLSdDhXu0h0BjTsMgjnvfW5P1YKnytOKxYrtC41o6fXizYkgnng/viewform?embedded=true&entry.1624544771={package_name}&entry.902804967={example_description}", width="100%", height="1100", frameborder="0", marginheight="0", marginwidth="0", id="feedback-form"))

await main()