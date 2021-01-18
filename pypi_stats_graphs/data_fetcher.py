import json
import logging
import tempfile
from typing import Any, List, Optional

from google.cloud.bigquery import Client
from pydantic import BaseSettings, Field, SecretStr
from pypinfo.cli import FIELD_MAP
from pypinfo.core import build_query, create_config, parse_query_result

logger = logging.getLogger(__name__)


class PyPiDataFetcher(BaseSettings):
    __slots__ = ('_client',)
    service_account_json: SecretStr = Field(..., env='service_account_json')
    package: str
    limit: Optional[int] = 1000
    header_fields: Optional[List[str]] = [
        "country",
        "distro",
        "system",
        "date",
        "version",
        "installer",
        "cpu",
        "system-release",
        "pyversion"
    ]
    days: Optional[int] = 0
    all_installers: Optional[bool] = True
    timeout: Optional[int] = 120000

    def __init__(self, **values: Any):
        super().__init__(**values)

        project_name = json.loads(self.service_account_json.get_secret_value())['project_id']
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", prefix="google_cred") as tmp:
            tmp.write(self.service_account_json.get_secret_value())
            tmp.seek(0)

            object.__setattr__(
                self,
                '_client',
                Client.from_service_account_json(
                    tmp.name,
                    project=project_name
                )
            )

            tmp.close()

    def _build_query(self):
        parsed_fields = []
        for field in self.header_fields:
            parsed = FIELD_MAP.get(field)
            if parsed is None:
                raise ValueError(f'"{field}" is an unsupported field.')
            parsed_fields.append(parsed)

        return build_query(
            self.package,
            parsed_fields,
            limit=self.limit,
            days=str(self.days),
            pip=not self.all_installers,
        )

    def get_query_results(self):
        built_query = self._build_query()
        query_job = self._client.query(built_query, job_config=create_config())
        query_rows = query_job.result(timeout=self.timeout // 1000)
        rows = parse_query_result(query_job, query_rows)
        if len(rows) == 1 and not json:
            # Only headers returned
            logger.warning("No data returned, check project name")
            return None

        return rows
