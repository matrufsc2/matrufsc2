import unidecode
from prismic import predicates
from app.support.prismic_api import get_prismic_form, prismic_link_resolver, prismic_html_serializer

__author__ = 'fernando'


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