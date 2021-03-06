# Copyright 2015 FUJITSU LIMITED
# (C) Copyright 2016 Hewlett Packard Enterprise Development Company LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

import logging
import psycopg2

from monasca_notification.common.repositories.base.base_repo import BaseRepo
from monasca_notification.common.repositories import exceptions as exc

log = logging.getLogger(__name__)


class PostgresqlRepo(BaseRepo):
    def __init__(self, config):
        super(PostgresqlRepo, self).__init__(config)
        self._pgsql_params = config['postgresql']
        self._pgsql = None

    def _connect_to_pgsql(self):
        self._pgsql = None
        try:
            self._pgsql = psycopg2.connect(**self._pgsql_params)
            self._pgsql.autocommit = True
        except psycopg2.Error as e:
            log.exception('Pgsql connect failed %s', e)
            raise

    def fetch_notification(self, alarm):
        try:
            if self._pgsql is None:
                self._connect_to_pgsql()
            cur = self._pgsql.cursor()
            cur.execute(self._find_alarm_action_sql, (alarm['alarmDefinitionId'], alarm['newState']))
            for row in cur:
                yield (row[1].lower(), row[0], row[2], row[3])
        except psycopg2.Error as e:
            log.exception("Couldn't fetch alarms actions %s", e)
            raise exc.DatabaseException(e)

    def get_alarm_current_state(self, alarm_id):
        try:
            if self._pgsql is None:
                self._connect_to_pgsql()
            cur = self._pgsql.cursor()
            cur.execute(self._find_alarm_state_sql, alarm_id)
            row = cur.fetchone()
            state = row[0] if row is not None else None
            return state
        except psycopg2.Error as e:
            log.exception("Couldn't fetch current alarm state %s", e)
            raise exc.DatabaseException(e)
