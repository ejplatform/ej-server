from collections.abc import MutableMapping

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from sidekick import import_later

pd = import_later("pandas")


#
# Managers and QuerySet classes
#
class DataFrameQuerySet(models.QuerySet):
    def as_dataframe(self):
        """
        Return queryset as the default dataframe.
        """
        columns = getattr(self, "DATAFRAME_COLUMNS", None)
        if columns is None:
            columns = getattr(self.model, "DATAFRAME_COLUMNS", None)
        if columns is None:
            raise ImproperlyConfigured(
                "DATAFRAME_COLUMNS must be defined either on the model or on the "
                "queryset class"
            )
        columns = normalize_columns(columns)
        return self.values_list(**dict(zip(*columns)))

    def values_dataframe(self, *args, **kwargs):
        """
        Return a dataframe using the specified columns.

        It can be called with a list of argument names,

            qs.values_dataframe('name', 'age')

        a list of values,

            qs.values_dataframe(['name', 'age'])

        or even key, value pairs

            qs.values_dataframe(profile__age='age', name='name')

        The last function signature is used when the query fields must be
        mapped into different column names in the dataframe.
        """
        if not kwargs and len(args) == 1:
            value = args[0]
            if not isinstance(value, str):
                if isinstance(value, MutableMapping):
                    args = ()
                    kwargs = value
                else:
                    args = tuple(value)

        columns = list(zip(args, args)) + list(kwargs.items())
        names, values = normalize_columns(columns)
        qs = self.values_list("id", *names)
        df = pd.DataFrame(list(qs), columns=["id", *values])
        df.index = df.pop("id")
        return df


#
# Utility functions
#
def normalize_columns(columns):
    """
    Return a tuple with (db column names, dataframe column names)
    """
    if isinstance(columns, MutableMapping):
        return list(columns.keys()), list(columns.values())
    return (list(columns),) * 2
