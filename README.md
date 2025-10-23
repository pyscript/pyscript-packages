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
   automatically try to serve a simple terminal based project using this package,
   so importing the package can be attempted. A form will be displayed to allow
   folks to submit a report about the status of the package.
3. Green (this package is supported by PyScript). Any information about special
   cases for this package will also be displayed.

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


That's it! Feel free to create PR's via GitHub. Thank you! 💐