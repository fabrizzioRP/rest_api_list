def get_paginated_list(results, url, start, limit):
    
    results = [result for result in results]

    #from pprint import pprint
    #pprint(results)

    start = int(start)
    limit = int(limit)
    count = len(results)
    
    if count < start or limit < 0:
        error = 'La paginación excedio la cantidad total de recursos.'
        return error, 404
    if limit < 0:
        error = 'El limite de resultados debe ser mayor a 0.'
        return error, 404
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    #print('OBJ')
    #pprint(obj)
    
    return obj
