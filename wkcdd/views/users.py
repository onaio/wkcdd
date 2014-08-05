from deform import Form, ValidationFailure, Button
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from wkcdd.models.user import User, UserFactory
from wkcdd.views.base import BaseClassViews
from wkcdd.views.helpers import check_post_csrf
from wkcdd.views.user_form import UserForm


@view_defaults(route_name='users', context=User, permission="authenticated")
class AdminView(BaseClassViews):

    @view_config(name='',
                 context=UserFactory,
                 renderer='admin_users_list.jinja2',
                 request_method='GET')
    def list(self):
        # display list of registered users for administration
        users = User.all()
        return {'users': users}

    @view_config(name='add',
                 context=UserFactory,
                 renderer='user_form.jinja2',
                 decorator=check_post_csrf)
    def add_user(self):
        form = Form(
            UserForm().bind(
                request=self.request),
            buttons=('Save', Button(name='cancel', type='button')))

        if self.request.method == "POST":
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                # add user
                user = User(**values)
                user.save()
                # redirect to user admin view
                return HTTPFound(
                    self.request.route_url('users', traverse=()))
        # return form

        return {'form': form}

    @view_config(name='edit',
                 context=User,
                 renderer='user_form.jinja2',
                 decorator=check_post_csrf)
    def edit(self):
        # update user to be either admin or inactive
        user = self.request.context
        form = Form(
            UserForm().bind(
                request=self.request,
                user=user),
            buttons=('Save', Button(name='cancel', type='button')),
            appstruct=user.appstruct)
        if self.request.method == 'POST':
            data = self.request.POST.items()
            try:
                values = form.validate(data)
            except ValidationFailure:
                self.request.session.flash(
                    u"Please fix the errors indicated below.", "error")
            else:
                user.update(
                    values['username'],
                    values['password'],
                    values['active'],
                    values['group'])
                self.request.session.flash(
                    "Your changes have been saved.", 'success')
                return HTTPFound(
                    self.request.route_url(
                        'users', traverse=(user.id, 'edit')))

        return {'form': form}
