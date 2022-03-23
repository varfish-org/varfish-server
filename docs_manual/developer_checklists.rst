.. _developer_checklists:

==========
Checklists
==========

--------
Releases
--------

Prerequisites:

- Have all issues done for the next milestone.

Tasks:

1. Create ticket with the following template and assign it to the proper milestone.

    .. code-block:: markdown

        Release for version vVERSION

        - [ ] edit `HISTORY.rst` and ensure a proper section is added
        - [ ] edit `admin_upgrade.rst` to reflect the upgrade instructions
        - [ ] create a git tag `v.MAJOR.MINOR.PATCH` and `git push --tags`
        - [ ] create a "Github release` based on the tag with the text

              ```
              All details can be found in the `HISTORY.rst` file.
              ```

2. Follow through the items.

--------------------------
Data & Software Validation
--------------------------

Prerequisites:

- Have all background data imported into dedicated instances for validation.
  (Internally we use ``varfish-build-release-{37,38}.cubi.bihealth.org``).
- Create the ``varfish-site-data-X.tar.gz`` tarball with the database dump.
- Have a token ready for the root user.

Tasks:

1. Create a ticket with the following template.

    .. code-block:: markdown

        Validate data for:

        - **VarFish:** vMAJOR.MINOR.PATCH
        - **Site Data:** vVERSION (`sha256:CHECKSUM`)
        - **Genome Build:** GRCh37 or GRCh38

        Result Reports:

        PASTE HERE

2. Use the ``varfish-wf-validation`` Snakemake workflow for running the validation.

3. Paste the result reports into the tickets.
