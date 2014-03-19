import transaction

from wkcdd.models.base import DBSession
from wkcdd.models.project import Project
from wkcdd.models.form import Form

from wkcdd.tests.test_base import TestBase


class TestForm(TestBase):
    def setUp(self):
        super(TestForm, self).setUp()
        self.setup_test_data()
        self.project = Project.get(Project.project_code == 'YH9T')
        self.json_data = '[{"_id": "1", "id_string": "xlsform"}]'

    def test_save_form(self):
        count = Form.count()
        form = Form(
            form_id='xlsform',
            form_name='xlsform',
            project_type_id=self.project.project_type_id,
            form_type_id=1,
            form_data=self.json_data)
        with transaction.manager:
            DBSession.add_all([form])
        self.assertEqual(count + 1, Form.count())
