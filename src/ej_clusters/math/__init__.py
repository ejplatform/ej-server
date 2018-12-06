from sidekick import import_later as _import_later

from .data import *
from .pipeline import clusterization_pipeline

k_means = _import_later('.kmeans', package=__package__)
pipeline = _import_later('.pipeline', package=__package__)
