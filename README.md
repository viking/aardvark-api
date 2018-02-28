aardvark-api
============

Aardvark is a package management system for R. Primary features and goals
include:

* completely automated package submission
* version management

### Automated package submission

Package submission to CRAN can be a frustrating experience due to the changing
requirements and checks that can occur, sometimes without notice. While CRAN
policies exist to create a healthy ecosystem of packages, the somewhat manual
submission process can cause delays and inhibit package releases.

### Version management

R's builtin package system does not easily allow for the possibility of
installing different versions of packages. If packages are updated with changed
functionality, code that depends on the old versions will no longer function.
This is a problem for reproducible research.

### Alternatives

There are some existing ways to get around these problems, such as by using
[packrat](https://rstudio.github.io/packrat/). Packrat leverages CRAN and the
`install_github` function in the
[devtools](https://cran.r-project.org/web/packages/devtools/index.html) package
to provide a reproducible environment for package dependencies.
