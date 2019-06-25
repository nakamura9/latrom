from django.core.paginator import Paginator
from django.views.generic.base import ContextMixin as CMixin
from formtools.wizard.views import SessionWizardView
from collections import OrderedDict
from django.http import HttpResponseRedirect



class MultiPageDocument(CMixin):
    '''This class enables long invoices and other lists of items to be rendered correctly over multiple pages.
    Makes use of django's built in pagination feature

    '''
    page_length = 10 #default value
    multi_page_queryset = None

    def get_multipage_queryset(self):
        '''Used to create the queryset'''
        pass
        

    @property
    def pages(self):
        '''Returns a list of pages'''
        pages = [self._paginator.get_page(page) \
                    for page in self._paginator.page_range]

        return pages

    @property
    def page_count(self):
        return self._paginator.num_pages

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.multi_page_queryset:
            self.multi_page_queryset = self.get_multipage_queryset()

        self._paginator = Paginator(self.multi_page_queryset, self.page_length)
        context['pages'] = self.pages
        return context


class MultiPagePDFDocument(CMixin):
    '''This class enables long invoices and other lists of items to be rendered correctly over multiple pages.
    Makes use of django's built in pagination feature

    '''
    page_length = 10 #default value
    multipage_queryset = None

    @property
    def pages(self):
        '''Returns a list of pages'''
        pages = [self._paginator.get_page(page) \
                    for page in self._paginator.page_range]

        return pages

    @property
    def page_count(self):
        return self._paginator.num_pages

    def get_multipage_queryset(self):
        if self.multipage_queryset: return self.multipage_queryset
        return None

        

class ConfigWizardBase(SessionWizardView):
    '''This class saves instances of each model after each step
    After all the forms are rendered, the application saves its config model'''
    config_class = None
    success_url = None

    def get_next_step(self, step=None):
        """
        Not called directly, overrides built in method that raises 
        a value error because of the condition dict
        """
        if step is None:
            step = self.steps.current
        
        form_list = self.get_form_list()
        keys = list(form_list.keys())
        
        if step in keys:
            key = keys.index(step) + 1
            if len(keys) > key:
                return keys[key]
        else:
            
            all_forms_keys = list(self.form_list.keys())
            
            if step == all_forms_keys[-1]:#last step
                return None
            next_key = all_forms_keys.index(step) + 1
            key_string = all_forms_keys[next_key]
            key_index = keys.index(key_string)

            return keys[key_index]
            #find where it originally was in the list

        return None

    def render_next_step(self, form, **kwargs):
        '''saves each instance of the form after rendering'''
        form.save()
        return super().render_next_step(form, **kwargs)

    def render_done(self, form, **kwargs):
        '''This method overrides form tools default to prevent revalitdation
        on forms that have already been saved.'''
        final_forms = OrderedDict()
        form.save()

        # walk through the form list and try to validate the data again.
        for form_key in self.get_form_list():
            form_obj = self.get_form(
                step=form_key,
                data=self.storage.get_step_data(form_key),
                files=self.storage.get_step_files(form_key)
            )
            
            final_forms[form_key] = form_obj
            done_response = self.done(final_forms.values(), 
                form_dict=final_forms, **kwargs)
            
            self.storage.reset()

            return done_response

    def done(self, form_list, **kwargs):
        config = self.config_class.objects.first()
        config.is_configured = True
        config.save()
        return HttpResponseRedirect(self.success_url)

