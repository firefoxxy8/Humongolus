from pymongo.connection import Connection
import logging
import humongolus as orm
import datetime
import humongolus.field as field
import humongolus.widget as widget
from tests.states import states

conn = Connection()
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("humongolus")

orm.settings(logger=logger, db_connection=conn)

class Car(orm.Document):
    _db = "test"
    _collection = "cars"
    owner = field.DynamicDocument()
    make = field.Char()
    model = field.Char()
    year = field.Date()
    silly_date = field.TimeStamp()

Car.__remove__()

class Address(orm.EmbeddedDocument):
    street = field.Char()
    street2 = field.Char()
    zip = field.Char()


class Location(orm.EmbeddedDocument):
    city = field.Char(required=True)
    state = field.Char()
    address = Address()

class Job(orm.EmbeddedDocument):
    employer = field.Char()
    title = field.Char(required=True)
    locations = orm.List(type=Location)


class Human(orm.Document):
    _db = "test"
    _collection = "humans"
    human_id = field.AutoIncrement(collection="human")
    name = field.Char(required=True, min=2, max=25)
    age = field.Integer(required=True, min=0, max=3000)
    height = field.Float(min=1, max=100000)
    weight = field.Float(min=1, max=30000)
    jobs = orm.List(type=Job)
    genitalia = field.Char()
    location = Location()
    car = field.ModelChoice(type=Car)
    color = field.Choice(choices=[{'value':'red', 'display':'Red'},{'value':'blue', 'display':'Blue'},{'value':'green', 'display':'Green'}])
    state = field.CollectionChoice(db='test', collection='states', sort=[('fullname',1)])
    email = field.Email()

Human.__remove__()

class Female(Human):
    genitalia = field.Char(default='inny')

class Male(Human):
    genitalia = field.Char(default='outy')
    
class CarDisplay(orm.Widget):
    #ideally you're using some sort of templating engine, I prefer Mako.
    def render(self, *args, **kwargs):
        return """
                <ul class='%s'>
                    <li>Make: %s</li>
                    <li>Model: %s</li>
                    <li>Year: %s</li>
                </ul>
        """ % (kwargs.get("cls", ""), self._object.make, self._object.model, self._object.year)

Human.cars = orm.Lazy(type=Car, key='owner._id')

chris = Male()
chris.name = "Chris"
chris.age = 31
chris.height = 100
chris.weight = 180
chris.location.city = "Chicago"
chris.location.state = "IL"
chris.location.address.zip = 60626

job = Job()
job.employer = "Entropealabs"
job.title = "President"

loc = Location()
loc.city = "Chicago"
loc.state = "IL"

job.locations.append(loc)
chris.jobs.append(job)

print chris.name
print chris.location.city
print chris.location.address.zip
print chris.jobs[0].title
print chris.jobs[0].locations[0].state


print chris.json()

_id = chris.save()

print _id

car = Car()
car.owner = chris
car.make = "Isuzu"
car.model = "Rodeo"
car.year = datetime.datetime(1998, 1, 1)
print car
c_id = car.save()

car2 = Car()
car2.owner = chris
car2.make = "Mercedes"
car2.model = "Baby C"
car2.year = datetime.datetime(1965, 1, 1)
print car2
c_id = car2.save()

print car.owner.name

c = Male(id=_id)
print c.json()