from math import floor, ceil
from django.template.defaulttags import register
from django.http import HttpResponse
from django.shortcuts import render
import numpy as np
from main import parse_query, SECOND_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_SECOND_DATASET, file_content, \
    THIRD_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_THIRD_DATASET, ONLINE_INDEX, NUMBER_OF_DOCS, URL_MAP

RESULTS_PER_PAGE = 7
TITLE = 'title'
PUBLISH_DATE = 'publish_date'
URL = 'url'
THUMBNAIL = 'thumbnail'
ID = 'id'
CONTENT = 'content'


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def prepare_results(docs_ids):
    results = []
    for doc_id in docs_ids:  # todo check index
        if doc_id < NUMBER_OF_DOCS:
            row = file_content.iloc[doc_id]
            title = row[TITLE]
            # publish_date = row[PUBLISH_DATE] todo
            publish_date = ''
            url = "http://" + row[URL]
            thumbnail = row[THUMBNAIL]
            results.append({TITLE: title, PUBLISH_DATE: publish_date, URL: url, THUMBNAIL: thumbnail, ID: doc_id})
        else:
            url = URL_MAP[doc_id]
            results.append({'crawled_url': url, ID: doc_id})

    return results


def search_view(request, page):
    if request.method == 'GET':
        return render(request, template_name='index.html')
    elif request.method == 'POST':
        query = request.POST['query']

        docs = parse_query(query, 100, THIRD_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_THIRD_DATASET, 'THIRD',
                           weighting_scheme=3)

        # todo
        results = prepare_results(docs)
        results_length = len(results)
        has_next = False
        has_previous = False
        result_pages = ceil(results_length / RESULTS_PER_PAGE)
        if page < 1:
            page = 1
        if page >= result_pages:
            page = result_pages
        if page == 1:
            has_previous = False
            if result_pages == 1:
                has_next = False
            else:
                has_next = True
        elif page == result_pages:
            has_previous = True
            has_next = False
        else:
            has_previous = has_next = True

        context = {'results': results[(page - 1) * RESULTS_PER_PAGE: page * RESULTS_PER_PAGE],
                   'has_next': has_next, 'has_previous': has_previous, 'query': query, 'next_page': page + 1,
                   'previous_page': page - 1}
        request.session['query'] = query
        request.session['context'] = context
        print(results_length)
        return render(request, template_name='index.html', context=context)
    else:
        return HttpResponse('bad request method.')


def get_page_context(id, query_terms):
    row = file_content.iloc[id]
    content = row[CONTENT]

    for term in query_terms:
        content = content.replace(term, '<b>' + term + '</b>')

    return {'content': content}


tens = np.load('Python_Objects/all.npy')


def content_view(request, id):
    if request.method == 'GET':
        query = request.session.get('query')
        if query is None:
            return HttpResponse('bad request. (request without querying)')
        ten_top = []
        for x in tens[id]:
            row = file_content.iloc[int(x)]
            ten_top.append((int(x), row['title']))
        query = query.replace('!', '').replace('"', '')
        query_terms = query.split(' ')
        context = get_page_context(id, query_terms)
        context.update({'ten_top': ten_top})
        return render(request, template_name='content.html', context=context)
    else:
        return HttpResponse('bad request method.')
