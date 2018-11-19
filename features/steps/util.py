

def find_by_css(context, query):
    element = context.browser.find_by_css(query)
    print (element)
    assert element
