# Импортируем класс, который говорит нам о том,
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import NewsForm
from .models import News, NewsCategory, Author
from .filters import NewsFilter
from django.core.mail import EmailMultiAlternatives  # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html в текст
from django.conf import settings


class Profile(ListView):
    model = User
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_author'] = Author.objects.filter(authorUser_id=self.request.user.id).exists()
        context['profile'] = self.request.user
        context['email'] = self.request.user.email
        print(Author.objects.filter(authorUser_id=self.request.user.id).exists())
        # context['save_author'] = Author.objects.create(authorUser_id=self.request.user.id)
        return context


class NewsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = News
    # Поле, которое будет использоваться для сортировки объектов
    ordering = 'title'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news'
    paginate_by = 10  # регулируем количество записей на странице


class NewsDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = News
    # Используем другой шаблон — product.html
    template_name = 'news_id.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'news'


class NewsSearch(ListView):
    model = News
    ordering = 'title'
    template_name = 'search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = NewsFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset

        return context


# Добавляем новое представление для создания товаров.
class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_news',)
    raise_exception = True
    # Указываем нашу разработанную форму
    form_class = NewsForm
    # модель товаров
    model = News
    # и новый шаблон, в котором используется форма.
    template_name = 'edit_news.html'

    def form_valid(self, form):  # Переопределение метода при валидации формы NewsForm

        self.object = form.save(commit=False
                                )  # object - экземпляр заполненной формы NewsForm из запроса POST. В БД не сохраняем
        self.object.author = Author.objects.get(
            authorUser__username=self.request.user
        )  # Назначяем полю author модели News экзамеляр модели Author, где пользователь-автор совпадает с
        # пользователем-юзер
        return super().form_valid(
            form)  # Вызываем метод в родительском классе с измененной формой (а именно - определение поля author)


# Добавляем представление для изменения товара.
class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('simpleapp.change_news',)
    form_class = NewsForm
    model = News
    template_name = 'edit_news.html'


# Представление удаляющее товар.
class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('simpleapp.delete_news',)
    model = News
    template_name = 'delete_news.html'
    success_url = reverse_lazy('news_list')


class CategoryList(ListView):
    model = News
    # Поле, которое будет использоваться для сортировки объектов
    ordering = 'category'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'category_list.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(NewsCategory, id=self.kwargs['pk'])
        queryset = News.objects.filter(category=self.category).order_by('-dateCreation')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribes.all()
        context['category'] = self.category
        return context


@login_required  # проверка зареган ли user
def subscribe(request, pk):
    user = request.user
    category = NewsCategory.objects.get(id=pk)
    category.subscribes.add(user)
    message = 'Вы успешно подписались на рассылку новостей категории'

    return render(request, 'subscribe.html', {'category': category, 'message': message})
