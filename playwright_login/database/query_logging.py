import logging


logger = logging.getLogger("database.queries")


def execute_logged(connection, query: str, parameters: tuple | None = None):
    logger.info("SQL query:\n%s", query.strip())
    if parameters is None:
        return connection.execute(query)
    return connection.execute(query, parameters)