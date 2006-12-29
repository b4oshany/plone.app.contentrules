from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.conditions.role import RoleCondition
from plone.app.contentrules.conditions.role import RoleEditForm

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, obj):
        self.object = obj

class TestRoleCondition(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testRegistered(self): 
        element = getUtility(IRuleCondition, name='plone.conditions.Role')
        self.assertEquals('plone.conditions.Role', element.addview)
        self.assertEquals('edit.html', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(None, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleCondition, name='plone.conditions.Role')
        storage = IRuleStorage(self.folder)
        storage[u'foo'] = Rule()
        rule = self.folder.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.folder.REQUEST), name='+')
        addview = getMultiAdapter((adding, self.folder.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'role_name' : 'Manager'})
        
        e = rule.elements[0].instance
        self.failUnless(isinstance(e, RoleCondition))
        self.assertEquals('Manager', e.role_name)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleCondition, name='plone.conditions.Role')
        e = RoleCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, RoleEditForm))

    def testExecute(self): 
        e = RoleCondition()
        e.role_name = 'Manager'        
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder)), IExecutable)
        self.assertEquals(True, ex())
        
        e.role_name = 'Reviewer'
        
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.portal)), IExecutable)
        self.assertEquals(False, ex())
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRoleCondition))
    return suite