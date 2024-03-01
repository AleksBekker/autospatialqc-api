# `autospatialqc` API

This project provides a Flask API for the Ioannis Vlachos Noncoding Lab's automatic spatial quality control website.

# How to contribute

Install Python and Poetry, and all of their dependencies.
Run `poetry install` in this project's main directory to install all python dependencies.

Create a MySQL server with a user with adequate permissions for app execution.

Modify the variables in the `.env.shared` file.
This file is public-facing, so no confidential information should be stored in it.

* `DB_DATABASE`: the SQL database on the host that contains all relevant API information. Throughout app scripts, this
  value is assumed to be 'autospatialqc'.
* `DB_USERNAME`: the SQL user's username. Throughout app scripts, this value is assumed to be 'noncoding'.

Create a `.env.secret` file in the project's main directory.
This file should never be committed to any repository.
Populate it with the following variables:

* `DB_HOST`: the SQL database's host.
* `DB_PASSWORD`: the SQL user's password.

Run `scripts/bootstrap.sh` to start the development server.

# How to deploy

I'm not entirely sure how this works, but the development server says we need something called a "production WSGI
server."

