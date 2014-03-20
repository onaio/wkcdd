import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import (
    Column,
    Integer,
)
from wkcdd import constants
from wkcdd.models.base import (
    DBSession,
    Base
)
from wkcdd.models.project import (
    Project
)

from wkcdd.models.report import (
    Report
)


class BaseSubmissionHandler(object):
    def __init__(self, submission):
        self.submission = submission

    def handle_submission(self):  # pragma: no cover
        raise NotImplementedError("handle_submission is not implemented")


class ProjectRegistrationHandler(BaseSubmissionHandler):
    @classmethod
    def parse_data(cls, raw_data):
        """
        Return the project registration details from submission
        """
        return (raw_data.get(constants.PROJECT_CODE),
                raw_data.get(constants.COMMUNITY_NAME))

    def handle_submission(self):
        project_code, project_community = ProjectRegistrationHandler.parse_data(
            self.submission.raw_data)

        project = Project(
            project_code=project_code,
            name="Dairy Cows",
            community_id='{}',
            project_type_id=1
        )

        DBSession.add(project)


class ProjectReportHandler(BaseSubmissionHandler):
    @classmethod
    def parse_data(cls, raw_data):

        return (raw_data.get(constants.PROJECT_CODE),
                raw_data.get(constants.DATE_COMPILED),
                raw_data.get(constants.XFORM_ID),)

    def handle_submission(self):
        project_code, xform_id = \
            ProjectReportHandler.parse_data(self.submission.raw_data)

        # check if we have a valid project with submitted project_code
        try:
            project = Project.get(Project.project_code == project_code)
        except NoResultFound:
            raise ProjectNotFound
        else:
            report_submission = Report(
                project_id=project.project_code,
                report_date=self.submission,
                report_data=self.submission.raw_data,
                form_id=xform_id
            )
            DBSession.add(report_submission)


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    raw_data = Column(JSON, nullable=False)

    # tools to handler mapping
    HANDLER_TO_XFORMS_MAPPING = (
        (ProjectRegistrationHandler, [constants.DAIRY_COWS_PROJECT_REGISTRATION]),
        (ProjectReportHandler, [constants.DAIRY_COWS_PROJECT_REPORT]),
    )

    @classmethod
    def create_from_json(cls, payload):
        # TODO: check for and handle json.loads parse errors
        submission = Submission(raw_data=json.loads(payload))
        DBSession.add(submission)

        # TODO: handle duplicates within handlers, via uuid
        handler_class = determine_handler_class(
            submission, cls.HANDLER_TO_XFORMS_MAPPING)
        handler_class(submission).handle_submission()
        return submission


def determine_handler_class(submission, mapping):
    """
    Determine the handler to use to handle the submission
    """
    try:
        xform_id = submission.raw_data[constants.XFORM_ID]
    except KeyError:
        raise SubmissionHandlerError(
            "'{}' not found in json".format(constants.XFORM_ID))

    # for each item in mapping check if this id exists
    handlers = filter(lambda x: xform_id in x[1], mapping)

    if len(handlers) == 1:
        handler_class, xform_ids = handlers[0]
        return handler_class
    elif len(handlers) == 0:
        raise ZeroSubmissionHandlersError(
            "No handlers found for '{}'".format(xform_id))
    else:
        raise MultipleSubmissionHandlersError(
            "Multiple handlers found for '{}'".format(xform_id))


class SubmissionHandlerError(Exception):
    pass


class ZeroSubmissionHandlersError(SubmissionHandlerError):
    pass


class MultipleSubmissionHandlersError(SubmissionHandlerError):
    pass


class ProjectNotFound(SubmissionHandlerError):
    pass
