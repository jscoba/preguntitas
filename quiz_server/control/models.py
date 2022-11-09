from django.db import models
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext as _ 

# Create your models here.

class MultipleCorrectAnswers(BaseException):
    pass

class Game(models.Model):

    name = models.TextField(_("Nombre del juego"),blank=False)
    expected_start_time = models.DateTimeField(_("Fecha esperada de inicio"), auto_now=False, auto_now_add=False, blank=False)
    real_start_time = models.DateTimeField(_("Fecha real de inicio"), auto_now=False, auto_now_add=False, blank=True)
    finished_time = models.DateTimeField(_("Fecha de finalización"), auto_now=False, auto_now_add=False, blank=True)
    is_active = models.BooleanField(_("Juego activo"), default=False)

    def save(self, *args, **kwargs) -> None:
        if(self.is_active):
            active_games = Game.objects.filter(is_active=True).all()
            for game in active_games:
                game.is_active = False
                game.save()
        return super().save(*args, **kwargs)
    

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")

    def __str__(self):
        return "Nombre del juego: %s\n" % self.name

    def get_absolute_url(self):
        return reverse("game_detail", kwargs={"pk": self.pk})


class Question(models.Model):

    game = models.ForeignKey("Game", verbose_name=_("Game"), on_delete=models.CASCADE)
    question_text = models.TextField(_("Texto de la pregunta"), blank=False)

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        return "Question: %s\n" % self.question_text

    def get_absolute_url(self):
        return reverse("question_detail", kwargs={"pk": self.pk})


class Answer_option(models.Model):

    question = models.ForeignKey("Question", verbose_name=_("Question"), on_delete=models.CASCADE)
    answer_option_text = models.TextField(_("Texto de la respuesta"))
    is_correct = models.BooleanField(_("Correcta"), blank=False)

    def save(self, *args, **kwargs) -> None:
        if (self.is_correct):
            count_correct = Answer_option.objects.filter(question = self.question, is_correct=True).count()
            if (count_correct != 0):
                raise MultipleCorrectAnswers
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("answer_option")
        verbose_name_plural = _("answer_options")

    def __str__(self):
        return "Answer text: %s\n" % self.answer_option_text

    def get_absolute_url(self):
        return reverse("answer_option_detail", kwargs={"pk": self.pk})