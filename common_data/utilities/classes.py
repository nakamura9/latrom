from django.core.paginator import Paginator
from django.views.generic.base import ContextMixin as CMixin

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
        print(context)
        return context


    