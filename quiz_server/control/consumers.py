# control/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
from django.db.models import Count, Q
from django.core import serializers
from channels.db import database_sync_to_async

class ControlConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.name_group = 'consumer_control'
        self.player_group = 'consumer_player'

        await self.channel_layer.group_add(
            self.name_group,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.name_group,
            {
                'type' : "requestSyncInfo",
                'requestFrom' : self.channel_name
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.name_group,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, message_data):
        message_data_json = json.loads(message_data)
        message_type = message_data_json['type']

        if (message_type == "livePlayerStats"):
            
            live_viewers = message_data_json['liveViewers']
            alive_players = message_data_json['alivePlayers']
            total_players = message_data_json['totalPlayers']
            
            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "livePlayerStats",
                    'alivePlayers' : alive_players,
                    'liveViewers' : live_viewers,
                    'totalPlayers' : total_players
                }
            )
            
        elif (message_type == "nextQuestion"):
            
            question_id = message_data_json['questionId']
            answers_json = serializers.serialize("json",Answer_option.objects.filter(question__id=question_id), fields=("id", "answer_option_text"))
            question_text = await database_sync_to_async(Question.objects.filter(id=question_id).first())

            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "question",
                    'question' : {
                        'questionId' : question_id,
                        'questionText' : question_text,
                        'answerOptions' : answers_json
                    }
                }
            )

        elif (message_type == "hide"):
            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "hide"
                }
            )

        elif (message_type == "showQuestionResult"):
            
            question_id = message_data_json['questionId']
            answers = await database_sync_to_async(Answer_option.objects.filter(question__id=question_id).values("id", "is_correct"))
            question_text = await database_sync_to_async(Question.objects.filter(id=question_id).first())
            answers_list = list(answers)
            json_list_dict = []
            fields=['answerOptionId', 'isCorrect', 'AnswerOptionVotes']

            for a in answers_list:
                numVotos = await database_sync_to_async(Vote.objects.filter(answer_option__id=a[0]).count())
                a.append(numVotos)
                json_list_dict.append(dict(zip(fields,a)))

            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "questionResult",
                    'answerOptions' : json_list_dict
                }
            )
            

        elif (message_type == "actualScoreBoard"):

            votes_actual_game = Count('vote', filter=Q(vote__answer_option__question__game__is_active=True, vote_set__answer_option__is_correct=True))
            user_correct_votes = await database_sync_to_async(User.objects.annotate(votes=votes_actual_game).order_by("-votes").values("name", "votes"))
            values = list(user_correct_votes)
            json_list_dict = []
            fields = ['showName', 'points']

            for a in values:
                json_list_dict.append(dict(zip(fields, a)))
            
            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "actualScoreBoard",
                    'players' : json_list_dict
                }
            )

        
        elif (message_type == "generalScoreBoard"):

            votes_actual_game = Count('vote', filter=Q(vote_set__answer_option__is_correct=True))
            user_correct_votes = await database_sync_to_async(User.objects.annotate(votes=votes_actual_game).order_by("-votes").values("name", "votes"))
            values = list(user_correct_votes)
            json_list_dict = []
            fields = ['showName', 'points']
            
            for a in values:
                json_list_dict.append(dict(zip(fields, a)))
            
            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "generalScoreBoard",
                    'players' : json_list_dict
                }
            )
            
        
        elif (message_type == "endRequest"):
            
            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "endGame"
                }
            )
        
        elif (message_type == "start"):
            
            await self.channel_layer.group_send(
                self.player_group,
                {
                    'type' : "start"
                }
            )
        
        elif (message_type == "syncInfo"):
            
            await self.channel_layer.group_send(
                self.name_group,
                {
                    'type' : "syncInfo",
                    'to' : message_data_json['to'],
                    'liveViewers' : message_data_json['liveViewers'],
                    'alivePlayers' : message_data_json['alivePlayers'],
                    'totalPlayers' : message_data_json['totalPlayers']
                }
            )



        
    async def newVote(self, event):
        answer_option_id = event['answerOptionId']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "newVote",
            'answerOptionId' : answer_option_id
        }))

    async def newPlayerJoined(self, event):

        await self.send(text_data=json.dumps({
            'type': "newPlayerJoined"
        }))
    
    async def playerLeft(self, event):
        
        await self.send(text_data=json.dumps({
            'type': "playerLeft"
        }))
    
    async def requestSyncInfo(self, event):
        
        if event['requestFrom'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type' : "requestedInfo",
                'from' : event['requestFrom']
            }))
        
    
    async def syncInfo(self, event):
        
        if event['to'] == self.channel_name:
            await self.send(text_data=json.dumps({
                'type' : "requestedInfo",
                'liveViewers' : event['liveViewers'],
                'alivePlayers' : event['alivePlayers'],
                'totalPlayers' : event['totalPlayers']
            }))
