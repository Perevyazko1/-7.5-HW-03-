from django.contrib.auth.models import User
from django.db import models


# Товар для нашей витрины
from django.urls import reverse


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, default=None)
    subscribes = models.ManyToManyField(User, related_name='categories')
    def __str__(self):
        return self.name


# Create your models here.
class News(models.Model):
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    )
    categoryType = models.CharField(max_length=2,choices=CATEGORY_CHOICES,
                                    default=ARTICLE,verbose_name='Тип')
    dateCreation = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    # category = models.ForeignKey(
    #     to='NewsCategory',
    #     on_delete=models.CASCADE,
    #     related_name='news',
    #     verbose_name='Категория'# все продукты в категории будут доступны через поле news
    # )
    category = models.ManyToManyField(NewsCategory,through='Postcategory')
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

    def preview(self):
        preview = self.text[0:124] + '...'
        return preview

    def __str__(self):
        return f'{self.title}| {self.text[:20]}'





class PostCategory(models.Model):
    postThrough = models.ForeignKey(News, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(NewsCategory,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.postThrough.title()} | {self.categoryThrough.name}'