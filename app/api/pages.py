from app.support.prismic_api import prismic_link_resolver, prismic_html_serializer, get_prismic_form
from prismic import predicates

__author__ = 'fernando'

def format_page(doc):
    page = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_structured_text("page.title").get_title().text,
        "link": prismic_link_resolver(doc.as_link())
    }
    body = doc.get_structured_text("page.body")
    if body:
        page["body"] = body.as_html(prismic_link_resolver, prismic_html_serializer())
    return page


def get_pages(filters):
    form = get_prismic_form()
    page = filters.get("page", "1")
    if page.isdigit():
        page = int(page)
    else:
        page = 1
    page_size = filters.get("limit", "10")
    if page_size.isdigit():
        page_size = int(page_size)
    else:
        page_size = 1
    form.query(
            predicates.at('document.type', 'page')
        ).page(page).fetch(["page.permalink", "page.title"]).page_size(page_size)
    try:
        response = form.submit()
        results = map(format_page, response.documents)
        return {
            "results": results,
            "total_pages": response.total_pages,
            "page": page
        }
    except:
        return {
            "results": [],
            "total_pages": 0,
            "page": page
        }

def get_page(id_value):
    form = get_prismic_form()
    form.query(
            predicates.at('document.type', 'page'),
            predicates.at('document.id', id_value)
        ).page(1).page_size(1)
    try:
        response = form.submit()
        if response.documents:
            return format_page(response.documents[0])
    except:
        return None

