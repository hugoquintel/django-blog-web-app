from django.db import models


class QuerySetMixin(models.QuerySet):
    def filter_with_dict(self, filter_conditions):
        if isinstance(filter_conditions, dict):  # use dict
            return self.filter(**filter_conditions)
        else:  # use Q objects
            return self.filter(filter_conditions)
