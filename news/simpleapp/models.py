from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.db.models import Sum


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        post_rating = self.news_set.aggregate(Sum('rating')).get('rating__sum')
        if post_rating is None:
            post_rating = 0

        comment_rating = self.authorUser.comment_set.aggregate(Sum('rating')).get('rating__sum')
        if comment_rating is None:
            comment_rating = 0

        compost_rating = 0
        for post in self.post_set.all():
            rating = post.comment_set.aggregate(Sum('rating')).get('rating__sum')
            if rating is None:
                rating = 0
            compost_rating += rating

        self.ratingAuthor = post_rating * 3 + comment_rating + compost_rating
        self.save()


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, default=None)
    subscribes = models.ManyToManyField(User, related_name='categories')

    def __str__(self):
        return self.name


# Create your models here.
class News(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES,
                                    default=ARTICLE, verbose_name='Тип')
    dateCreation = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    # category = models.ForeignKey(
    #     to='NewsCategory',
    #     on_delete=models.CASCADE,
    #     related_name='news',
    #     verbose_name='Категория'# все продукты в категории будут доступны через поле news
    # )
    category = models.ManyToManyField(NewsCategory, through='Postcategory')
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])

    def preview(self):
        preview = self.text[0:124] + '...'
        return preview

    def __str__(self):
        return f'{self.title}| {self.text[:20]}'


class PostCategory(models.Model):
    postThrough = models.ForeignKey(News, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.postThrough.title()} | {self.categoryThrough.name}'


class Comment(models.Model):
    commentPost = models.ForeignKey(News, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
