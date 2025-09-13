from django.contrib.auth.mixins import AccessMixin


class DispatcherOnlyMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_dispatcher:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class GenerationOnlyMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_generation:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
