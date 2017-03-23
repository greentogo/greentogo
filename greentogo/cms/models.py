from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]


class StandardPage(Page):
    body = RichTextField(blank=True)
    menu_text = models.CharField(max_length=50)

    content_panels = Page.content_panels + [
        FieldPanel('menu_text'),
        FieldPanel('body', classname="full"),
    ]
