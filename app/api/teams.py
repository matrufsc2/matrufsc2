import json
import logging as _logging
from google.appengine.ext import ndb
from app.cache import gc_collect
from app.decorators.cacheable import cacheable
from app.decorators.searchable import searchable
from app.json_serializer import JSONEncoder
from app.repositories import DisciplinesRepository, TeamsRepository

__author__ = 'fernando'


logging = _logging.getLogger("matrufsc2_api")
logging.setLevel(_logging.WARN)

@searchable(
    lambda item: item['id'],
    prefix="matrufsc2-discipline-",
    min_word_length=40,
    consider_only=["campus"]
)
def get_disciplines_teams(filters):
    gc_collect() # Just to avoid too much use of memory
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
    gc_collect() # Just to avoid too much use of memory
    return new_disciplines




@searchable(lambda item: item["id"], prefix="matrufsc2-team-", consider_only=["campus"], min_word_length=40)
def get_all_teams(filters):
    if "campus" not in filters:
        return []
    gc_collect() # Just to avoid too much use of memory
    repository = TeamsRepository()
    results = []
    more = True
    page = 1
    logging.debug("Fetching list of teams based on teams of each discipline")
    while more:
        gc_collect() # Just to avoid too much use of memory
        disciplines_teams = get_disciplines_teams({
            "campus": filters["campus"],
            "q": "",
            "page": page,
            "limit": 50
        })
        teams = []
        for result in disciplines_teams["results"]:
            teams.extend(result["teams"])
        results.extend(repository.find_by({"key": teams}).get_result())
        more = disciplines_teams["more"]
        page += 1
        del disciplines_teams
        del teams
        gc_collect() # Just to avoid too much use of memory
    logging.debug("Fetched %d teams (found on %d pages of disciplines)..", len(results), page)
    gc_collect() # Just to avoid too much use of memory
    return results


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
        "campus": str(filters["campus"])
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
