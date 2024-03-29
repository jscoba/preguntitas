# Preguntitas client-server communications

In preguntitas each client has to communicate with the server in real time to coordinate the game.
We'll be using Websockets as communications technology (Using django channels server-side).
The protocol between client and server is described below. Every message is a JSON encoded message. They should have AT LEAST the `type` attribute.

## WebSocket Messages

```json
// Name: startGameMessage
// Description: Anounces the beggining of active game when the operator clicks start action.
// Sent by: Control
// Received by: Clients through server
// Fields
{
    'type': "start"
}
```
```json
// Name: nextQuestionMessage
// Description: Activates a question of the game for the players to vote.
// Sent by: Control
// Received by: Server
// Fields
{
    'type': "nextQuestion",
    'questionId': string //Database ID of Question object.
}
```
```json
// Name: questionShowResultsMessage
// Description: Activates the question result overlay in players, deactivating (if still active) the question overlay.
// Sent by: Control
// Received by: Server
// Fields
{
    'type': "showQuestionResult",
    'questionId': string //Database ID of Question object.
}
```
```json
// Name: showActualScoreboardMessage
// Description: Activates the game Scoreboard for the players.
// Sent by: Control
// Received by: Server
// Fields
{
    'type': "showActualBoard"
}
```
```json
// Name: showGeneralScoreboardMessage
// Description: Activates the Scoreboard relative to ALL played games for the players.
// Sent by: Control
// Received by: Server
// Fields
{
    'type': "showGeneralBoard"
}
```
```json
// Name: endRequestMessage
// Description: Sent by operator when the game (livestream) is about to finish to assure correct termination.
// Sent by: Control
// Received by: Server
// Fields
{
    'type': "endRequest"
}
```
```json
// Name: livePlayerStatsMessage
// Description:
// Sent by: Control
// Received by: Players through server
// Fields
{
    'type': "livePlayerStats",
    'liveViewers' : number, //People watching livestream
    'alivePlayers' : number, //Players still alive (answering questions)
    'totalPlayers' : number //Initial alive players
}

```
```json
// Name: hideMessage
// Description: Message generated by Control to hide whatever element is on the screen and show only the video.
// Sent by: Control
// Received by: Players through server
// Fields
{
    'type': "hide",
}
```
```json
// Name: voteMessage
// Description: Message generated by player app when they tap an answer for the active question.
// Sent by: Player
// Received by: Server
// Fields
{
    'type': "vote",
    'answerOptionId': string //Database ID of Answer_option object clicked.
}
```
```json
// Name: questionResultMessage
// Description: 
// Sent by: Server
// Received by: Players
// Fields
{
    'type': "questionResult",
    'answerOptions' : [{
        'answerOptionId': string,
        'answerOptionVotes': number,
        'isCorrect': bool
    }, ...]
}
```
```json
// Name: actualScoreBoardMessage
// Description:
// Sent by: Server
// Received by: Players
// Fields
{
    'type': "actualScoreBoard",
    'players': [{
        'showName' : string,
        'points' : number
    }, ...] //Ordered by decreasing points
}
```
```json
// Name: generalScoreBoardMessage
// Description:
// Sent by: Server
// Received by: Players
// Fields
{
    'type': "generalScoreBoard",
    'players': [{
        'showName' : string,
        'points' : number
    }, ...] //Ordered by decreasing points
}
```
```json
// Name: questionMessage
// Description:
// Sent by: Server
// Received by: Players
// Fields
{
    'type': "question",
    'question': {
        'questionId': string,
        'questionText' : string,
        'answerOptions' : [{
            'answerOptionId': string,
            'answerOptionText' : string
        }, ...] //4 elements in the Iterable
    }
}
```
```json
// Name: endGameMessage
// Description:
// Sent by: Server
// Received by: Players
// Fields
{
    'type': "endGame"
}
```
```json
// Name: requestSyncInfoMessage
// Description: Requests players stats from other controls
// Sent by: Control
// Received by: Control
// Fields
{
    'type': "requestSyncInfo",
    'requestFrom': channel_name
}
```
```json
// Name: syncInfoMessage
// Description:
// Sent by: Server
// Received by: Players
// Fields
{
    'type' : "syncInfo",
    'to' : channel_name,
    'liveViewers' : current_viewers,
    'alivePlayers' : alive_players,
	'totalPlayers' : total
}
```