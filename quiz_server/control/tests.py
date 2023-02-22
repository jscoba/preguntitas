from django.test import TestCase
from django.contrib.auth.models import User
from control.models import *
from django.test import override_settings

from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from control.consumers import ControlConsumer
from player.consumers import PlayerConsumer

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


    async def test_player_connections(self):
        control = WebsocketCommunicator(ControlConsumer.as_asgi(), "/ws/consumer_control/")
        u1 = await database_sync_to_async(lambda: User.objects.get(username='u1'))()
        await database_sync_to_async(self.client.force_login)(u1)

        headers = [(b'origin', b'...'), (b'cookie', self.client.cookies.output(header='', sep='; ').encode())]
        player = WebsocketCommunicator(AuthMiddlewareStack(PlayerConsumer.as_asgi()), "/ws/consumer_player/", headers)
        await control.connect()
        #requested_info = await control.receive_json_from()
        #assert(requested_info["type"] == 'requestedInfo')
        await player.connect()
        player_connected = await control.receive_json_from()
        print(player_connected)
        assert(player_connected == {'type': "newPlayerJoined"})

        await player.disconnect()
        player_disconnected = await control.receive_json_from()
        assert(player_disconnected == {'type' : 'playerLeft'})
        await control.disconnect()

    async def test_show_next_question(self):
        control = WebsocketCommunicator(ControlConsumer.as_asgi(), "/ws/consumer_control/")
        u1 = await database_sync_to_async(lambda: User.objects.get(username='u1'))()
        await database_sync_to_async(self.client.force_login)(u1)

        headers = [(b'origin', b'...'), (b'cookie', self.client.cookies.output(header='', sep='; ').encode())]
        player = WebsocketCommunicator(AuthMiddlewareStack(PlayerConsumer.as_asgi()), "/ws/consumer_player/", headers)
        await control.connect()
        #requested_info = await control.receive_json_from()
        #assert(requested_info["type"] == 'requestedInfo')
        await player.connect()
        await control.receive_json_from()

        await control.receive_nothing()

        await control.send_json_to({'type' : 'nextQuestion', 'questionId' : 1})

        question_message = await player.receive_json_from()
        print(question_message)
        assert(question_message)
        