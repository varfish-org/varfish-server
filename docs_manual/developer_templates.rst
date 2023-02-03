.. _developer_templates:

===========================
Templates (for Issues etc.)
===========================

We do organize bug reports and feature request in the
`Github issue tracker <https://github.com/bihealth/varfish-server/issues/new/choose>`_.
Please choose the template that fits best what you want to report and fill out
the questions to help us decide on how to approach the task.

-----------
Bug Reports
-----------

The template for bug reports has the following form (an up-to-date form is located in the Github issue tracker):

.. code-block:: markdown

    **Describe the bug**
    A clear and concise description of what the bug is.

    **To Reproduce**
    Steps to reproduce the behavior:
    1. Go to '...'
    2. Click on '....'
    3. Scroll down to '....'
    4. See error

    **Expected behavior**
    A clear and concise description of what you expected to happen.

    **Screenshots**
    If applicable, add screenshots to help explain your problem.

    **Desktop (please complete the following information):**
     - OS: [e.g. iOS]
     - Browser [e.g. chrome, safari]
     - Version [e.g. 22]

    **Smartphone (please complete the following information):**
     - Device: [e.g. iPhone6]
     - OS: [e.g. iOS8.1]
     - Browser [e.g. stock browser, safari]
     - Version [e.g. 22]

    **Additional context**
    Add any other context about the problem here.

Root Cause Analysis
===================

In the following, a root cause analysis (RCA) needs to be done. The ticket will get an answer with the title
**Root Cause Analysis** and a thorough description of what might cause the bug.

Resolution Proposal
===================

When the root cause is determined, a solution needs to be proposed, following this form:

.. code-block:: markdown

    **Resolution Proposal**
    e.g. The component X needs to be changed to Y so Z is not executed when M occurs.

    **Affected Components**
    e.g. VarFish server

    **Affected Modules/Files**
    e.g. variants module or queries.py

    **Required Architectural Changes**
    e.g. Function F needs to be moved to X.

    **Required Database Changes**
    i.e. name any model that needs changing, to be added and will lead to a migration

    **Backport Possible?**
    e.g., "Yes" if this is a bug fix or small change and should be backported to the current stable version

    **Resolution Sketch**
    e.g. Change X in F. Then do Y.


Commits
=======

All commits should adhere to `semantic pull requests <https://www.conventionalcommits.org/en/v1.0.0/>`__.
That is, the commit messages look like this:

::

    prefix: message here

Valid prefixes types are defined in `here <https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type>`__.

Common examples are:

::

    fix: fixing bug (#number)
    feat: implementing feature (#number)
    chore: will not go to changelog (#number)

Almost all commits should refer to a ticket in trailing parenthesis, e.g.

::

    fix: resolve some issue (#NUMBER)

Note that we enforce squash commits for pull requests.
All of your commits will be squashed when merged.
The pull request should be broken into semantic parts and checking this is part of the code review process.

Fix & Pull Request
==================

1. Create new branch (name starts with issue number), e.g. ``123-fix-for-issue``
2. Create pull request in "Draft" state
3. Fix problem, ideally in a test-driven way, remove "Draft" state

Review & Merge
==============

1. Perform code review
2. Ensure fix is documented in changelog (link to bug and PR #ids)

----------------
Feature Requests
----------------

A feature request follows the same workflow as a bug request (an up-to-date form is located in the Github issue tracker):

.. code-block:: markdown

    **Is your feature request related to a problem? Please describe.**
    A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

    **Describe the solution you'd like**
    A clear and concise description of what you want to happen.

    **Describe alternatives you've considered**
    A clear and concise description of any alternative solutions or features you've considered.

    **Additional context**
    Add any other context or screenshots about the feature request here.


Design
======

In the following, the design of the feature needs to be specified:

.. code-block:: markdown

    **Implementation Proposal**
    e.g. The component X needs to be changed to Y so Z is not executed when M occurs.

    **Affected Components**
    e.g. VarFish server

    **Affected Modules/Files**
    e.g. variants module or queries.py

    **Required Architectural Changes**
    e.g. Function F needs to be moved to X.

    **Implementation Sketch**
    e.g. Change X in F. Then do Y.

Implement & Test
================

1. Create feature branch, named starting with issue ID
2. Perform implementation, ideally in a test-driven way
3. Tests and documentation must be augmented/updated as well

Review & Merge
==============

1. Perform code review
2. Ensure change is documented in changelog (link to feature issue and PR #ids)
