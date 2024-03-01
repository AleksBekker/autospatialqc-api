#!/usr/bin/env python

import json
from sys import argv

from autospatialqc_api import Database, Sample
from autospatialqc_api.environment import require_env


def main():

    db = Database(
        host=require_env("DB_HOST"),
        database=require_env("DB_DATABASE"),
        username=require_env("DB_USERNAME"),
        password=require_env("DB_PASSWORD"),
    )

    path = argv[1]
    with open(path) as file:
        data = json.load(file)

    for dictionary in data:
        sample = Sample.model_validate(dictionary)
        db.insert_sample(sample)
        print(f"Sample ({sample.assay}, {sample.tissue}) successfully added.")


if __name__ == "__main__":
    main()
