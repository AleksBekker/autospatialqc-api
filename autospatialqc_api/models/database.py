import functools
from operator import or_ as binary_or

import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from mysql import connector

from autospatialqc_api.models import Permissions, Sample, User
from autospatialqc_api.models.errors import InvalidCredentials, SampleNameCollision, SampleNotFound, UserNotFound


class Database:

    def __init__(self, host: str, database: str, username: str, password: str):
        """Initializes a new database object.

        Arguments:
            host (str): the database's host.
            database (str): the database to use.
            username (str): the SQL user's username.
            password (str): the SQL user's password.

        Note:
            The SQL user's password should be stored in a `.env.secret` file or environmental variable with the name
              "NC_SQL_PASSWORD".
        """

        self.__host = host
        self.__database = database
        self.__username = username
        self.__password = password

        self.connect()

    def connect(self):
        self.__connection = connector.connect(
            host=self.__host, user=self.__username, password=self.__password, database=self.__database
        )

    def commit(self):
        self.__connection.commit()
        self.connect()  # TODO: is this necessary?

    def get_user(self, email: str) -> User:
        """Finds a User from the database.

        Arguments:
            email (str): the user's email.

        Returns:
            A User object containing this user's data.

        Raises:
            UserNotFound: if this email is not in the database.
        """

        cursor = self.__connection.cursor()
        cursor.execute(
            """
                SELECT internal_id FROM users u
                WHERE email = %s;
            """,
            [email],
            multi=True,
        )

        if (results := cursor.fetchone()) is None:
            raise UserNotFound(email)

        id = int(results[0])  # type: ignore[reportArgumentType]
        permissions = self.get_permissions(email)

        return User(id=id, email=email, permissions=permissions, authenticated=False)

    def get_validated_user(self, email: str, password: str) -> User:
        """Finds and validates a user from the database.

        Arguments:
            email (str): the user's email.
            password (str): the user's password.

        Returns:
            A User object describing the user with these credentials.

        Raises:
            UserNotFound: if this email is not associated with a user in the database.
            InvalidCredentials: if the password is not correct.
        """

        user = self.get_user(email)

        cursor = self.__connection.cursor()
        cursor.execute(
            """
                SELECT password_hash FROM users u
                WHERE email = %s;
            """,
            [email],
            multi=False,
        )

        password_hash = str(cursor.fetchone()[0])  # type: ignore[reportArgumentType, reportOptionalSubscript]

        hasher = PasswordHasher()

        # TODO: implement more robust exception handler
        try:
            if not hasher.verify(password_hash, password):
                raise InvalidCredentials()

        except VerifyMismatchError:
            raise InvalidCredentials()

        user.authenticated = True

        return user

    def get_permissions(self, email: str) -> Permissions:
        """Gets the permissions for a user.

        Arguments:
            email (str): the user's email.

        Returns:
            This user's permissions flag if the email is in the database, Permissions.NONE otherwise.
        """

        cursor = self.__connection.cursor()
        cursor.execute(
            """
                SELECT permission_name FROM users u
                LEFT JOIN user_permissions up ON u.internal_id = up.user_id
                LEFT JOIN permissions p ON p.id = up.permission_id
                WHERE email = %s;
            """,
            [email],
            multi=True,
        )

        permission_gen = (Permissions.from_str(tup[0]) for tup in cursor.fetchall())  # type: ignore[reportArgumentType]
        return functools.reduce(binary_or, permission_gen, Permissions.NONE)

    def change_password(self, user: User, new_password: str | bytes):
        """Change a user's password.

        Arguments:
            user (User): the user data for the user whose password is to be modified.
            new_password (bytes): the password to add to the database. This password will be hashed before storage.
        """

        if isinstance(new_password, str):
            new_password = new_password.encode("utf-8")

        new_hash = argon2.hash_password(new_password)

        cursor = self.__connection.cursor()
        cursor.execute(
            """
                UPDATE users
                SET password_hash = %s
                WHERE email = %s;
            """,
            [new_hash, user.email],
        )

        self.commit()

    def get_sample(self, assay: str, tissue: str) -> Sample:
        """Gets a sample from the database.

        Arguments:
            assay (str): the assay to search for.
            tissue (str): the tissue to search for.

        Return:
            The unique sample with assay `assay` and tissue `tissue`.

        Raises:
            SampleNotFound: if no sample has `assay` and `tissue`.
        """

        # TODO: replace the * with the proper table column names
        sql = """
            SELECT *
            FROM samples
            WHERE assay = %s AND tissue = %s;
        """

        cursor = self.__connection.cursor(dictionary=True)
        cursor.execute(sql, [assay, tissue], multi=True)

        if (results := cursor.fetchone()) is None:
            raise SampleNotFound(assay, tissue)

        return Sample.model_validate(results)

    def delete_sample(self, assay: str, tissue: str):
        """Delete a sample from the database.

        Arguments:
            assay (str): the assay of the sample to look up.
            tissue (str): the tissue of the sample to look up.

        Raises:
            SampleNotFound: if no sample has `assay` and `tissue`.
        """

        cursor = self.__connection.cursor()
        cursor.execute(
            """
                DELETE FROM samples
                WHERE assay = %s AND tissue = %s;
            """,
            [assay, tissue],
        )

        self.commit()

    def insert_sample(self, sample: Sample):
        """Post a sample to the database.

        Arguments:
            sample (Sample): object containing this sample's information

        Raises:
            SampleNameCollision: if `sample.sample_name` is already in the database.
        """

        # Verify that the sample is not already in the database
        # NOTE: this might be possible using the database itself, since it may be possible to throw an error on
        # non-unique entries
        try:
            self.get_sample(sample.assay, sample.tissue)
            raise SampleNameCollision()
        except SampleNotFound:
            pass

        cursor = self.__connection.cursor()
        cursor.execute(
            """
                INSERT INTO samples (assay, tissue, area, assigned_transcripts, cell_count, cell_over25_count,
                    complexity, false_discovery_rate, median_counts, median_genes, reference_correlation, sparsity,
                    volume, x_transcript_count, y_transcript_count, transcripts_per_area, transcripts_per_feature)

                VALUES (%(assay)s, %(tissue)s, %(area)s, %(assigned_transcripts)s, %(cell_count)s,
                    %(cell_over25_count)s, %(complexity)s, %(false_discovery_rate)s, %(median_counts)s,
                    %(median_genes)s, %(reference_correlation)s, %(sparsity)s, %(volume)s, %(x_transcript_count)s,
                    %(y_transcript_count)s, %(transcripts_per_area)s, %(transcripts_per_feature)s);
            """,
            dict(sample)
        )

        self.commit()
