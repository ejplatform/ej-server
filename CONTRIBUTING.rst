==================
Contributing to EJ
==================

For member of the Organization 
=========================================

EJ main repository uses "master" as the main development branch and tags for stable
releases. Generally, we want to move code to the master as soon as possible, but
we need some discipline to make it work. The master is locked and submissions
of new features are done using pull requests.

For each issue to be solved, follow the procedure below:

* In case of your development environment isn't already built, then clone the
  repository, follow the installation guide at `README.rst`_. Install the
  commit hooks to statically check your code before each commit::

    $ inv install-hooks

* Checkout to a branch you created to solve your issue. For simple things,
  use the generic ``dev`` branch, otherwise, describe what you are going to do
  e.g.::

   $ git checkout -b facebook-login

* Always run all tests before any commit,otherwise your pull request will not be
  merged!

  ::

   $ pytest   # backend tests

* After you finished, open a pull request MASTER::

   ejplatform/ej-server/<your-branch>  ==>  ejplatform/ej-server/master

  and wait until Travis CI, GitLab CI and Code Climate run all the integration tests.
  Your PR should have a small explanation of what it does preferably with a link
  to the originating issue. Please tell explicitly if the PR closes that issue
  or not and move the issue to the proper slot on the Projects_ board.
* Any contributor can merge your PR after your tests passed. Ideally, we can use
  a second pair of eyes to review the code, specially for tricky code. But, if
  you are in hurry, you can accept your own PR.
* If changes were made in a branch different from ``dev``, then delete it after
  your PR gets merged.

.. _Projects: https://github.com/ejplatform/ej-server/projects/1


For external Contributors
=========================================

Just follow all the steps above, the difference will be that you will need to create a fork.

Forking a repository is really straightforward:

1. Make sure you’re logged into GitHub with your account.
2. Find the GitHub repository with which you’d like to work.
3. Click the Fork button on the upper right-hand side of the repository’s page.

After the fork clone you fork

    $ git clone https://github.com/<your-user>/ej-server.git

Create a branch there and start Working :)


What should be committed directly to dev?
=========================================

``dev`` is the branch to go for small maintenance contributions and it is likely
that more than one developer will be working on it simultaneously.
Acceptable work to do in ``dev`` includes:

* Small bug fixes that affects only a few functions in a single file.
* Small tweaks in CSS and HTML templates.
* Writing new tests for integrated features.
* Refactor small parts of the code to increase code quality or performance.
* Implementation of simple isolated features that do not affect other parts
  of the system (i.e., create a new view or api entry point)
* Updates to the .po files by translators.
* Updates to the documentation.

.. _README.rst: README.rst


Style Guide
=========================================
 
We use the PEP8(https://www.python.org/dev/peps/pep-0008/) as a guide style we also recomend the use of 
Pyflakes there are a lot of plugins available for various IDE's:

* Atom linter-flake8(https://atom.io/packages/linter-flake8)
* Vs Code (https://dev.to/j0nimost/setting-up-pep8-and-pylint-on-vs-code-34h)
* Sublime (https://packagecontrol.io/packages/Python%20PEP8%20Autoformat)

If you do not want to use IDE's here we have the basic guidelines for

* Indentation - Use 4 spaces per indentation level.
* Maximum Line Length - Limit all lines to a maximum of 79 characters.
* Blank Lines - Surround top-level function and class definitions with two blank lines.
* Source File Encoding - Code in the core Python distribution should always use UTF-8 (or ASCII in Python 2).
