from . import kmeans


def get_clusters(votes, n_clusters_range=[2]):
    """
    Receives vote stream input that should be a list with the following format
    [('choice', 'user_id', 'comment_id'), ...] and a list of possible numbers
    of clusters. The algorithm will try to arrange users into a best fit number
    of clusters according to the max silhouette method.
    Returns a dict with users clustering information.
    Example:
        {'1': {'x': 12.5, 'y': 1.3, group: 1.0},
         '2': {'x': 1.5, 'y': 17.3, group: 2.0},
         '3': {'x': 12.3, 'y': 1.2, group: 1.0}}
    """
    return kmeans.make_clusters(votes, n_clusters_range)
