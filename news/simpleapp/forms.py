from django import forms
from django.core.exceptions import ValidationError

from .models import News, Author


class NewsForm(forms.ModelForm):
    title = forms.CharField(max_length=30)
    class Meta:
        model = News
        fields = [
            'title',
            'text',
            'category',
            'categoryType',

        ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        text = cleaned_data.get("text")

        if text is not None and len(text) < 10:
            raise ValidationError({
                "text": "Заголовок не может быть менее 10 символов."
            })

        if title == text:
            raise ValidationError(
                "Описание не должно быть идентично названию."
            )

        return cleaned_data