from django.forms import DateTimeInput
from django_filters import FilterSet, DateTimeFilter, ModelChoiceFilter
from .models import News, NewsCategory


# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class NewsFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='dateCreation',
        lookup_expr='gt',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
           # В Meta классе мы должны указать Django модель,
           # в которой будем фильтровать записи.
           model = News
           # В fields мы описываем по каким полям модели
           # будет производиться фильтрация.
           fields = {
               # поиск по названию
               'title': ['icontains'],
               # количество товаров должно быть больше или равно
               'category': ['exact'],
           }
