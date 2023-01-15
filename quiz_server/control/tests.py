from django.test import TestCase
from django.contrib.auth.models import User
from control.models import *
from django.test import override_settings

# Create your tests here.

class VotesSecurity(TestCase):
    def setUp(self) -> None:
        User.objects.create(username='u1')
        User.objects.create(username='u2')
        User.objects.create(username='u3')
        with override_settings(USE_TZ=False):
            g1 = Game.objects.create(name="Juego1", expected_start_time="2023-01-10 00:02:20", real_start_time="2023-01-10 00:02:30", finished_time = "2023-01-10 01:02:20", is_active=False)
            g2 = Game.objects.create(name="Juego2", expected_start_time="2023-01-10 00:02:20", real_start_time="2023-01-10 00:02:30", finished_time = "2023-01-10 01:02:20", is_active=False)
        q1 = Question.objects.create(game=g1, question_text="¿Quieres ser millonario?")
        q2 = Question.objects.create(game=g1, question_text="¿Quieres ser millonario?1")
        q3 = Question.objects.create(game=g1, question_text="¿Quieres ser millonario?2")
        q4 = Question.objects.create(game=g2, question_text="¿Quieres ser millonario?3")
        q5 = Question.objects.create(game=g2, question_text="¿Quieres ser millonario?4")
        a1 = Answer_option.objects.create(question=q1, answer_option_text="Si", is_correct = True)
        a2 = Answer_option.objects.create(question=q1, answer_option_text="No", is_correct = False)
        a3 = Answer_option.objects.create(question=q2, answer_option_text="Si", is_correct = True)
        a4 = Answer_option.objects.create(question=q1, answer_option_text="No", is_correct = False)

    def test_no_double_correct_answer(self):
        """A question can't have two correct answers"""
        q1 = Question.objects.first()
        with self.assertRaises(MultipleCorrectAnswers): 
            Answer_option.objects.create(question=q1, answer_option_text="Ñe", is_correct=True)

    def test_no_multiple_answers(self):
        u1 = User.objects.get(username='u1')
        q1 = Question.objects.first()
        ao = Answer_option.objects.filter(question=q1).first()
        vote1 = Vote.objects.create(user = u1, answer_option = ao)
        with self.assertRaises(MultipleVotes):
            # Check voting to the same answer option as before.
            Vote.objects.create(user=u1, answer_option = ao)
        with self.assertRaises(MultipleVotes):
            # Check voting different answer to the question already answered
            ao2 = Answer_option.objects.filter(question=q1, answer_option_text="No").first()
            Vote.objects.create(user=u1, answer_option=ao2)

    def test_dead_player(self):
        u1 = User.objects.get(username='u1')
        q1 = Question.objects.first()
        q2 = Question.objects.filter(question_text="¿Quieres ser millonario?1").first()
        ao = Answer_option.objects.filter(question=q1, is_correct = False).first()
        vote1 = Vote.objects.create(user = u1, answer_option = ao)
        #User has voted incorrectly for a question in this game.
        with self.assertRaises(DeadPlayer):
            ao2 = Answer_option.objects.filter(question=q2).first()
            vote2 = Vote.objects.create(user=u1, answer_option = ao2)
