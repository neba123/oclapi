from django.core.validators import RegexValidator
from rest_framework import serializers
from concepts.fields import LocalizedTextListField
from concepts.models import Concept, ConceptVersion
from oclapi.models import NAMESPACE_REGEX
from oclapi.serializers import HyperlinkedResourceSerializer, HyperlinkedSubResourceSerializer, ResourceVersionSerializer


class ConceptListSerializer(HyperlinkedResourceSerializer):
    id = serializers.CharField(source='mnemonic')
    conceptClass = serializers.CharField(source='concept_class')
    datatype = serializers.CharField()
    source = serializers.CharField(source='parent_resource')
    owner = serializers.CharField(source='owner_name')
    ownerType = serializers.CharField(source='owner_type')
    displayName = serializers.CharField(source='display_name')
    displayLocale = serializers.CharField(source='display_locale')

    class Meta:
        model = Concept
        fields = ('id', 'conceptClass', 'datatype', 'source', 'owner', 'ownerType', 'displayName', 'displayLocale', 'url')


class ConceptDetailSerializer(HyperlinkedSubResourceSerializer):
    conceptClass = serializers.CharField(source='concept_class')
    datatype = serializers.CharField()
    displayName = serializers.CharField(source='display_name')
    displayLocale = serializers.CharField(source='display_locale')
    names = LocalizedTextListField()
    descriptions = LocalizedTextListField()
    source = serializers.CharField(source='parent_resource')
    owner = serializers.CharField(source='owner_name')

    class Meta:
        model = Concept


class ConceptCreateOrUpdateSerializer(serializers.Serializer):
    class Meta:
        model = Concept
        lookup_field = 'mnemonic'

    def restore_object(self, attrs, instance=None):
        concept = instance if instance else Concept()
        concept.mnemonic = attrs.get(self.Meta.lookup_field, concept.mnemonic)
        concept.concept_class = attrs.get('concept_class', concept.concept_class)
        concept.datatype = attrs.get('datatype', concept.datatype)
        concept.names = attrs.get('names', concept.names)  # Is this desired behavior??
        concept.descriptions = attrs.get('descriptions', concept.descriptions)  # Is this desired behavior??
        return concept


class ConceptCreateSerializer(ConceptCreateOrUpdateSerializer):
    id = serializers.CharField(required=True, validators=[RegexValidator(regex=NAMESPACE_REGEX)], source='mnemonic')
    conceptClass = serializers.CharField(required=True, source='concept_class')
    datatype = serializers.CharField(required=False)
    names = LocalizedTextListField(required=True)
    descriptions = LocalizedTextListField(required=False)

    def save_object(self, obj, **kwargs):
        errors = Concept.persist_new(obj, **kwargs)
        self._errors.update(errors)


class ConceptVersionListSerializer(ResourceVersionSerializer):
    id = serializers.CharField(source='name')
    conceptClass = serializers.CharField(source='concept_class')
    datatype = serializers.CharField()
    source = serializers.CharField(source='parent_resource')
    owner = serializers.CharField(source='owner_name')
    ownerType = serializers.CharField(source='owner_type')
    displayName = serializers.CharField(source='display_name')
    displayLocale = serializers.CharField(source='display_locale')

    class Meta:
        model = ConceptVersion
        fields = ('id', 'conceptClass', 'datatype', 'source', 'owner', 'ownerType', 'displayName', 'displayLocale', 'url')


class ConceptVersionDetailSerializer(ResourceVersionSerializer):
    id = serializers.CharField(source='name')
    conceptClass = serializers.CharField(source='concept_class')
    datatype = serializers.CharField()
    displayName = serializers.CharField(source='display_name')
    displayLocale = serializers.CharField(source='display_locale')
    names = LocalizedTextListField()
    descriptions = LocalizedTextListField()
    source = serializers.CharField(source='parent_resource')
    owner = serializers.CharField(source='owner_name')

    class Meta:
        model = ConceptVersion
