# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

from socorro.external.postgresql.base import PostgreSQLBase
from socorro.lib import datetimeutil

logger = logging.getLogger("webapi")


class CrontabberState(PostgreSQLBase):
    """Implement the /crontabber_state service with PostgreSQL. """

    def get(self, **kwargs):
        """Return the current state of all Crontabber jobs"""

        sql = """
        /* socorro.external.postgresql.crontabber_state.CrontabberState.get */
            SELECT
                app_name,
                next_run,
                first_run,
                last_run,
                last_success,
                error_count,
                depends_on,
                last_error,
                ongoing
            FROM crontabber
            ORDER BY app_name
        """

        error_message = (
            "Failed to retrieve crontabber state data from PostgreSQL"
        )
        results = self.query(sql, error_message=error_message)
        state = {}
        for row in results.zipped():
            app_name = row.pop('app_name')
            state[app_name] = row
            possible_datetimes = (
                'next_run',
                'first_run',
                'last_run',
                'last_success',
                'ongoing'
            )
            for key in possible_datetimes:
                value = state[app_name][key]
                if value is None:
                    continue
                state[app_name][key] = datetimeutil.date_to_string(value)

        return {"state": state}
