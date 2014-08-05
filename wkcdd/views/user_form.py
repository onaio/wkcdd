import colander
from deform.widget import SelectWidget, CheckedPasswordWidget
from wkcdd.models.user import ADMIN_PERM, CPC_PERM


@colander.deferred
def user_role_widget(node, kw):
    return SelectWidget(
        values=[(CPC_PERM, CPC_PERM.upper()),
                (ADMIN_PERM, ADMIN_PERM.capitalize())])


class UserForm(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title="Username",
        validator=colander.Length(min=1, max=100))
    password = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=5),
        widget=CheckedPasswordWidget(size=20),
        description='Type your password and confirm it')
    active = colander.SchemaNode(
        colander.Boolean(),
        title="Active")
    group = colander.SchemaNode(
        colander.String(),
        title="Type",
        widget=user_role_widget)

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True

        if value['group'] not in [ADMIN_PERM, CPC_PERM]:
            valid = False
            exc['group'] = "Enter a valid user type"

        if not valid:
            raise exc
