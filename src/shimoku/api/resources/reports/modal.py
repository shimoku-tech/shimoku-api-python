from ..report import Report

import asyncio
import logging

logger = logging.getLogger(__name__)


class Modal(Report):
    """Modal report class"""

    report_type = "MODAL"

    default_properties = dict(
        **Report.default_properties,
        open=False,
        reportIds=[],
        width=60,
        height=50,
    )

    def __init__(self, *args, **kwargs):
        self.dirty = False
        super().__init__(*args, **kwargs)

    async def update(self, *args, **kwargs) -> bool:
        """Update the modal on the server
        :return: True if the modal was updated, False otherwise
        """
        if not self.dirty:
            return False
        self.dirty = False
        await super().update()
        return True

    async def delete(self):
        """Delete the modal from the server and all its children"""
        await asyncio.gather(
            *[
                self._base_resource.parent.delete_report(rd_id)
                for rd_id in self["properties"]["reportIds"]
            ]
        )
        await super().delete()

    def add_report(self, report: Report):
        """Add report to the modal without saving it to the server
        :param report: report to add
        """
        if report["id"] in self["properties"]["reportIds"]:
            logger.warning(f"Report {report['id']} already in modal")
            return

        self["properties"]["reportIds"].append(report["id"])
        self.dirty = True

    def remove_report(self, report: Report):
        """Remove report from the modal without saving it to the server
        :param report: report to remove
        """

        if report["id"] not in self["properties"]["reportIds"]:
            logger.warning(f"Report {report['id']} not in modal")
            return

        self["properties"]["reportIds"].remove(report["id"])
        self.dirty = True

    def has_report(self, report: Report):
        """Check if report is in the modal
        :param report: report to check
        """
        return report["id"] in self["properties"]["reportIds"]

    def clear_content(self):
        """Remove all reports from the tabs group without saving it to the server"""
        self["properties"]["reportIds"] = []
        self.dirty = True
