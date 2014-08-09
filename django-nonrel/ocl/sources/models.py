from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djangotoolbox.fields import ListField
from oclapi.models import ConceptContainerModel, ConceptContainerVersionModel

SOURCE_TYPE = 'Source'

DICTIONARY_SRC_TYPE = 'dictionary'
REFERENCE_SRC_TYPE = 'reference'
EXTERNAL_DICT_SRC_TYPE = 'externalDictionary'
DEFAULT_SRC_TYPE = DICTIONARY_SRC_TYPE
SRC_TYPE_CHOICES = ((DICTIONARY_SRC_TYPE, 'Dictionary'),
                    (REFERENCE_SRC_TYPE, 'Reference'),
                    (EXTERNAL_DICT_SRC_TYPE, 'External Dictionary'))


class Source(ConceptContainerModel):
    source_type = models.TextField(choices=SRC_TYPE_CHOICES, default=DEFAULT_SRC_TYPE, blank=True)

    @classmethod
    def resource_type(cls):
        return SOURCE_TYPE

    @classmethod
    def get_version_model(cls):
        return SourceVersion

    @staticmethod
    def get_url_kwarg():
        return 'source'


SOURCE_VERSION_TYPE = 'Source Version'


class SourceVersion(ConceptContainerVersionModel):
    source_type = models.TextField(choices=SRC_TYPE_CHOICES, default=DEFAULT_SRC_TYPE, blank=True)
    concepts = ListField()

    def update_concept_version(self, concept_version):
        previous_version = concept_version.previous_version
        if previous_version and previous_version.id in self.concepts:
            index = self.concepts.index(previous_version.id)
            self.concepts[index] = concept_version.id
        else:
            self.concepts.append(concept_version.id)

    def seed_concepts(self):
        seed_concepts_from = self.previous_version or self.parent_version
        if seed_concepts_from:
            self.concepts = list(seed_concepts_from.concepts)

    @property
    def resource_type(self):
        return SOURCE_VERSION_TYPE

    @classmethod
    def for_base_object(cls, source, label, previous_version=None, parent_version=None, released=False):
        if not Source == type(source):
            raise ValidationError("source must be of type 'Source'")
        if not source.id:
            raise ValidationError("source must have an Object ID.")
        return SourceVersion(
            mnemonic=label,
            name=source.name,
            full_name=source.full_name,
            source_type=source.source_type,
            public_access=source.public_access,
            default_locale=source.default_locale,
            supported_locales=source.supported_locales,
            website=source.website,
            description=source.description,
            versioned_object_id=source.id,
            versioned_object_type=ContentType.objects.get_for_model(type(source)),
            released=released,
            previous_version=previous_version,
            parent_version=parent_version
        )


admin.site.register(Source)
admin.site.register(SourceVersion)

@receiver(post_save, sender=User)
def propagate_owner_status(sender, instance=None, created=False, **kwargs):
    if instance.is_active:
        for source in Source.objects.filter(owner=instance):
            source.undelete()
    else:
        for source in Source.objects.filter(owner=instance):
            source.soft_delete()
