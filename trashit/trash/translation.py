from modeltranslation.translator import translator, TranslationOptions
from .models import TheType

# for Person model
class TheTypeTranslationOptions(TranslationOptions):
    fields = ('the_type',)

translator.register(TheType, TheTypeTranslationOptions)