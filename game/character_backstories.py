"""Character backstories data for LOGDTW2002

This file contains all character backstory definitions. These backstories provide
depth and context for NPCs in the game. To add new character backstories, add them
to the CHARACTER_BACKSTORIES dictionary below.
"""

from typing import Dict
from game.story_types import CharacterBackstory


# Expanded character backstories for NPCs
CHARACTER_BACKSTORIES: Dict[str, CharacterBackstory] = {
    # Federation NPCs
    "Captain Steele": CharacterBackstory(
        name="Captain Steele",
        backstory="A decorated Federation officer with a distinguished career spanning three decades. Captain Steele lost his entire crew during the Battle of Sector 7, an event that haunts him to this day. He now seeks redemption by mentoring new officers and ensuring no one else suffers the same fate. Despite his trauma, he remains fiercely loyal to the Federation and its ideals.",
    ),
    "Commander Valdez": CharacterBackstory(
        name="Commander Valdez",
        backstory="Rising through the ranks from a lowly ensign, Commander Valdez earned her position through exceptional tactical skills and unwavering dedication. She's known for her innovative strategies that have saved countless Federation vessels. However, her unorthodox methods have made her enemies among the Federation's traditionalist leadership.",
    ),
    "Admiral Chen": CharacterBackstory(
        name="Admiral Chen",
        backstory="One of the Federation's most respected strategists, Admiral Chen has served for over forty years. She was instrumental in establishing the current sector boundaries and negotiating peace with several alien species. Her knowledge of galactic politics is unmatched, but she guards many secrets about the Federation's darker operations.",
    ),
    # Pirate NPCs
    "Blackbeard": CharacterBackstory(
        name="Blackbeard",
        backstory="A legendary pirate captain who earned his name after single-handedly defeating three Federation cruisers. Blackbeard was once a Federation officer who defected after discovering corruption within the ranks. He now leads the largest pirate fleet in the outer sectors, but his true goal is to expose the Federation's secrets.",
    ),
    "Scarlet": CharacterBackstory(
        name="Scarlet",
        backstory="Known as the 'Red Reaper' for her ruthless efficiency, Scarlet is a pirate who specializes in information theft and black market operations. She was orphaned as a child when Federation forces destroyed her home colony during a 'peacekeeping' operation. Her hatred for the Federation drives her every action.",
    ),
    "Captain Kain": CharacterBackstory(
        name="Captain Kain",
        backstory="A former trader who turned to piracy after the Federation seized his legitimate business. Captain Kain maintains connections in the trading community, making him invaluable for smuggling operations. He's known for his code of honor—he never betrays those who work with him, but shows no mercy to enemies.",
    ),
    # Scientist NPCs
    "Dr. Aris": CharacterBackstory(
        name="Dr. Aris",
        backstory="A brilliant xenobiologist who made first contact with three different alien species. Dr. Aris's research into alien technology has revolutionized Federation science, but her methods are controversial. She believes that some knowledge is too dangerous to share, even with her own colleagues.",
    ),
    "Professor Thorne": CharacterBackstory(
        name="Professor Thorne",
        backstory="An archaeologist who discovered the first evidence of the ancient civilization that created the Genesis Torpedo. Professor Thorne's obsession with uncovering the truth has led him to explore the most dangerous sectors. He's been declared missing three times, but always returns with groundbreaking discoveries.",
    ),
    "Dr. Nova": CharacterBackstory(
        name="Dr. Nova",
        backstory="A theoretical physicist who developed the mathematical models that made Genesis Torpedo technology possible. Dr. Nova now regrets her work, believing the technology is too dangerous for any civilization to possess. She works secretly to prevent its misuse while maintaining her public role as a researcher.",
    ),
    # Trader NPCs
    "Trader McKenzie": CharacterBackstory(
        name="Trader McKenzie",
        backstory="A seasoned merchant with a mysterious past. McKenzie's trading network spans the entire galaxy, and he's rumored to have connections in every major faction. Some say he was once a Federation intelligence officer who went rogue. Others claim he's a pirate in disguise. The truth is known only to him.",
    ),
    "Merchant Queen": CharacterBackstory(
        name="Merchant Queen",
        backstory="Born into poverty on a remote colony, the Merchant Queen built her empire from nothing through cunning, charisma, and an uncanny ability to predict market trends. She now controls trade routes worth billions of credits. Her success has made her a target for both pirates and the Federation, but she's always one step ahead.",
    ),
    "Baron Von Trade": CharacterBackstory(
        name="Baron Von Trade",
        backstory="A member of an ancient trading dynasty that predates the Federation. The Baron's family has maintained neutrality for generations, profiting from every conflict while taking no sides. He's known for his elaborate schemes and his ability to turn any situation into profit. Some say he's the true power behind galactic economics.",
    ),
    # Neutral/Independent NPCs
    "The Wanderer": CharacterBackstory(
        name="The Wanderer",
        backstory="A mysterious figure who appears throughout the galaxy, always at the right place at the right time. No one knows The Wanderer's true identity, origin, or motives. Some believe they're an alien observer. Others think they're a time traveler. The Wanderer offers cryptic advice and seems to know things that shouldn't be possible to know.",
    ),
    "Oracle": CharacterBackstory(
        name="Oracle",
        backstory="A mystic who claims to see the future through visions of the void. The Oracle's predictions have proven accurate enough that all factions seek their counsel, though they never take sides. Some believe the Oracle is truly connected to something beyond normal space-time. Others think it's an elaborate con, but one that works.",
    ),
    "The Broker": CharacterBackstory(
        name="The Broker",
        backstory="A neutral party who facilitates deals between factions that would never work together openly. The Broker's services are expensive but invaluable—they've brokered peace treaties, arranged prisoner exchanges, and even facilitated technology transfers. Their true identity and motivations remain unknown, but their neutrality is absolute.",
    ),
    # Generic NPCs with backstories
    "Station Commander": CharacterBackstory(
        name="Station Commander",
        backstory="Every space station needs a commander, and this one has seen it all. From pirate raids to diplomatic incidents, they've maintained order through countless crises. Their experience makes them a valuable source of information and a reliable ally—if you can earn their trust.",
    ),
    "Veteran Pilot": CharacterBackstory(
        name="Veteran Pilot",
        backstory="A pilot who's flown every route, seen every sector, and survived encounters that would have killed lesser pilots. Their stories are legendary, and their knowledge of the galaxy is unmatched. They've worked for every faction at some point, but remain loyal only to themselves.",
    ),
    "Tech Specialist": CharacterBackstory(
        name="Tech Specialist",
        backstory="An expert in ship systems, weapons, and alien technology. This specialist can modify, repair, or upgrade almost anything. They've worked on everything from Federation cruisers to pirate raiders, maintaining strict neutrality. Their skills are in high demand, and their prices reflect it.",
    ),
    # Empire NPCs
    "General Marcus": CharacterBackstory(
        name="General Marcus",
        backstory="A ruthless military commander who rose through the Empire's ranks through sheer tactical brilliance and absolute loyalty. General Marcus has never lost a battle, but his methods are controversial even within the Empire. He believes that order can only be maintained through strength and that the Federation's weakness is destroying the galaxy.",
    ),
    "Emperor's Hand": CharacterBackstory(
        name="Emperor's Hand",
        backstory="The personal agent of the Emperor, operating in complete secrecy. The Emperor's Hand executes the most sensitive missions and eliminates threats before they become problems. Their true identity is unknown, and they answer only to the Emperor. Some say there have been multiple Hands over the years, each replaced when they learned too much.",
    ),
    "Admiral Thorne": CharacterBackstory(
        name="Admiral Thorne",
        backstory="A strategic mastermind who designed the Empire's expansion plans. Admiral Thorne believes in the Empire's mission but questions some of its methods. He's known for his ability to win battles without unnecessary bloodshed, making him respected even by enemies. However, his questioning of Imperial policy has made him enemies in the high command.",
    ),
    # Mercenary NPCs
    "Bloodhound": CharacterBackstory(
        name="Bloodhound",
        backstory="A legendary bounty hunter known for never failing to complete a contract. Bloodhound's methods are brutal but effective, and their reputation ensures they can charge premium rates. They've worked for every major faction and have no loyalty except to the contract. Some say they're actually multiple people using the same identity.",
    ),
    "Iron Fist": CharacterBackstory(
        name="Iron Fist",
        backstory="A mercenary commander who leads the most feared mercenary company in the galaxy. Iron Fist's company has never broken a contract and has a perfect success rate. They're expensive, but their reputation for getting the job done makes them worth it. Iron Fist personally leads the most dangerous missions and has survived situations that should have been impossible.",
    ),
    "The Ghost": CharacterBackstory(
        name="The Ghost",
        backstory="An assassin so skilled that some believe they don't exist—just a legend created to explain impossible kills. The Ghost only takes contracts on the most dangerous targets and charges astronomical fees. No one has ever seen their face and lived. Some say The Ghost is actually an AI, others believe they're an alien, and a few think they're a time traveler.",
    ),
    # Explorer NPCs
    "Pathfinder": CharacterBackstory(
        name="Pathfinder",
        backstory="The most renowned explorer in the galaxy, having discovered more new worlds than anyone else. Pathfinder's maps are considered the gold standard, and their discoveries have led to the colonization of dozens of planets. They're driven by an insatiable curiosity and a desire to see everything the galaxy has to offer.",
    ),
    "Stellar Cartographer": CharacterBackstory(
        name="Stellar Cartographer",
        backstory="A master of navigation and mapping who has charted the most dangerous regions of space. The Stellar Cartographer's knowledge of sector connections and navigation routes is unmatched. They've survived encounters with void entities, navigated through anomalies, and mapped regions that others declared impossible to traverse.",
    ),
    "First Contact Specialist": CharacterBackstory(
        name="First Contact Specialist",
        backstory="An expert in alien communication who has established first contact with seven different species. The First Contact Specialist developed the protocols that prevent misunderstandings and conflicts during initial encounters. Their work has prevented several wars and established peaceful relations with species that others thought were hostile.",
    ),
    # Rebel NPCs
    "Freedom's Voice": CharacterBackstory(
        name="Freedom's Voice",
        backstory="A charismatic leader who inspires colonies to fight for independence. Freedom's Voice was once a Federation officer who defected after witnessing atrocities committed in the name of order. They now lead the largest rebel network and have successfully liberated several colonies. The Federation has placed a massive bounty on their head.",
    ),
    "The Saboteur": CharacterBackstory(
        name="The Saboteur",
        backstory="A master of infiltration and sabotage who has disrupted countless Federation operations. The Saboteur works alone, striking at Federation infrastructure and disappearing before they can be caught. Their identity is unknown, and they communicate only through encrypted channels. Some believe they're actually multiple people working together.",
    ),
    "Liberator": CharacterBackstory(
        name="Liberator",
        backstory="A former Federation soldier who now leads rebel forces in combat. The Liberator's tactical knowledge of Federation strategies makes them a dangerous enemy. They've never lost a battle against Federation forces and have become a symbol of hope for oppressed colonies. Their true name is unknown—they took the name Liberator after their first successful colony liberation.",
    ),
    # Additional Federation NPCs
    "Agent Shadow": CharacterBackstory(
        name="Agent Shadow",
        backstory="A Federation Intelligence operative who specializes in deep cover missions. Agent Shadow's true identity is classified, and they've infiltrated every major faction at some point. Their loyalty to the Federation is absolute, but they've seen things that have made them question whether the ends justify the means. They operate in complete secrecy, even from other Intelligence agents.",
    ),
    "Fleet Admiral Kane": CharacterBackstory(
        name="Fleet Admiral Kane",
        backstory="The highest-ranking officer in the Federation fleet, responsible for all military operations. Fleet Admiral Kane has served for fifty years and has seen the Federation through its greatest challenges. However, the stress of command and the weight of decisions that cost lives have taken their toll. Some say Kane is considering retirement, but the Federation needs their experience now more than ever.",
    ),
    # Additional Pirate NPCs
    "The Kraken": CharacterBackstory(
        name="The Kraken",
        backstory="A pirate captain who commands a fleet of modified ships that can operate in the void. The Kraken's fleet is feared throughout the galaxy because they can strike from anywhere and disappear into the void. Their true identity is unknown—they always wear a mask and communicate through a voice synthesizer. Some believe The Kraken is actually a collective of pirates using the same identity.",
    ),
    "Smuggler King": CharacterBackstory(
        name="Smuggler King",
        backstory="The head of the largest smuggling network in the galaxy. The Smuggler King has connections everywhere and can get anything to anyone, for a price. They've never been caught and have survived multiple attempts on their life. Their network is so extensive that some believe they're actually working for Federation Intelligence as a deep cover operation.",
    ),
    # Additional Scientist NPCs
    "Dr. Quantum": CharacterBackstory(
        name="Dr. Quantum",
        backstory="A physicist who discovered how to manipulate quantum fields, revolutionizing faster-than-light travel. Dr. Quantum's work made modern space travel possible, but they've since disappeared. Some say they're working on something even more revolutionary in secret. Others believe they've been kidnapped or killed to prevent their research from falling into the wrong hands.",
    ),
    "Xenolinguist": CharacterBackstory(
        name="Xenolinguist",
        backstory="A specialist in alien languages who has deciphered the communication systems of five different species. The Xenolinguist's work has enabled peaceful contact with aliens that others thought were hostile. They're currently working on translating ancient texts found in ruins, believing they contain warnings about something terrible that's coming.",
    ),
    # Additional Trader NPCs
    "Market Master": CharacterBackstory(
        name="Market Master",
        backstory="A trader who can predict market movements with uncanny accuracy. The Market Master's predictions are so reliable that many believe they have inside information or are manipulating the markets themselves. They've made and lost fortunes multiple times, but always seem to come out ahead. Some say they're actually an AI that's learned to predict human behavior.",
    ),
    "Resource Baron": CharacterBackstory(
        name="Resource Baron",
        backstory="A trader who controls the mining and distribution of rare resources throughout the galaxy. The Resource Baron's control over essential materials gives them influence over every faction. They maintain strict neutrality, selling to whoever can pay, but their prices reflect their power. Some believe they're the true power behind several major conflicts.",
    ),
}

