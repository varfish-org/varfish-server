.. _project_permissions:

======================
Project Access Control
======================

In VarFish, access to data is organized in **Projects**.
Projects can be grouped into possibly nested **Categories** and access.
Users are assigned **Roles** in projects and get access to the project's data through these role assignments.

Projects can either be local or come from a central SODAR site.
In the first case, the project owners can change the user in projects through the VarFish site itself.
In the second case, user assignment is performed in the central SODAR site.

---------------
Project Details
---------------

When selecting a project, you are directed to its Details view.
Here, you can see its README information, the overview from the further VarFish components, the project timeline, and background jobs.

.. note::

    The overview page will only display the five most recent entries in each category.
    You can reach the full information using the corresponding buttons in the left navigation bar.

    Most importantly use the :guilabel:`Cases` link to see the full list of cases in a project.

.. figure:: figures/project_details.png
    :alt: Details view for the demo project.
    :width: 60%
    :align: center

    This figure shows the project details of the demo project.
    On the left, you can see the navigation bar to the different apps active for the project.
    On the right, you can see the project overview showing up to the five most recent entries only.

**VarFishApp Overview**
    See the latest imported cases.

**Project Timeline**
    Keep track of recent project settings.

**Background Jobs App Overview**
    Background job status, e.g., for file exports.
