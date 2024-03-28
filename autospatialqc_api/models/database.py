from typing import List, Optional, Union

import argon2
import pymysql.cursors

from autospatialqc_api.models.errors import (InvalidCredentials, SampleNameCollision, SampleNotFound, UserCollision,
                                             UserNotFound)
from autospatialqc_api.models.sample import Sample
from autospatialqc_api.models.user import Permissions, User


class Database:
    """Abstraction for the main application database."""

    def __init__(self, host: str, database: str, username: str, password: str):
        """Initializes a new database object.

        Arguments:
            host (str): the database's host.
            database (str): the database to use.
            username (str): the SQL user's username.
            password (str): the SQL user's password.
        """

        self.__host = host
        self.__database = database
        self.__username = username
        self.__password = password

    def connection(self) -> pymysql.Connection:
        """Make a connection to the server.

        Returns:
            A `pymysql.Connection` object that connects to this database.
        """
        return pymysql.connect(
            host=self.__host,
            user=self.__username,
            password=self.__password,
            database=self.__database,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def get_user(self, email: str, password: Optional[str] = None) -> User:
        """Finds a User from the database.

        Arguments:
            email (str): the user's email.
            password (str | None): the user's password. If the resulting user does not need to be authenticated,
              this parameter should be set to None. Defaults to None

        Returns:
            A User object containing this user's data.

        Raises:
            InvalidCredentials: if the user is to be authenticated, but their password is incorrect.
            UserNotFound: if this email is not in the database.
        """

        with self.connection() as connection:
            with connection.cursor() as cursor:
                sql = f"""
                    SELECT internal_id, first_name, last_name {", password_hash" if password is not None else ""}
                    FROM users u WHERE email = %s
                """
                cursor.execute(sql, (email))

                if (results := cursor.fetchone()) is None:
                    raise UserNotFound(email)

        if password is not None and not argon2.PasswordHasher().verify(results["password_hash"], password):
            raise InvalidCredentials()

        return User(
            **results,
            id=results["internal_id"],
            email=email,
            permissions=self.get_permissions(email),
            authenticated=password is not None,
        )

    def get_permissions(self, email: str) -> Permissions:
        """Gets the permissions for a user.

        Arguments:
            email (str): the user's email.

        Returns:
            This user's permissions flag if the email is in the database, Permissions.NONE otherwise.
        """

        with self.connection() as connection:
            with connection.cursor() as cursor:
                sql = """
                    SELECT permission_name FROM users u
                    LEFT JOIN user_permissions up ON u.internal_id = up.user_id
                    LEFT JOIN permissions p ON p.id = up.permission_id
                    WHERE email = %s;
                """
                cursor.execute(sql, (email))
                return Permissions.from_str(*(dictionary["permission_name"] for dictionary in cursor.fetchall()))

    def change_password(self, email: str, new_password: Union[str, bytes]):
        """Change a user's password.

        Arguments:
            email (str): the email of the user whose password is to be changed.
            new_password (bytes): the password to add to the database. This password will be hashed before storage.
        """

        if isinstance(new_password, str):
            new_password = new_password.encode("utf-8")

        new_hash = argon2.hash_password(new_password)

        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE email = %s",
                    (new_hash, email),
                )

            connection.commit()

    def add_sample(self, sample: Sample):
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

        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO samples (assay, tissue, area, assigned_transcripts, cell_count, cell_over25_count,
                            complexity, false_discovery_rate, median_counts, median_genes, reference_correlation,
                            sparsity, volume, x_transcript_count, y_transcript_count, transcripts_per_area,
                            transcripts_per_feature)

                        VALUES (%(assay)s, %(tissue)s, %(area)s, %(assigned_transcripts)s, %(cell_count)s,
                            %(cell_over25_count)s, %(complexity)s, %(false_discovery_rate)s, %(median_counts)s,
                            %(median_genes)s, %(reference_correlation)s, %(sparsity)s, %(volume)s,
                            %(x_transcript_count)s, %(y_transcript_count)s, %(transcripts_per_area)s,
                            %(transcripts_per_feature)s);
                    """,
                    dict(sample),
                )

            connection.commit()

    def delete_sample(self, assay: str, tissue: str):
        """Delete a sample from the database.

        Arguments:
            assay (str): the assay of the sample to look up.
            tissue (str): the tissue of the sample to look up.

        Raises:
            SampleNotFound: if no sample has `assay` and `tissue`.
        """

        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM samples WHERE assay = %s AND tissue = %s",
                    (assay, tissue),
                )

            connection.commit()

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

        with self.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM samples WHERE assay = %s and tissue = %s",
                    (assay, tissue),
                )

                if (results := cursor.fetchone()) is None:
                    raise SampleNotFound(assay, tissue)

        return Sample.model_validate(results)

    def add_permissions(self, user: User, permissions: List[str]):
        """Add permissions to a user.

        Arguments:
            user (User): the user data for the user for whom the permissions are being applied.
            permissions (list[str]): a list of string identifiers for the permissions that need to be applied.

        Raises:
            UserNotFound: if the user is not in the database.
        """

        # TODO: make an exception for non-existant permission strings

        with self.connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    f"""
                        INSERT INTO user_permissions (user_id, permission_id)
                        SELECT users.internal_id, permissions.id FROM users, permissions WHERE users.email = %s
                        AND permissions.permission_name IN ({str(permissions)[1:-1]});
                    """,
                    (user.email),
                )

            connection.commit()

    def delete_permissions(self, user: User, permissions: List[str]):
        """Remove permissions from a user.

        Arguments:
            user (User): the user data for the user for whom the permissions are being applied.
            permissions (list[str]): a list of string identifiers for the permissions that need to be removed.

        Raises:
            UserNotFound: if the user is not in the database.
        """

        with self.connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    f"""
                        DELETE FROM user_permissions WHERE user_id = (SELECT internal_id FROM users WHERE email = %s)
                        AND permission_id IN ({str(permissions)[1:-1]});
                    """,
                    (user.email),
                )

            connection.commit()

    def add_user(self, email: str, password: str, permissions: List[str], first_name: str, last_name: str):
        """Adds a new user to the database.

        Arguments:
            email (str): the new user's email. Cannot already exist in the database.
            password (str): the new user's password. This will be hashed prior to storage.
            permissions (list[str]): a list of string names for the permissions. Invalid names will fail silently.
            first_name (str): the new user's first name.
            last_name (str): the new user's last name.

        Raises:
            UserCollision: if the new user's unique identifers are already in use for another user.
        """

        # TODO: should invalid permission names fail silently or cause an error?

        password_hash = argon2.PasswordHasher().hash(password)

        try:
            with self.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                            INSERT INTO users (email, password_hash, first_name, last_name)
                            VALUES (%s, %s, %s, %s);
                        """,
                        (email, password_hash, first_name, last_name),
                    )

                connection.commit()
        except pymysql.IntegrityError:
            raise UserCollision(email)

        user = self.get_user(email)

        if permissions:
            self.add_permissions(user, permissions)
