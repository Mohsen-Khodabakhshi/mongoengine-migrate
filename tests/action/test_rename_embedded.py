import pytest

from mongoengine_migrate.actions import RenameEmbedded
from mongoengine_migrate.graph import MigrationPolicy
from mongoengine_migrate.schema import Schema


class TestRenameEmbedded:
    def test_build_object__on_usual_document_type__should_return_none(self):
        left_schema = Schema({
            'Document1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'collection': 'document1'}),
            '~EmbeddedDocument1': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field22': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={}),
        })
        right_schema = Schema({
            'Document1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'collection': 'document1'}),
            '~EmbeddedDocument_new': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field22': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={}),
        })

        res = RenameEmbedded.build_object('Document1', left_schema, right_schema)

        assert res is None

    @pytest.mark.xfail
    def test_build_object__if_document_is_similar_with_other_document__should_return_none(self):
        left_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={}),
            '~EmbeddedDocument2': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field22': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={'collection': 'document21'}),
        })
        right_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={}),
            'Document2': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field22': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={'collection': 'document21'}),
        })

        res = RenameEmbedded.build_object('~EmbeddedDocument2', left_schema, right_schema)

        assert res is None

    @pytest.mark.parametrize('new_schema', (
        Schema.Document({
            'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
            'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
            'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
        }, parameters={'collection': 'document1'}),
        Schema.Document({
            'field_changed': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
            'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
            'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
        }, parameters={'collection': 'document1'}),
        Schema.Document({
            'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
            'field12': {'param_changed': 'schemavalue21', 'param22': 'schemavalue22'},
            'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
            'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
        }, parameters={'collection': 'document1'}),
        Schema.Document({
            'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
            'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            'field13': {'param31': 'schemavalue_changed', 'param32': 'schemavalue32'},
            'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
        }, parameters={'collection': 'document1'}),
        Schema.Document({
            'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
            'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
            'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
        }, parameters={'collection': 'document_changed'}),
    ))
    def test_build_object__if_changes_similarity_more_than_threshold__should_return_object(
            self, new_schema
    ):
        left_schema = Schema({
            '~EmbeddedDocument1': new_schema,
            'Document2': Schema.Document({
                'field1': {'param123': 'schemavalue123'},
            }, parameters={'collection': 'document123', 'test_parameter': 'test_value'}),
            '~EmbeddedDocument3': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            })
        })
        
        right_schema = Schema({
            '~EmbeddedDocument11': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
                'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
            }, parameters={'collection': 'document1'}),
            'Document2': Schema.Document({
                'field1': {'param123': 'schemavalue123'},
            }, parameters={'collection': 'document123', 'test_parameter': 'test_value'}),
            '~EmbeddedDocument31': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            })
        })
        
        res = RenameEmbedded.build_object('~EmbeddedDocument1', left_schema, right_schema)

        assert isinstance(res, RenameEmbedded)
        assert res.document_type == '~EmbeddedDocument1'
        assert res.new_name == '~EmbeddedDocument11'
        assert res.parameters == {}

    def test_build_object__if_there_are_several_rename_candidates__should_return_none(self):
        left_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
                'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
            }, parameters={'collection': 'document1'}),
            'Document2': Schema.Document({
                'field1': {'param123': 'schemavalue123'},
            }, parameters={'collection': 'document123', 'test_parameter': 'test_value'}),
            '~EmbeddedDocument3': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            })
        })
        
        right_schema = Schema({
            '~EmbeddedDocument11': Schema.Document({
                'field_changed': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field12': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
                'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
                'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
            }, parameters={'collection': 'document1'}),
            '~EmbeddedDocument111': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field12': {'param21': 'schemavalue_changed', 'param22': 'schemavalue22'},
                'field13': {'param31': 'schemavalue31', 'param32': 'schemavalue32'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
                'field15': {'param51': 'schemavalue51', 'param52': 'schemavalue52'},
            }, parameters={'collection': 'document1'}),
            'Document2': Schema.Document({
                'field1': {'param123': 'schemavalue123'},
            }, parameters={'collection': 'document123', 'test_parameter': 'test_value'}),
            '~EmbeddedDocument31': Schema.Document({
                'field11': {'param11': 'schemavalue11', 'param12': 'schemavalue21'},
                'field14': {'param41': 'schemavalue41', 'param42': 'schemavalue42'},
            }),
        })
        
        res = RenameEmbedded.build_object('~EmbeddedDocument1', left_schema, right_schema)

        assert res is None

    def test_build_object__if_changes_similarity_less_than_threshold__should_return_object(self):
        left_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'param1': 'value1'}),
            '~EmbeddedDocument2': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={'param2': 'value2'}),
        })
        right_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'param1': 'value1'}),
            '~EmbeddedDocument_new': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'param': 'value'}),
        })

        res = RenameEmbedded.build_object('Document2', left_schema, right_schema)

        assert res is None

    @pytest.mark.parametrize('document_type', ('Document1', 'Document_unknown'))
    def test_build_object__if_document_is_not_disappears_in_right_schema__should_return_none(
            self, document_type
    ):
        left_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'param1': 'value1'}),
            '~EmbeddedDocument2': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={'param2': 'value2'}),
        })
        right_schema = Schema({
            '~EmbeddedDocument1': Schema.Document({
                'field1': {'param1': 'schemavalue1', 'param2': 'schemavalue2'},
            }, parameters={'param1': 'value1'}),
            '~EmbeddedDocument2': Schema.Document({
                'field21': {'param21': 'schemavalue21', 'param22': 'schemavalue22'},
            }, parameters={'param2': 'value2'}),
        })

        res = RenameEmbedded.build_object(document_type, left_schema, right_schema)

        assert res is None

    def test_forward__should_do_nothing(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dump_db()

        action = RenameEmbedded('~Schema1EmbDoc1', new_name='~Schema1Doc')
        action.prepare(test_db, schema, MigrationPolicy.strict)

        action.run_forward()

        assert dump == dump_db()

    def test_backward__should_do_nothing(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dump_db()

        action = RenameEmbedded('~Schema1EmbDoc1', new_name='~Schema1Doc')
        action.prepare(test_db, schema, MigrationPolicy.strict)
        action.run_backward()

        assert dump == dump_db()
