import inventory 

class InventoryConfigMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(inventory.models.InventorySettings.objects.first().__dict__)
        return context