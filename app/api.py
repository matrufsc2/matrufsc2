import json
import logging as _logging
import datetime, calendar
from urllib import urlencode
import urllib
from google.appengine.api import app_identity
import unidecode
from app.cache import get_from_cache, set_into_cache
import pytz
from feedgen.feed import FeedGenerator
from google.appengine.ext import ndb
import math
from app.json_serializer import JSONEncoder
from app.repositories import CampusRepository, DisciplinesRepository, TeamsRepository, SemesterRepository, \
    PlansRepository
from app.decorators import cacheable, searchable
from app.models import Plan
from app import cache
import operator
import prismic
import rollbar
from flask import request
from prismic import predicates, fragments
from lxml import html
from lxml.html.clean import Cleaner

__author__ = 'fernando'

logging = _logging.getLogger("matrufsc2_api")
logging.setLevel(_logging.WARN)
# mapping with LAT/LONG for some of the cities
CAMPI_LAT_LON = {
    "CBS": [-27.282778, -50.583889],
    "ARA": [-28.935, -49.485833],
    "BLN": [-26.908889, -49.072222],
    "FLO": [-27.596944, -48.548889],
    "JOI": [-26.303889, -48.845833]
}


def prismic_custom_request_handler(url):
    resp = ndb.get_context().urlfetch(url).get_result()
    return resp.status_code, resp.content, resp.headers


def prismic_link_resolver(doc):
    fmt = None
    if doc.type == "page":
        fmt = "/%s/%s/"
    elif doc.type == "question-group":
        fmt = "/ajuda/perguntas-frequentes/%s/%s/"
    elif doc.type == "post":
        fmt = "/blog/post/%s/%s/"
    elif doc.type == "category":
        fmt = "/blog/categoria/%s/%s/"
    elif doc.type == "section":
        fmt = "/ajuda/secao/%s/%s/"
    elif doc.type == "article":
        fmt = "/ajuda/artigo/%s/%s/"
    elif doc.type == "author":
        fmt = "/blog/autor/%s/%s/"
    if fmt is None:
        rollbar.report_message("Found link with unrecognized document type '%s'!" % doc.type, request=request)
        return "javascript:alert('Tipo de link nao reconhecido! Tente novamente mais tarde');"
    else:
        return fmt % (doc.slug, doc.id)

def prismic_full_link_resolver(doc):
    return "".join(["http://", get_domain(), prismic_link_resolver(doc)])

def prismic_html_serializer(block, content):
    return None


def distance_on_unit_sphere(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


def get_domain():
    domain = get_from_cache("matrufsc2_domain").get_result()
    if not domain:
        domain = app_identity.get_default_version_hostname()
        set_into_cache("matrufsc2_domain", domain).get_result()
    return domain


def get_campi_key(campus, lat, lon):
    campus_lat_lon = CAMPI_LAT_LON.get(campus.name, [0, 0])
    return distance_on_unit_sphere(lat, lon, campus_lat_lon[0], campus_lat_lon[1])


def sort_campi_by_distance(filters):
    campi = filters["campi"]
    lat = filters["lat"]
    lon = filters["lon"]
    return map(
        operator.itemgetter(1),
        sorted(
            zip(
                map(
                    get_campi_key,
                    campi,
                    (lat for _ in campi),
                    (lon for _ in campi),
                ),
                campi
            ),
            key=operator.itemgetter(0)
        )
    )


@cacheable(consider_only=[])
def get_semesters(filters):
    repository = SemesterRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


@cacheable()
def get_semester(id_value):
    repository = SemesterRepository()
    return repository.find_by_id(id_value).get_result()


@cacheable(consider_only=["semester", "_full"])
def get_campi(filters):
    repository = CampusRepository()
    full = filters.pop("_full", None)
    if filters:
        campi = repository.find_by(filters).get_result()
    else:
        campi = repository.find_all().get_result()
    if not full:
        # Avoid descompression of big data when caching
        for campus in campi:
            campus.disciplines = []
    return campi


@cacheable()
def get_campus(id_value):
    repository = CampusRepository()
    campus = repository.find_by_id(id_value).get_result()
    if campus:
        campus.disciplines = []
    return campus


@searchable(
    lambda item: " - ".join([item['code'], item['name']]),
    prefix="matrufsc2-discipline-",
    consider_only=['campus']
)
def get_disciplines(filters):
    repository = DisciplinesRepository()
    if filters:
        disciplines = repository.find_by(filters).get_result()
    else:
        disciplines = repository.find_all().get_result()
    return disciplines


@searchable(
    lambda item: item['id'],
    prefix="matrufsc2-discipline-",
    min_word_length=40,
    consider_only=["campus"]
)
def get_disciplines_teams(filters):
    new_disciplines = []
    repository = DisciplinesRepository()
    disciplines = repository.find_by(filters).get_result()
    for discipline_model in disciplines:
        discipline = json.loads(json.dumps(discipline_model, cls=JSONEncoder))
        new_disciplines.append({
            "id": discipline["id"],
            "teams": map(ndb.Key.id, discipline_model.teams)
        })
    logging.debug("Return %d disciplines to the indexing", len(new_disciplines))
    return new_disciplines


@cacheable()
def get_discipline(id_value):
    repository = DisciplinesRepository()
    discipline = repository.find_by_id(id_value).get_result()
    return discipline


@searchable(lambda item: item["id"], prefix="matrufsc2-team-", consider_only=["campus"], min_word_length=40)
def get_all_teams(filters):
    if "campus" not in filters:
        return []
    repository = TeamsRepository()
    teams = []
    more = True
    page = 1
    logging.debug("Fetching list of teams based on teams of each discipline")
    while more:
        disciplines_teams = get_disciplines_teams({
            "campus": filters["campus"],
            "q": "",
            "page": page,
            "limit": 50,
            "log": False
        })
        for result in disciplines_teams["results"]:
            teams.extend(result["teams"])
        more = disciplines_teams["more"]
        page += 1
    logging.debug("Fetching %d teams (found on %d pages of disciplines)..", len(teams), page)
    result = list(repository.find_by({"key": teams}).get_result())
    logging.debug("%d Teams fetched!", len(result))
    return result


def get_teams(filters):
    """
    Return a list of dict that matches the discipline filter =)
    :param filters: A dict (containing only discipline field)
    :return:
    """
    if "discipline" not in filters or "campus" not in filters:
        return []
    logging.debug("Fetching discipline '%s' (of the campus '%s') to get the teams..", filters["discipline"],
                  filters["campus"])
    disciplines = get_disciplines_teams({
        "q": str(filters["discipline"]).replace("matrufsc2-discipline-", ""),
        "campus": filters["campus"]
    })
    teams = []
    if not disciplines["results"]:
        return teams
    if disciplines["results"][1:]:
        raise Exception("Something strange found")
    for team_key in disciplines["results"][0]["teams"]:
        search_query = str(team_key).replace("matrufsc2-team-", "")
        logging.debug("Fetching team '%s'..", team_key)
        result = get_all_teams({"q": search_query, "campus": filters["campus"]})
        if len(result["results"]) > 1:
            raise Exception("Number of teams unexpected found for team key '%s'"%search_query)
        elif not result["results"]:
            logging.error("No team found for team key '%s'"%search_query)
        if result["results"]:
            r = dict(result["results"][0])
            r["id"] = "".join(["matrufsc2-team-", r["id"]])
            teams.append(r)
    return teams


@cacheable()
def get_team(id_value):
    repository = TeamsRepository()
    return repository.find_by_id(id_value).get_result()


def get_plan(plan_id):
    repository = PlansRepository()
    return repository.find_by_id(plan_id).get_result()


def get_plans(data):
    if "code" not in data:
        return []
    code = Plan.generate_id_string(data["code"])
    result = []
    match = get_plan(code)
    if match:
        result.append(match)
    return result


@ndb.transactional
def create_plan(data):
    if "code" not in data or "data" not in data:
        return False
    code = data["code"]
    plan_id = Plan.generate_id_string(code)
    if get_plan(plan_id): # Check in cache AND in database
        return False
    model = Plan(
        key=ndb.Key(Plan, plan_id),
        code=code,
        history=[{
            "id": calendar.timegm(datetime.datetime.now().utctimetuple()),
            "data": data["data"]
        }]
    )
    model.put()
    return model


@ndb.transactional
def update_plan(plan_id, data):
    if "code" not in data or "data" not in data:
        return False
    plan_id_test = Plan.generate_id_string(data["code"])
    if plan_id_test != plan_id:
        return False
    model = get_plan(plan_id) # Get from cache if available
    # Get the UTC timestamp
    now = calendar.timegm(datetime.datetime.now().utctimetuple())
    # Identify possible duplicates:
    while True:
        found = False
        for item in model.history:
            if item["id"] == now:
                now += 1
                found = True
        if not found:
            break
    model.history.insert(0, {
        "id": now,
        "data": data["data"]
    })
    # Hard limit to history: 10 itens
    if len(model.history) > 10:
        model.history.pop()
    model.put()
    # Update cache too
    return model


def get_prismic_api():
    return prismic.get(
        "http://matrufsc2.cdn.prismic.io/api",
        None,
        cache,
        prismic_custom_request_handler
    )


def get_prismic_form(ref=None, form="everything"):
    prismic_api = get_prismic_api()
    if ref is None:
        if "io.prismic.preview" in request.cookies:
            ref = request.cookies["io.prismic.preview"]
        else:
            ref = prismic_api.get_ref("master")
    form = prismic_api.form(form)
    form.ref(ref)
    return form


def format_page(doc):
    page = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_structured_text("page.title").get_title().text,
        "link": prismic_link_resolver(doc.as_link())
    }
    body = doc.get_structured_text("page.body")
    if body:
        page["body"] = body.as_html(prismic_link_resolver, prismic_html_serializer)
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
        preds.append(predicates.at('my.post.categories.category', filters["category"]))
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


def format_question_group(doc):
    """
    Format a question group

    :param doc: The document of the question group
    :type doc: prismic.Document
    :return: The dict of the question group
    """
    question_group = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_text("question-group.title"),
        "description": doc.get_structured_text("question-group.description").as_html(prismic_link_resolver, prismic_html_serializer),
        "link": prismic_link_resolver(doc.as_link())
    }
    questions = doc.get_group("question-group.questao")
    if questions:
        question_group["questions"] = [{
            "question": question.get_text("question"),
            "answer": question.get_structured_text("answer").as_html(prismic_link_resolver, prismic_html_serializer)
        } for question in questions.value]
    return question_group


def get_questions_groups(filters):
    form = get_prismic_form()
    preds = []
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
    preds.append(predicates.at('document.type', 'question-group'))
    q = filters.get("q")
    if q:
        preds.append(predicates.fulltext('document', unidecode.unidecode(q)))
    form.query(*preds).fetch(["question-group.title","question-group.description"]).page(page).page_size(page_size)
    try:
        response = form.submit()
        results = map(format_question_group, response.documents)
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


def get_question_group(id_value):
    form = get_prismic_form()
    form.query(
            predicates.at('document.type', 'question-group'),
            predicates.at('document.id', id_value)
        ).page(1).page_size(1)
    try:
        response = form.submit()
        if response.documents:
            return format_question_group(response.documents[0])
    except:
        return None


def format_section(doc):
    category = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_text("section.name"),
        "link": prismic_link_resolver(doc.as_link())
    }
    description = doc.get_structured_text("section.description")
    if description:
        category["description"] = description.as_html(prismic_link_resolver, prismic_html_serializer)
    return category


def get_sections(filters):
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
            predicates.at('document.type', 'section')
        ).page(page).page_size(page_size)
    try:
        response = form.submit()
        results = map(format_section, response.documents)
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


def get_section(id_value, description=True):
    form = get_prismic_form()
    form.query(
            predicates.at('document.type', 'section'),
            predicates.at('document.id', id_value)
        ).page(1).page_size(1).fetch(['section.name', 'section.description'] if description else ['section.name'])
    try:
        response = form.submit()
        if response.documents:
            return format_section(response.documents[0])
    except:
        return None


def format_article(doc):
    article = {
        "id": doc.id,
        "slug": doc.slug,
        "title": doc.get_text("article.title"),
        "link": prismic_link_resolver(doc.as_link())
    }
    summary = doc.get_structured_text("article.summary")
    if summary:
        article["summary"] = summary.as_html(prismic_link_resolver, prismic_html_serializer)
    content = doc.get_structured_text("article.content")
    if content:
        article["body"] = content.as_html(prismic_link_resolver, prismic_html_serializer)
    section = doc.get_link("article.section")
    if section:
        article["section"] = get_section(section.id, False)
    return article


def get_articles(filters):
    form = get_prismic_form()
    preds = []
    preds.append(predicates.at('document.type', 'article'))
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
    if "section" in filters:
        preds.append(predicates.at('my.article.section', filters["section"]))
    q = filters.get("q")
    if q:
        preds.append(predicates.fulltext('document', q))
    form.query(*preds).page(page).fetch(["article.title", "article.summary"]).page_size(page_size)
    try:
        response = form.submit()
        results = map(format_article, response.documents)
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


def get_article(id_value):
    form = get_prismic_form()
    form.query(
            predicates.at('document.type', 'article'),
            predicates.at('document.id', id_value)
        ).page(1).page_size(1)
    try:
        response = form.submit()
        if response.documents:
            return format_article(response.documents[0])
    except:
        return None