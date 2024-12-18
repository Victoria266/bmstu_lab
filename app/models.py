from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Resource(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    density = models.IntegerField(verbose_name="Плотность")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"
        db_table = "resources"


class Report(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', blank=True,  null=True)

    company = models.CharField(blank=True, null=True)
    month = models.CharField(blank=True, null=True)

    def __str__(self):
        return "Отчет №" + str(self.pk)

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
        db_table = "reports"
        ordering = ('-date_formation', )


class ResourceReport(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.DO_NOTHING, blank=True, null=True)
    report = models.ForeignKey(Report, on_delete=models.DO_NOTHING, blank=True, null=True)
    plan_volume = models.IntegerField(verbose_name="Поле м-м", default=0)
    volume = models.IntegerField(verbose_name="Вычисляемое поле", blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "resource_report"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['resource', 'report'], name="resource_report_constraint")
        ]
