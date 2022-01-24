from pprint import pprint

from elasticsearch import Elasticsearch

es = Elasticsearch([{"host": "localhost", "port": 9200}])

data = [
    {
        "balance": "$2,410.62",
        "age": 40,
        "name": "Bettie Buckner",
        "gender": "female",
        "company": "RODEOMAD",
        "email": "bettiebuckner@rodeomad.com",
        "phone": "+1 (857) 491-2461",
    },
    {
        "balance": "$1,143.56",
        "age": 28,
        "name": "Hanson Gates",
        "gender": "male",
        "company": "PEARLESSA",
        "email": "hansongates@pearlessa.com",
        "phone": "+1 (825) 524-3896",
    },
    {
        "balance": "$2,542.95",
        "age": 20,
        "name": "Audra Marshall",
        "gender": "female",
        "company": "COMTRAIL",
        "email": "audramarshall@comtrail.com",
        "phone": "+1 (920) 569-2780",
    },
    {
        "balance": "$2,235.86",
        "age": 34,
        "name": "Milagros Conrad",
        "gender": "female",
        "company": "IDEGO",
        "email": "milagrosconrad@idego.com",
        "phone": "+1 (823) 451-2064",
    },
    {
        "balance": "$2,606.95",
        "age": 34,
        "name": "Maureen Lopez",
        "gender": "female",
        "company": "EVENTEX",
        "email": "maureenlopez@eventex.com",
        "phone": "+1 (913) 425-3716",
    },
]

for a_data in data:
    res = es.index(index="my-index", body=a_data)
    pprint(res)


body = {
    "query": {
        "bool": {
            "must": [{"match": {"gender": "male"}}, {"range": {"age": {"gte": 25}}}]
        }
    }
}
res = es.search(index="my-index", body=body)
pprint(res)


# query = Q('match', gender='male') & Q('range', age={'gte': 25})
# s = Search(using=es, index='my-index').query(query)
# response = s.execute()
# for hit in response:
#     pprint(hit.name)
