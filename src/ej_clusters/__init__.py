import sidekick as _sk

default_app_config = 'ej_clusters.apps.EjClustersConfig'

update_clusters = _sk.import_later('.factories:update_clusters', package=__package__)
set_clusters_from_comments = _sk.import_later('.factories:set_clusters_from_comments', package=__package__)
