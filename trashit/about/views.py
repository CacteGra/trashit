from django.views.generic import TemplateView

# Create your views here.

def determine_template_name(user_languages, template_name):
    languages = []
    if user_languages:
        for lang in user_languages.split(','):
            lang_code = lang.split(';')[0].strip()
            languages.append(lang_code)
    
    # Determine preferred language
    preferred_language = 'en'  # default
    supported_languages = ['en', 'fr', 'es']  # your supported languages
    
    for lang in languages:
        if lang in supported_languages:
            preferred_language = lang
            break
        # Check language codes without region
        lang_code = lang.split('-')[0]
        if lang_code in supported_languages:
            preferred_language = lang_code
            break
    if preferred_language:
        return 'about/{0}/{1}.html'.format(preferred_language.lower(), template_name)
    else:
        return 'about/en/{}.html'.format(template_name)

class About(TemplateView):
    def get_template_names(self):
        # Your logic to determine the template name
        template_name = determine_template_name(self.request.META.get('HTTP_ACCEPT_LANGUAGE', 'en'), 'index')
        return [template_name]

class PrivacyPolicy(TemplateView):
    def get_template_names(self):
        # Your logic to determine the template name
        template_name = determine_template_name(self.request.META.get('HTTP_ACCEPT_LANGUAGE', 'en'), 'privacy-policy')
        return [template_name]

