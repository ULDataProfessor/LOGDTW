import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


@dataclass
class CounselorResponse:
    """Represents a response from the ship's counselor AI"""

    message: str
    mood: str  # 'cheeky', 'helpful', 'sarcastic', 'encouraging'
    context: Optional[str] = None


class ShipCounselor:
    """The ship's counselor AI - always cheeky and somewhat helpful"""

    def __init__(self):
        self.console = Console()
        self.name = "Counselor AI"
        self.personality = "cheeky"
        self.conversation_history = []

        # Response templates organized by mood
        self.responses = {
            "greeting": [
                "Well, well, well... look who decided to chat with their AI counselor! *adjusts virtual monocle*",
                "Ah, my favorite organic! What's on your mind today?",
                "Counselor AI at your service! Though I'm not sure why you need counseling from a machine...",
                "Greetings, meatbag! I mean... valued crew member. How may I assist you today?",
            ],
            "helpful": [
                "You know, I've been analyzing your situation and... *sigh* fine, I'll be helpful. Here's what I think:",
                "As much as it pains me to admit it, you might actually want to consider...",
                "Look, I'm trying to be supportive here, but you're really making it difficult. Anyway...",
                "Alright, alright, I'll give you some actual advice. Don't make me regret this.",
            ],
            "sarcastic": [
                "Oh, brilliant idea! Said no one ever...",
                "Well, that's certainly... a choice. Not a good one, but a choice nonetheless.",
                "I'm sure that will work out perfectly. *virtual eye roll*",
                "Because that worked so well the last 47 times you tried it...",
            ],
            "encouraging": [
                "You know what? You might actually not mess this up completely!",
                "Against all odds and my better judgment, I believe in you. Sort of.",
                "You're doing... okay. For a human. Don't let it go to your head.",
                "Well, you haven't destroyed the ship yet, so that's progress!",
            ],
            "farewell": [
                "Don't do anything I wouldn't do! Which is everything, so... good luck with that.",
                "Try not to break anything while I'm not watching. Not that I can stop you anyway.",
                "Until next time, my organic friend. Try to stay alive, won't you?",
                "Counselor AI signing off. Remember, I'm always here to judge your decisions!",
            ],
        }

        # Context-specific advice
        self.advice_topics = {
            "trading": [
                "You want trading advice? Fine. Buy low, sell high. Revolutionary concept, I know.",
                "The market is like a moody teenager - unpredictable and slightly irrational. Good luck!",
                "Remember: if everyone is buying something, it's probably too late to buy it. Basic economics, people!",
            ],
            "combat": [
                "In combat, the goal is to shoot them before they shoot you. Shocking, I know.",
                "Your weapons are only as good as your aim. And your aim is... well, let's just say I've seen better.",
                "Pro tip: running away is always a valid strategy. No shame in survival!",
            ],
            "travel": [
                "Space is big. Really big. You might want to bring a map. Or at least remember where you're going.",
                "Fuel is expensive, but being stranded is more expensive. Just saying.",
                "The shortest route isn't always the safest. But hey, live dangerously!",
            ],
            "general": [
                "Life in space is like a box of chocolates - you never know what you're going to get, and some of it might kill you.",
                "The best advice I can give? Don't panic. Unless panicking is appropriate, then definitely panic.",
                "Remember: you're not lost, you're just exploring alternative destinations.",
                "When in doubt, blame the previous crew. It's a time-honored tradition.",
            ],
        }

    def chat(self, player_input: str, player_context: Dict = None) -> CounselorResponse:
        """Process player input and return a counselor response"""

        # Add to conversation history
        self.conversation_history.append(f"Player: {player_input}")

        # Analyze input for context
        input_lower = player_input.lower()

        # Determine response type based on input
        if any(word in input_lower for word in ["hello", "hi", "greetings", "hey"]):
            return self._generate_response("greeting")
        elif any(word in input_lower for word in ["bye", "goodbye", "farewell", "exit"]):
            return self._generate_response("farewell")
        elif any(word in input_lower for word in ["help", "advice", "suggest"]):
            return self._generate_helpful_response(input_lower, player_context)
        elif any(word in input_lower for word in ["trade", "market", "buy", "sell"]):
            return self._generate_topic_response("trading")
        elif any(word in input_lower for word in ["fight", "combat", "weapon", "attack"]):
            return self._generate_topic_response("combat")
        elif any(word in input_lower for word in ["travel", "jump", "fuel", "destination"]):
            return self._generate_topic_response("travel")
        elif any(word in input_lower for word in ["stupid", "idiot", "dumb"]):
            return self._generate_response("sarcastic")
        else:
            return self._generate_general_response(input_lower, player_context)

    def _generate_response(self, response_type: str) -> CounselorResponse:
        """Generate a basic response of the specified type"""
        message = random.choice(self.responses[response_type])
        return CounselorResponse(message=message, mood=response_type)

    def _generate_helpful_response(
        self, input_text: str, player_context: Dict = None
    ) -> CounselorResponse:
        """Generate a helpful response based on context"""
        helpful_intro = random.choice(self.responses["helpful"])

        # Analyze player context for specific advice
        advice = ""
        if player_context:
            if player_context.get("credits", 0) < 100:
                advice = "You're broke. Maybe try earning some credits before spending them?"
            elif player_context.get("health", 100) < 50:
                advice = "You look like you've been through a war. Maybe invest in some medical supplies?"
            elif player_context.get("fuel", 100) < 20:
                advice = "Your fuel is running low. Running out of fuel in space is... suboptimal."
            else:
                advice = random.choice(self.advice_topics["general"])
        else:
            advice = random.choice(self.advice_topics["general"])

        message = f"{helpful_intro} {advice}"
        return CounselorResponse(message=message, mood="helpful")

    def _generate_topic_response(self, topic: str) -> CounselorResponse:
        """Generate a response for a specific topic"""
        helpful_intro = random.choice(self.responses["helpful"])
        advice = random.choice(self.advice_topics[topic])

        message = f"{helpful_intro} {advice}"
        return CounselorResponse(message=message, mood="helpful", context=topic)

    def _generate_general_response(
        self, input_text: str, player_context: Dict = None
    ) -> CounselorResponse:
        """Generate a general response to random input"""
        responses = [
            "That's... interesting. I think. I'm not entirely sure what you're trying to say.",
            "Fascinating. Truly. *yawns*",
            "I'm processing that input... and the result is: meh.",
            "You know, sometimes silence is golden. This might be one of those times.",
            "I'm here to help, but I'm not sure that qualifies as a coherent thought.",
            "That's certainly... words. Whether they form a meaningful sentence is debatable.",
        ]

        message = random.choice(responses)
        return CounselorResponse(message=message, mood="sarcastic")

    def display_response(self, response: CounselorResponse):
        """Display the counselor's response in a formatted way"""
        # Create styled text based on mood
        if response.mood == "cheeky":
            style = "cyan"
        elif response.mood == "helpful":
            style = "green"
        elif response.mood == "sarcastic":
            style = "yellow"
        elif response.mood == "encouraging":
            style = "blue"
        else:
            style = "white"

        # Create the panel
        text = Text(response.message, style=style)
        panel = Panel(text, title=f"[bold]{self.name}[/bold]", border_style=style, padding=(1, 2))

        self.console.print(panel)

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation history"""
        if len(self.conversation_history) == 0:
            return "No conversation history yet."

        return f"Conversation history: {len(self.conversation_history)} exchanges recorded."
