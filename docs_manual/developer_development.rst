.. _developer_development:

===========
Development
===========

-----------------------
Working With Sodar Core
-----------------------

VarFish is based on the Sodar Core framework which has a `developer manual <https://sodar-core.readthedocs.io/en/latest/development.html>`_ itself.
It is worth reading its development instructions.
The following lists the most important topics:

- `Models <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#models>`_
- `Rules <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#rules-file>`_
- `Views <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#views>`_
- `Templates <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#templates>`_
    - `Icons <https://sodar-core.readthedocs.io/en/latest/dev_general.html#using-icons>`_
- `Forms <https://sodar-core.readthedocs.io/en/latest/dev_project_app.html#forms>`_


-------------
Running Tests
-------------

Running the VarFish test suite is easy, but can take a long time to finish (>10 minutes).

.. code-block:: bash

   $ make test

You can exclude time-consuming UI tests:

.. code-block:: bash

   $ make test-noselenium

If you are working on one only a few tests, it is better to run them directly.
To specify them, follow the path to the test file, add the class name and the test function, all separated by a dot:

.. code-block:: bash

   $ python manage.py test -v2 --settings=config.settings.test variants.tests.test_ui.TestVariantsCaseFilterView.test_variant_filter_case_multi_bookmark_one_variant

This would run the UI tests in the variants app for the case filter view.


----------------
Working With Git
----------------

In this section we will briefly describe the workflow how to contribute to VarFish.
This is not a git tutorial and we expect basic knowledge.
We recommend `gitready <https://gitready.com/>`_ for any questions regarding git.
We do use `git rebase <https://gitready.com/intermediate/2009/01/31/intro-to-rebase.html>`_ a lot.

In general, we recommend to work with ``git gui`` and ``gitk``.

The first thing for you to do is to create a fork of our github repository in your github space.
To do so, go to the `VarFish repository <https://github.com/bihealth/varfish-server>`_ and click on the ``Fork`` button in the top right.

Update Main
===========

`Pull with rebase on gitready <https://gitready.com/advanced/2009/02/11/pull-with-rebase.html>`_

.. code-block:: bash

    $ git pull --rebase


Create Working Branch
=====================

Always create your working branch from the latest main branch.
Use the ticket number and description as name, following the format ``<ticket_number>-<ticket_title>``, e.g.

.. code-block:: bash

    $ git checkout -b 123-adding-useful-feature

Write A Sensible Commit Message
===============================

A commit message should only have 72 characters per line.
As the first line is the representative, it should sum up everything the commit does.
Leave a blank line and add three lines of github directives to reference the issue.

.. code-block::

    Fixed serious bug that prevented user from doing x.

    Closes: #123
    Related-Issue: #123
    Projected-Results-Impact: none

Cleanup Before Pull Request
===========================

We suggest to first squash your commits and then do a rebase to the main branch.

Squash Multiple Commits (Or Use Amend)
--------------------------------------

`Pull with rebase on gitready <https://gitready.com/advanced/2009/02/10/squashing-commits-with-rebase.html>`_

We prefer to have only one commit per feature (most of the time there is only one feature per branch).
When your branch is rebased on the main branch, do:

.. code-block:: bash

    $ git rebase -i main

Alternatively, you can always use ``git commit --amend`` to modify your last commit.
This allows you also to change your latest commit message.

Rebase To Main
--------------

Make sure your main is up-to-date. In you branch, do:

.. code-block:: bash

    $ git checkout 123-adding-useful-feature
    $ git rebase main

In case of conflicts, resolve them (find ``<<<<`` in conflicting files) and do:

.. code-block:: bash

    $ git add conflicting.file
    $ git rebase --continue

If unsure, abort the rebase:

.. code-block:: bash

    $ git rebase --abort

Push To Origin
--------------

.. code-block:: bash

    $ git push origin 123-adding-useful-feature

In case you squashed and/or rebased and already pushed the branch, you need to force the push:

.. code-block:: bash

    $ git push -f origin 123-adding-useful-feature
