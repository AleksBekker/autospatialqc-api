#!/usr/bin/env python

import json
from sys import argv

from autospatialqc_api import Database, Sample
from autospatialqc_api.environment import require_envs


def main():

    db = Database(
        **require_envs(
            host="DB_HOST",
            database="DB_NAME",
            username="DB_USERNAME",
            password="DB_PASSWORD",
        )
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
