# -*- coding: utf-8 -*-
from cms.exceptions import AppAllreadyRegistered
from cms.utils.django_load import load, iterload_objects
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class ApphookPool(object):
    def __init__(self):
        self.apps = {}
        self.discovered = False
        self.block_register = False
        
    def discover_apps(self):
        if self.discovered:
            return
        #import all the modules
        if settings.CMS_APPHOOKS:
            self.block_register = True
            for cls in iterload_objects(settings.CMS_APPHOOKS):
                self.block_register = False
                self.register(cls)
                self.block_register = True
            self.block_register = False
        else:
            load('cms_app')
        self.discovered = True
        
    def clear(self):
        self.apps = {}
        self.discovered = False

    def register(self, app):
        if self.block_register:
            return
        from cms.app_base import CMSApp
        assert issubclass(app, CMSApp)
        if app.__name__ in self.apps.keys():
            raise AppAllreadyRegistered, "[%s] an cms app with this name is already registered" % app.__name__
        self.apps[app.__name__] = app
        
    def get_apphooks(self):
        self.discover_apps()
        hooks = []
        for app_name in self.apps.keys():
            app = self.apps[app_name]
            hooks.append((app_name, app.name))
        # Unfortunately, we loose the ordering since we now have a list of tuples. Let's reorder by app_name:
        hooks = sorted(hooks, key=lambda hook: hook[1])
        return hooks
    
    def get_apphook(self, app_name):
        self.discover_apps()
        try:
            return self.apps[app_name]
        except KeyError:
            # deprecated: return apphooks registered in db with urlconf name instead of apphook class name 
            for app in self.apps.values():
                if app_name in app.urls:
                    return app
        raise ImproperlyConfigured('No registered apphook `%s` found.' % app_name)

apphook_pool = ApphookPool()
