from wkcdd.models.form import Form

from wkcdd.tests.test_base import TestBase


class TestForm(TestBase):
    def setUp(self):
        super(TestForm, self).setUp()
        self.json_data = '[{"_id": "1", "id_string": "xlsform"}]'

    def _create_form(self):
        count = Form.count()
        self._add_location_type()
        self._add_location()
        community = self._add_community()
        project_type = self._add_project_type()
        self._add_form_types()

        self.project = self._add_project(community_id=community.id,
                                         project_type_id=project_type.id)
        self._add_form()
        self.assertEqual(count + 1, Form.count())
        self.data = {}

    def test_save_form(self):
        self._create_form()

    def test_get_registration_form_id(self):
        form = Form.get_registration_form_id()
        self.assertIsNone(form)

        self._create_form()

        form = Form.get_registration_form_id()
        self.assertIsNotNone(form)
