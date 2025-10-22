# PyScript Package Tracker 📦

A simple website to display Python package support within PyScript.

PyScript-ers can quickly and easily see if a certain Python package is
supported in the PyScript ecosystem (both Pyodide and MicroPython).

On the front page is a list of the most popular Python packages on PyPI
(collected via https://pypistats.org/), along with an indication via RAG
(red/amber/green 🚦) of the package's status for use with PyScript. A red status
🟥 means the package is not, or cannot be supported by PyScript, an amber status
🟨 means either the status of PyScript support is unknown or pending more work,
and a green status 🟩 means the package is supported by PyScript. Clicking on
the package takes you to the page for that package with more details.

At the top of the front page is a search box for package names on PyPI 🔍. 
Typing into the box creates autosuggests for matching packages. Hitting return
or pressing the "search" button produces a page with the closest matches. The
results page will be at the `/search?<package_name>` endpoint. Clicking on a 
match takes you to the page for that package with more details.

Each package has a page for it. The url for such page will be via the 
`/package/<package_name>` endpoint.

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

This is a very simple Django based website.

1. Fork the project found at: https://github.com/pyscript/pyscript-packages
2. Clone *your* fork of the repository, and change into the resulting directory:
```sh
$ git clone git@github.com:<YOUR_USERNAME>/pyscript-packages.git
$ cd pyscript-packages
```
3. Create a virtual environment, and activate it:
```sh
$ python -mvenv env
$ source env/bin/activate
```
4. With the virtual environment active, install the dependencies:
```sh
$ pip install -r requirements.txt
```
5. Run the test suite (to ensure everything is working as expected):
```sh
$ ./manage.py test
```
6. Start a development server, and try the site locally (http://localhost:8000/):
```sh
$ ./manage.py runserver
```

That's it! Feel free to create PR's via GitHub. Thank you! 💐