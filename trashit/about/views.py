from django.views.generic import TemplateView

# Create your views here.

class About(TemplateView):
    template_name = 'about/index.html'

class PrivacyPolicy(TemplateView):
    def get_template_names(self):
        # Your logic to determine the template name
        template_name = self.determine_template_name()
        return [template_name]

    def determine_template_name(self):
        user_languages = self.request.META.get('HTTP_ACCEPT_LANGUAGE', 'en')

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
            return 'about/{}/privacy-policy.html'.format(preferred_language.lower())
        else:
            return 'about/en/privacy-policy.html'