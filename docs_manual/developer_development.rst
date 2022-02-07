.. _developer_development:

===========
Development
===========

VarFish is based on the SODAR core framework which has a `developer manual <https://sodar-core.readthedocs.io/en/latest/development.html>`_ itself.
It is worth having a look there.
The following lists parts that are useful in particular:

- `Models <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#models>`_
- `Rules <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#rules-file>`_
- `Views <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#views>`_
- `Templates <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#templates>`_
    - `Icons <https://sodar-core.readthedocs.io/en/latest/dev_general.html#using-icons>`_
- `Forms <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#forms>`_

------------------
Mandatory Trailers
------------------

In addition, the following rules apply to git commit trailers:

- You may specify ``Breaks-API: true`` trailer if your commit breaks the (REST) API (and thus the CLI)
- You may specify ``Breaks-Data-Import: true`` trailer if your commit breaks backward compatibility with data import.
- You **must** provide ``Influences-Query-Result:`` with value ``true`` or ``false`` to mark whether your change may change the variant query results.
- You **must** either provide a ``Related-Issue:`` trailer which references a Github commit or ``No-Related-Issue:``.
  When specifying ``No-Related-Issue:`` you can use the following values:

    - ``trivial`` - for trivial changes (commit **must** pass code review)
    - ``reason FREE TEXT`` - provide a terse free-text reason for why there is no related reason
