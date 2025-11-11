# PyScript Package Tracker 📦

A simple website to display Python package support within PyScript.

Use this site to check if a certain Python package is supported in the PyScript 
ecosystem (both Pyodide and MicroPython).

On the site's front page is a list of the most popular Python packages on PyPI
(collected via https://pypistats.org/), along with an indication via RAG
(red/amber/green 🚦) of the package's status for use with PyScript. A red status
🟥 means the package is not, or cannot be supported by PyScript, an amber status
🟨 means either the status of PyScript support is unknown or requires adjustment,
and a green status 🟩 means the package is supported by PyScript. Clicking on
the package takes you to the page for that package with more details.

At the top of the front page is a search box for package names on PyPI 🔍. 
Hitting return or pressing the "search" button returns a page for the given
package name. If no package exists with this name you'll be prompted to search
PyPI for the correct / matching package.

Each package has a page for it. The url for such page will be via the 
`/package?package=<package_name>` endpoint.

This page will display three possible states:

1. Red (this package is not supported by PyScript). Information about why this
   package isn't supported by PyScript will be displayed.
2. Amber (the status of this package is unknown or pending). The website will
   automatically try to serve a simple PyScript based project using this package,
   so importing the package can be attempted. A form will be displayed to allow
   folks to submit a report about the status of the package.
3. Green (this package is supported by PyScript). Any information about special
   cases for this package will also be displayed.

## API

The PyScript Packages website offers a simple API to access package information programmatically.
                    
Retrieve the status and metadata of packages in JSON format by making a GET request to the following endpoint:

```
GET /api/package/<package_name>.json
```

This will return a JSON object containing the following metadata (or respond with a 404 status code if the package is not found):


* *status*: The support status of the package (e.g., "green", "amber", "red").
* *summary*: The summary of the package from PyPI.
* *notes*: Brief notes, in Markdown, about the package's compatibility with PyScript.
* *updated_by*: The name or handle of the person who last updated this information.
* *updated_at*: The ISO 8601 timestamp of when this information was last updated.


For example, in Python, you can use the `requests` library to fetch such data about the `pandas` package:

```
import requests

response = requests.get("https://pkg.pyscript.net/api/package/pandas.json")
if response.status_code == 200:
    package_data = response.json()
    print(package_data)
else:
    print("Package not found or API error.")
```

If you wish to access data for all packages at once, you can use the following endpoint:

```
GET /api/all.json
```

Data about the top 100 packages is also available through this endpoint:

```
GET /api/top_100_pypi_packages.json
```

## Developer Setup

This is a very simple static website.

1. Fork the project found at: https://github.com/pyscript/pyscript-packages
2. Clone *your* fork of the repository, and change into the resulting directory:
```sh
$ git clone git@github.com:<YOUR_USERNAME>/pyscript-packages.git
$ cd pyscript-packages
```
3. Start a local server:
```sh
$ python -m http.server
```
4. Visit [localhost:8000](http://localhost:8000) to see the site working!
5. To build and refresh the site's data, ensure you have `requests` installed and run:
```sh
$ python build_data.py
```

That's it! Feel free to create PR's via GitHub. Thank you! 💐

## Acknowledgements

<p><svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="48" height="48" viewBox="0 0 48 48" style="vertical-align: text-bottom;">
<linearGradient id="I1Ls14S_9qH6lfzYnZ33la_F4uMFPZgS0gt_gr1" x1="20.837" x2="26.769" y1="4.234" y2="41.178" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#50d133"></stop><stop offset="1" stop-color="#3da126"></stop></linearGradient><path fill="url(#I1Ls14S_9qH6lfzYnZ33la_F4uMFPZgS0gt_gr1)" d="M11.575,8.758c1.128,0.177,2.553,0.46,4.074,0.892c-0.343,0.977-0.636,2.004-0.856,3.057 c-1.093-0.01-2.173,0.066-3.212,0.201C11.482,11.344,11.508,9.907,11.575,8.758z M10.082,13.144 c-0.086-1.246-0.092-2.411-0.06-3.435C9.969,9.761,9.91,9.805,9.857,9.858c-1.25,1.25-2.277,2.636-3.127,4.097 C7.717,13.663,8.842,13.373,10.082,13.144z M12.205,17.121c0.579-0.994,1.279-1.936,2.129-2.787 c0.045-0.045,0.094-0.082,0.139-0.126c-0.935,0.008-1.862,0.082-2.759,0.202C11.818,15.306,11.988,16.217,12.205,17.121z M10.929,18.242c-0.335-1.195-0.563-2.408-0.706-3.588c-1.763,0.336-3.316,0.797-4.461,1.189c-0.02,0.045-0.042,0.088-0.062,0.133 c0.502,1.124,1.236,2.597,2.204,4.132C8.84,19.432,9.852,18.793,10.929,18.242z M6.776,20.965c-0.716-1.122-1.297-2.2-1.77-3.162 c-0.593,1.827-0.915,3.719-0.969,5.621C4.795,22.666,5.717,21.813,6.776,20.965z M4.202,26.624 c0.252,1.922,0.784,3.808,1.593,5.604c0.371-1.03,0.848-2.205,1.45-3.425C6.083,28.069,5.056,27.31,4.202,26.624z M4.32,25.153 c0.907,0.765,2.102,1.686,3.489,2.571C8.361,26.718,9,25.715,9.732,24.763c-0.801-0.832-1.522-1.721-2.164-2.622 C6.243,23.212,5.127,24.298,4.32,25.153z M8.688,21.282c0.506,0.717,1.073,1.417,1.68,2.087c0.055-1.206,0.265-2.404,0.637-3.564 C10.193,20.258,9.413,20.754,8.688,21.282z M16.231,8.138c0.477-1.151,0.988-2.194,1.472-3.096 c-1.67,0.552-3.285,1.313-4.789,2.315C13.91,7.542,15.035,7.791,16.231,8.138z M17.774,8.625c0.919,0.321,1.849,0.705,2.762,1.151 c0.862-0.998,1.601-1.839,2.097-2.4c-0.72-0.597-1.862-1.515-3.063-2.385C19.007,5.977,18.364,7.222,17.774,8.625z M11.168,35.604 c-1.438-0.131-2.76-0.357-3.867-0.593c0.731,1.108,1.583,2.158,2.557,3.132c0.513,0.513,1.049,0.987,1.601,1.432 C11.307,38.432,11.184,37.07,11.168,35.604z M38.142,9.857C33.68,5.396,27.617,3.499,21.785,4.144 c1.581,1.206,2.84,2.294,2.932,2.375l0.767,0.667l-0.679,0.756c-0.016,0.018-0.896,1.001-2.17,2.466 c0.454-0.045,0.909-0.07,1.365-0.07c3.5,0,7.001,1.333,9.666,3.997c5.33,5.33,5.33,14.002,0,19.332 c-4.618,4.617-11.744,5.226-17.032,1.842c-1.014,0.147-2.034,0.214-3.031,0.214c-0.447,0-0.886-0.016-1.321-0.038 c0.027,1.87,0.233,3.567,0.436,4.817c3.389,2.319,7.333,3.492,11.283,3.492c5.122,0,10.243-1.95,14.142-5.848l0,0 C45.94,30.344,45.94,17.656,38.142,9.857z M15.296,34.535c-0.33-0.273-0.652-0.56-0.961-0.868c-0.671-0.671-1.257-1.396-1.759-2.16 c-0.169,1.027-0.26,2.057-0.286,3.06C13.268,34.62,14.282,34.611,15.296,34.535z M17.185,10.131 c-0.282,0.793-0.523,1.621-0.721,2.464c0.91-0.602,1.88-1.069,2.88-1.43c0.035-0.041,0.074-0.088,0.109-0.129 C18.703,10.69,17.941,10.391,17.185,10.131z M10.47,25.799c-0.606,0.824-1.151,1.685-1.624,2.554 c0.865,0.5,1.789,0.957,2.748,1.349C11.022,28.453,10.646,27.138,10.47,25.799z M11.541,30.983 c-1.146-0.437-2.237-0.972-3.252-1.553c-0.775,1.586-1.341,3.103-1.722,4.276c1.202,0.291,2.823,0.608,4.613,0.779 C11.214,33.341,11.324,32.161,11.541,30.983z"></path>
</svg><strong style="color: #111111; font-size: 3.2em;">Anaconda</p>

Huge thanks to [Anaconda](https://anaconda.com/) for their continued support of PyScript.