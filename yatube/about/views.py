from django.views.generic.base import TemplateView


# Описать класс AboutAuthorView для страницы about/author
class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'СТРаница'
        context['text'] = ('Всё равно страшно')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Очень страница'
        context['text'] = ('У меня Ай Ай')
        return context
