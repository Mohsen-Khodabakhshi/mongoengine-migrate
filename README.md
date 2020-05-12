# Mongoengine-migrate

Schema migrations for [Mongoengine](http://mongoengine.org/) ODM. Inspired by Django migrations system.

## How it works

Let's suppose that we already have the following Document declaration:

```python
from mongoengine import Document, fields
    
class Books(Document):
    name = fields.StringField()
    year = fields.StringField(max_length=4)
    isbn = fields.StringField()
```

Then we changed couple of things:

```
# Add Author Document
class Author(Document):
    name = fields.StringField(required=True)

class Books(Document):
    caption = fields.StringField(required=True)  # Make required and rename
    year = fields.fields.IntField()  # Change type to IntField
    # Removed field isbn
    author = fields.ReferenceField(Author)  # Add field
```

Such changes should be reflected in database during upgrading. To 
detect changes run the command:

```shell script
mongoengine-migrate -m myproject.db makemigrations
```

New migration file will be created:

```python
from mongoengine_migrate.actions import *
from mongoengine_migrate.fields import *


dependencies = [
    'my_migration'
]

forward = [
    CreateCollection('author'),
    CreateField('author', 'name', choices=None, db_field='name', default=None, max_length=None,
        min_length=None, null=False, primary_key=False, regex=None, required=True,
        sparse=False, type_key='StringField', unique=False, unique_with=None),
    RenameField('books', 'name', new_name='caption'),
    AlterField('books', 'caption', required=D(False, True, default=''), 
        db_field=D('name', 'caption')),
    AlterField('books', 'year', type_key=D('StringField', 'IntField'), regex=D(None, UNSET),
        min_length=D(None, UNSET), max_length=D(None, UNSET), min_value=D(UNSET, None), 
        max_value=D(UNSET, None)),
    DropField('books', 'isbn'),
    CreateField('books', 'author', choices=None, db_field='author', dbref=False, default=None,
        link_collection='author', null=False, primary_key=False, required=False, sparse=False,
        type_key='ReferenceField', unique=False, unique_with=None),
]
```

Now in order to migrate database to the last migration, just run the command:

```shell script
mongoengine-migrate -m myproject.db migrate
```

Or to migrate to the certain migration:

```shell script
mongoengine-migrate -m myproject.db migrate my_migration
```
...to be continued 

# Author

Igor Derkach, gosha753951@gmail.com