import pyorient


client = pyorient.OrientDB("localhost", 2424)  # host, port

client.connect("root", "root")
client.db_create("animals", pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_MEMORY)
client.db_open("animals", "admin", "admin")

# Create the Vertex Animal
client.command("create class Animal extends V")

# Insert a new value
client.command("insert into Animal set name = 'rat', species = 'rodent'")

# query the values
client.query("select * from Animal")

# Create the vertex and insert the food values
client.command("create class Food extends V")
client.command("insert into Food set name = 'pea', color = 'green'")

# Create the edge for the Eat action
client.command("create class Eat extends E")

# Lets the rat likes to eat pea
eat_edges = client.command(
    "create edge Eat from ("
    "select from Animal where name = 'rat'"
    ") to ("
    "select from Food where name = 'pea'"
    ")"
)

# Who eats the peas?
pea_eaters = client.command("select expand( in( Eat )) from Food where name = 'pea'")
for animal in pea_eaters:
    print(animal.name, animal.species)

# What each animal eats?
animal_foods = client.command("select expand( out( Eat )) from Animal")
for food in animal_foods:
    animal = client.query(
        "select name from ( select expand( in('Eat') ) from Food where name = 'pea' )"
    )[0]
    print(food.name, food.color, animal.name)
