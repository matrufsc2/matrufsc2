from app.cache import gc_collect
from app.decorators.cacheable import cacheable
from app.decorators.searchable import searchable
from app.repositories import DisciplinesRepository

__author__ = 'fernando'


@searchable(
    lambda item: " - ".join([item['code'], item['name']]),
    prefix="matrufsc2-discipline-",
    consider_only=['campus']
)
def get_disciplines(filters):
    gc_collect() # Just to avoid too much use of memory
    repository = DisciplinesRepository()
    if filters:
        disciplines = repository.find_by(filters).get_result()
    else:
        disciplines = repository.find_all().get_result()
    gc_collect()  # Just to avoid too much use of memory
    return disciplines


@cacheable()
def get_discipline(id_value):
    repository = DisciplinesRepository()
    discipline = repository.find_by_id(id_value).get_result()
    return discipline