.. _dev_tf:

=========================
GitHub Project Management
=========================

We use Terraform for managing the GitHub project settings (as applicable):

.. code-block:: bash

    $ export GITHUB_OWNER=bihealth
    $ export GITHUB_TOKEN=ghp_<thetoken>

    $ cd utils/terraform
    $ terraform init
    $ terraform import github_repository.varfish-server varfish-server
    $ terraform validate
    $ terraform fmt
    $ terraform plan
    $ terraform apply
