from lxml.html.clean import Cleaner
from lxml import html
import pytz
from feedgen.feed import FeedGenerator
from app.support.domain import get_domain
from app.support.prismic_api import prismic_link_resolver, prismic_full_link_resolver, prismic_html_serializer, \
    get_prismic_form
from prismic import predicates, fragments
import unidecode
__author__ = 'fernando'

def format_category(doc):
    category = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_text("category.name"),
        "link": prismic_link_resolver(doc if isinstance(doc, fragments.Fragment.DocumentLink) else doc.as_link())
    }
    description = doc.get_structured_text("category.description")
    if description:
        category["description"] = description.as_html(prismic_link_resolver, prismic_html_serializer)
    return category


def get_categories(filters):
    form = get_prismic_form()
    page = filters.get("page", "1")
    if page.isdigit():
        page = int(page)
    else:
        page = 1
    page_size = filters.get("limit", "10")
    if page_size.isdigit():
        page_size = int(page_size)

    form.query(
            predicates.at('document.type', 'category')
        ).page(page).fetch(["category.name"]).page_size(page_size)
    try:
        response = form.submit()
        results = map(format_category, response.documents)
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


def get_category(id_value, description=True):
    form = get_prismic_form()
    form.query(
            predicates.at('document.type', 'category'),
            predicates.at('document.id', id_value)
        ).page(1).page_size(1).fetch(["category.name", "category.description"] if description else ["category.name"])
    try:
        response = form.submit()
        if response.documents:
            return format_category(response.documents[0])
    except:
        return None

def format_post(doc, full_link=False):
    post = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_text("post.title"),
        "posted_at": doc.get_date("post.posted_at").as_datetime,
        "link":prismic_link_resolver(doc.as_link()),
        "full_link": prismic_full_link_resolver(doc.as_link()),
        "allow_comments": doc.get_text('post.allow_comments') == "Sim"
    }
    summary = doc.get_structured_text("post.summary")
    if summary:
        if full_link:
            post["summary"] = summary.as_html(prismic_full_link_resolver, prismic_html_serializer)
        else:
            post["summary"] = summary.as_html(prismic_link_resolver, prismic_html_serializer)
    body = doc.get_structured_text("post.body")
    if body:
        if full_link:
            post["body"] = body.as_html(prismic_full_link_resolver, prismic_html_serializer)
        else:
            post["body"] = body.as_html(prismic_link_resolver, prismic_html_serializer)
    category = doc.get_link("post.category")
    if category:
        post["category"] = get_category(category.id, False)
    return post


def get_posts(filters, full=False):
    form = get_prismic_form()
    preds = []
    preds.append(predicates.at('document.type', 'post'))
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
    if "category" in filters:
        preds.append(predicates.at('my.post.category', filters["category"]))
    q = filters.get("q")
    if q:
        preds.append(predicates.fulltext('document', unidecode.unidecode(q)))
    similar = filters.get("similar")
    if similar:
        preds.append(predicates.similar(similar, 5))
    form.query(*preds).page(page).page_size(page_size).orderings('[my.post.posted_at desc]')
    if not full:
        form.fetch(["post.title", "post.summary", "post.posted_at"])
    try:
        response = form.submit()
        if full:
            results = map(format_post, response.documents, [True]*len(response.documents))
        else:
            results = map(format_post, response.documents)
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

def get_post(id_value):
    form = get_prismic_form()
    form.query(
            predicates.at('document.type', 'post'),
            predicates.at('document.id', id_value)
        ).page(1).page_size(1)
    try:
        response = form.submit()
        if response.documents:
            return format_post(response.documents[0])
    except:
        return None


def get_feed(atom=False):
    fg = FeedGenerator()
    domain = get_domain()
    items = get_posts({"limit": "10"}, full=True)["results"]
    fg.id("http://%s/"%domain)
    fg.title("Blog do MatrUFSC2")
    fg.description("Feed do blog do MatrUFSC2, onde noticias e novos recursos sao anunciados primeiro!")
    fg.language('pt-BR')
    fg.link({"href":"/blog/feed","rel":"self"})
    fg.updated(items[0]["posted_at"].replace(tzinfo=pytz.UTC))
    for item in items:
        entry = fg.add_entry()
        entry.title(item["title"])

        tree = html.fromstring(item["summary"])
        cleaner = Cleaner(allow_tags=[])
        tree = cleaner.clean_html(tree)

        text = tree.text_content()
        entry.description(text, True)
        entry.link({"href":item["link"],"rel":"self"})
        entry.content(item["body"])
        entry.published(item["posted_at"].replace(tzinfo=pytz.UTC))
        entry.updated(item["posted_at"].replace(tzinfo=pytz.UTC))
        entry.category({"label": item["category"]["title"], "term": item["category"]["slug"]})
        entry.id(item["id"])
    if atom:
        return fg.atom_str(pretty=True)
    else:
        return fg.rss_str(pretty=True)