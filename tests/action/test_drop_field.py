import itertools
from copy import deepcopy
from unittest.mock import patch

import jsonpath_rw
import pytest

from mongoengine_migrate.actions import DropField
from mongoengine_migrate.exceptions import SchemaError
from mongoengine_migrate.graph import MigrationPolicy
from mongoengine_migrate.schema import Schema


@pytest.fixture
def left_schema():
    return Schema({
        'Document1': Schema.Document({
            'field1': {'param11': 'schemavalue11', 'param12': 'schemavalue12'},
            'field2': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
        }, parameters={'collection': 'document1'}),
        '~EmbeddedDocument2': Schema.Document({
            'field1': {'param3': 'schemavalue3'},
            'field2': {'param4': 'schemavalue4'},
        })
    })


class TestDropFieldInDocument:
    def test_forward__should_drop_field(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        expect = dump_db()
        parser = jsonpath_rw.parse('schema1_doc1[*]')
        for rec in parser.find(expect):
            if 'doc1_str' in rec.value:
                del rec.value['doc1_str']

        action = DropField('Schema1Doc1', 'doc1_str')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_forward()

        assert expect == dump_db()

    def test_backward__if_default_is_not_set__should_do_nothing(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        dump = dump_db()

        action = DropField('Schema1Doc1', 'doc1_str')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_backward()

        assert dump == dump_db()

    def test_backward__if_required_and_default_is_set__should_create_field_and_set_a_value(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        default = 'test!'
        schema['Schema1Doc1']['test_field'] = {
            'unique_with': None,
            'null': False,
            'choices': None,
            'default': default,
            'sparse': False,
            'unique': False,
            'required': True,
            'db_field': 'test_field',
            'primary_key': False,
            'type_key': 'StringField',
            'max_length': None,
            'regex': None,
            'min_length': None
        }
        dump = dump_db()
        expect = deepcopy(dump)
        parser = jsonpath_rw.parse('schema1_doc1[*]')
        for rec in parser.find(expect):
            rec.value['test_field'] = default

        action = DropField('Schema1Doc1', 'test_field')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_backward()
        assert expect == dump_db()

    def test_backward__if_required_and_default_is_set_and_field_in_db__should_not_touch_field(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        default = 'test!'
        schema['Schema1Doc1']['test_field'] = {
            'unique_with': None,
            'null': False,
            'choices': None,
            'default': default,
            'sparse': False,
            'unique': False,
            'required': True,
            'db_field': 'test_field',
            'primary_key': False,
            'type_key': 'StringField',
            'max_length': None,
            'regex': None,
            'min_length': None
        }
        ids = set()
        for doc in test_db['schema1_doc1'].find({}, limit=2):
            test_db['schema1_doc1'].update_one({'_id': doc['_id']},
                                               {'$set': {'test_field': 'old_value'}})
            ids.add(doc['_id'])

        action = DropField('Schema1Doc1', 'test_field')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_backward()

        assert all(d['test_field'] == 'old_value'
                   for d in test_db['schema1_doc1'].find()
                   if d['_id'] in ids)

    def test_prepare__if_such_document_is_not_in_schema__should_raise_error(self,
                                                                            load_fixture,
                                                                            test_db):
        schema = load_fixture('schema1').get_schema()
        del schema['Schema1Doc1']

        action = DropField('Schema1Doc1', 'doc1_str')

        with pytest.raises(SchemaError):
            action.prepare(test_db, schema, MigrationPolicy.strict)

    def test_prepare__if_such_field_in_document_is_not_in_schema__should_raise_error(self,
                                                                                     load_fixture,
                                                                                     test_db):
        schema = load_fixture('schema1').get_schema()

        action = DropField('Schema1Doc1', 'unknown_field')

        with pytest.raises(SchemaError):
            action.prepare(test_db, schema, MigrationPolicy.strict)

    def test_build_object__if_field_creates__should_return_object(self, left_schema):
        right_schema = Schema({
            'Document1': Schema.Document({
                'field1': {'param11': 'schemavalue11', 'param12': 'schemavalue12'},
            }, parameters={'collection': 'document1'}),
            '~EmbeddedDocument2': Schema.Document({
                'field1': {'param3': 'schemavalue3'},
                'field2': {'param4': 'schemavalue4'},
            })
        })

        res = DropField.build_object('Document1', 'field2', left_schema, right_schema)

        assert isinstance(res, DropField)
        assert res.document_type == 'Document1'
        assert res.field_name == 'field2'
        assert res.parameters == {}

    @pytest.mark.parametrize('document_type', ('Document1', 'Document_new', 'Document_unknown'))
    def test_build_object__if_document_not_in_both_schemas__should_return_none(
            self, left_schema, document_type
    ):
        right_schema = Schema({
            'Document_new': Schema.Document({
                'field1': {'param11': 'schemavalue11', 'param12': 'schemavalue12'},
            }, parameters={'collection': 'document1'}),
            '~EmbeddedDocument2': Schema.Document({
                'field1': {'param3': 'schemavalue3'},
                'field2': {'param4': 'schemavalue4'},
            })
        })

        res = DropField.build_object(document_type, 'field2', left_schema, right_schema)

        assert res is None

    @pytest.mark.parametrize('field_name', ('field1', 'field3', 'field_unknown'))
    def test_build_object__if_field_does_not_drop_in_schema__should_return_none(
            self, left_schema, field_name
    ):
        right_schema = Schema({
            'Document1': Schema.Document({
                'field1': {'param11': 'schemavalue11', 'param12': 'schemavalue12'},
                'field3': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
            }, parameters={'collection': 'document1'}),
            '~EmbeddedDocument2': Schema.Document({
                'field1': {'param3': 'schemavalue3'},
                'field2': {'param4': 'schemavalue4'},
            })
        })

        res = DropField.build_object('Document1', field_name, left_schema, right_schema)

        assert res is None

    def test_to_schema_patch__should_return_dictdiff_object(self):
        left_schema = Schema({
            'Document1': Schema.Document({
                'field1': {'param11': 'schemavalue11', 'param12': 'schemavalue12'},
            }, parameters={'collection': 'document1'})
        })

        field_params = {'param11': 'schemavalue11', 'param12': 'schemavalue12'}
        expect = [(
            'remove',
            'Document1',
            [('field1', field_params)]
        )]
        action = DropField('Document1', 'field1')

        res = action.to_schema_patch(left_schema)

        assert res == expect

    @pytest.mark.parametrize('document_type,field_name', (
            ('Document_unknown', 'field2'),
            ('Document1', 'field_unknown'),
    ))
    def test_to_schema_patch__if_document_or_field_does_not_exist__should_raise_error(
            self, document_type, field_name
    ):
        left_schema = Schema({
            'Document1': Schema.Document({
                'field1': {'param11': 'schemavalue11', 'param12': 'schemavalue12'},
            })
        })

        action = DropField(document_type, field_name)
        test_schema_skel = {'param21': None, 'param22': None, 'param23': None}

        patcher = patch.object(action, 'get_field_handler_cls')
        with patcher as get_field_handler_cls_mock:
            get_field_handler_cls_mock.schema_skel.return_value = test_schema_skel

            with pytest.raises(SchemaError):
                action.to_schema_patch(left_schema)


class TestDropFieldEmbedded:
    def test_backward__if_default_is_not_set__should_do_nothing(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        dump = dump_db()

        action = DropField('~Schema1EmbDoc1', 'embdoc1_str')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_backward()

        assert dump == dump_db()

    def test_backward__if_required_and_default_is_set__should_create_field_and_set_a_value(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        default = 'test!'
        schema['~Schema1EmbDoc1']['test_field'] = {
            'unique_with': None,
            'null': False,
            'choices': None,
            'default': default,
            'sparse': False,
            'unique': False,
            'required': True,
            'db_field': 'test_field',
            'primary_key': False,
            'type_key': 'StringField',
            'max_length': None,
            'regex': None,
            'min_length': None
        }
        dump = dump_db()
        expect = deepcopy(dump)
        parsers = load_fixture('schema1').get_embedded_jsonpath_parsers('~Schema1EmbDoc1')
        for rec in itertools.chain.from_iterable(p.find(expect) for p in parsers):
            rec.value['test_field'] = default

        action = DropField('~Schema1EmbDoc1', 'test_field')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_backward()

        assert expect == dump_db()

    def test_forward__should_drop_field(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dump_db()
        expect = deepcopy(dump)
        parsers = load_fixture('schema1').get_embedded_jsonpath_parsers('~Schema1EmbDoc1')
        for rec in itertools.chain.from_iterable(p.find(expect) for p in parsers):
            if 'embdoc1_str' in rec.value:
                del rec.value['embdoc1_str']

        action = DropField('~Schema1EmbDoc1', 'embdoc1_str')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_forward()

        assert expect == dump_db()
