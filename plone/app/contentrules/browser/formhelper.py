from Acquisition import aq_parent, aq_inner
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.interfaces import IContentRulesForm
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
from Products.Five.browser import BrowserView
from z3c.form import button
from z3c.form import form
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implements
import os
import zope.lifecycleevent


layout_factory = ZopeTwoFormTemplateFactory(
    os.path.join(os.path.dirname(__file__), 'templates', 'contentrules-pageform.pt'),
    form=IContentRulesForm,
    request=IPloneFormLayer)


class AddForm(AutoExtensibleForm, form.AddForm):
    """A base add form for content rule.

    Use this for rule elements that require configuration before being added to
    a rule. Element types that do not should use NullAddForm instead.

    Sub-classes should define create() and set the `schema` class attribute.

    Notice the suble difference between AddForm and NullAddform in that the
    create template method for AddForm takes as a parameter a dict 'data':

        def create(self, data):
            return MyAssignment(data.get('foo'))

    whereas the NullAddForm has no data parameter:

        def create(self):
            return MyAssignment()
    """

    implements(IContentRulesForm)

    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        focus = self.context.id.strip('+')
        return '%s/++rule++%s/@@manage-elements#%s' % (url, rule.__name__, focus)

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"), name='cancel')
    def handle_cancel_action(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    def add(self, ob):
        ob = self.context.add(ob)
        return ob


class NullAddForm(BrowserView):
    """An add view that will add its content immediately, without presenting
    a form.

    You should subclass this for rule elements that do not require any
    configuration before being added, and write a create() method that takes no
    parameters and returns the appropriate assignment instance.
    """

    def __call__(self):
        ob = self.create()
        notify(zope.lifecycleevent.ObjectCreatedEvent(ob))
        self.context.add(ob)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())

    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return '%s/++rule++%s/@@manage-elements' % (url, rule.__name__)

    def create(self):
        raise NotImplementedError("concrete classes must implement create()")


class EditForm(AutoExtensibleForm, form.EditForm):
    """An edit form for rule elements.
    """

    implements(IContentRulesForm)

    @button.buttonAndHandler(
        _(u"label_save", default=u"Save"),
        name=u'save')
    def handle_save_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(
        _(u"label_cancel", default=u"Cancel"),
        name=u'cancel')
    def handle_cancel_action(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())

    def nextURL(self):
        element = aq_inner(self.context)
        rule = aq_parent(element)
        context = aq_parent(rule)
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        focus = self.context.id.strip('+')
        return '%s/++rule++%s/@@manage-elements#%s' % (url, rule.__name__, focus)
