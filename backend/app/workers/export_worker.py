"""Reserved export worker module.

Exports are currently generated synchronously because CSV/XLSX files are small in the first release.
This module is kept as the extension point for large asynchronous exports.
"""


def process_export_job(job_id: int) -> None:
    raise NotImplementedError(f"Export job queue is not enabled yet: {job_id}")

