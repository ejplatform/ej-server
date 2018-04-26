
# remove when implement cache on __init__.py
DEFAULT_FRAGMENTS = []

def default_fragment(fragment_not_found):
    return {
            "content": f'''
            <h1>
                <strong>You didn't have a "{fragment_not_found}" fragment defined</strong>
                <p>Create a {fragment_not_found}.html</p>
                <p>Use the command loadfragments from manage.py to create new fragments or --force to update</p>
            </h1> 
            '''
    }