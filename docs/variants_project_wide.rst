.. _variants_project_wide:

==============================
Project-Wide Queries and Stats
==============================

-----------------------
Project-Wide Statistics
-----------------------

You can also view joint statistics for all cases within a project.
For this, open a project's case list (open the project detail view, then click the :guilabel:`Cases` icon in the left bar).

Here, the project-wide variant statistics will be displayed above your cases if it has been generated already.
If you want to (re)-generate it, use the :guilabel:`Recompute Project-Wide Stats` button on the top right.
This will create a background job for the recomputation (it might take quite some time).
After the job is complete, the updated data will be displayed on the case list.


--------------------
Project-Wide Queries
--------------------

Further, you can perform queries to all cases in your project.
For this, navigate to the project's case list.
Then, click the :guilabel:`Joint Filtration` button on the top right.

The form that opens is very similar to the one described in :ref:`variants_filtration` with the following differences:

- All members of all cases in your project will appear.
- Instead of having one row for each variant and one genotype column for each sample, you have one row for each variant and sample and one column with genotype information only.
  There is an additional column that gives the name of the sample that the row is for.
- The TSV and Excel file download generation creates similarly-structured tables.
- VCF export is currently not supported yet.
