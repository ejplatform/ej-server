============
Branch model
============

Ej-server uses "master" as the main development branch and tags for stable
releases. Generally, we want to move code to the master as soon as possible, but
we need some discipline to make it work:

* **Do not commit** if a test is breaking. Run tests locally before committing
  and please make sure no test breaks. If a test breaks and cannot be fixed
  please create a separate branch to stabilize the feature then perform a merge
  commit when everything is fine.
* Commits with broken tests should be reverted ASAP. Please revert your commit
  and warn the other devs if a commit must be reverted. This may happen from time
  to time since CI tests are more rigid than the local tests used for TDD.
* Generic maintenance contributions should be committed directly to the master.
  This includes:
    * Bug fixes.
    * Small tweaks to styles and HTML templates.
    * Writing new tests for integrated features.
    * Refactor small parts of the code to increase code quality or performance.
    * Implementation of simple isolated features that do not affect other parts
      of the system (i.e., creates a new view or api entry point)
* We configured a commit hook for flake8 to ensure that no style bugs are
  introduced in a commit. CI tests for code style regressions.
