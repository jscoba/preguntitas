# control/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from control.models import Answer_option
from control.models import *
from channels.db import database_sync_to_async

class PlayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.id == None:
            await self.deny()
        else:
            self.name_group = 'consumer_player'
            self.control_group = 'consumer_control'

            await self.channel_layer.group_add(
                self.name_group,
                self.channel_name
            )

            await self.channel_layer.group_send(
                self.control_group,
                {
                    'type' : "newPlayerJoined"
                }
            )

            await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_send(
                self.control_group,
                {
                    'type' : "playerLeft"
                }
            )

        await self.channel_layer.group_discard(
            self.name_group,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, message_data):
        message_data_json = json.loads(message_data)
        message_type = message_data_json['type']

        if (message_type == "vote"):

            answer_id = message_data_json['answerOptionId']
            
            answer = await database_sync_to_async(Answer_option.objects.filter(id=answer_id).first())

            try:
                new_vote = Vote(user=self.user, answer_option=answer)
                await database_sync_to_async(new_vote.save())

                await self.channel_layer.group_send(
                    self.control_group,
                    {
                        'type' : "newVote",
                        'answerOptionId' : answer_id
                    }
                )
            except (MultipleVotes, DeadPlayer) as e:
                print("User %s raised exception %s" % self.user, e)



        
    async def start(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "start"
        }))

    async def endGame(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "endGame"
        }))
    
    async def actualScoreBoard(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "actualScoreBoard",
            'players' : event['players']
        }))
    
    async def generalScoreBoard(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "generalScoreBoard",
            'players' : event['players']
        }))

    async def questionResult(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "questionResult",
            'answerOptions' : event['answerOptions']
        }))
    
    async def hide(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "hide"
        }))
    
    async def nextQuestion(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "nextQuestion",
            'question' : event['question']
        }))
    
    async def livePlayerStats(self, event):

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': "livePlayerStats",
            'alivePlayers' : event['alivePlayers'],
            'liveViewers' : event['liveViewers'],
            'totalPlayers' : event['totalPlayers']
        }))
