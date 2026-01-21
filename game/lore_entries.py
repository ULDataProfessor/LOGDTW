"""Lore entries data for LOGDTW2002

This file contains all lore entries that provide world-building information about
the game universe. To add new lore entries, add them to the LORE_ENTRIES dictionary
below.
"""

from typing import Dict
from game.story_types import LoreEntry


# Expanded lore entries
LORE_ENTRIES: Dict[str, LoreEntry] = {
    "Genesis Torpedo": LoreEntry(
        topic="Genesis Torpedo",
        content="A legendary weapon capable of terraforming entire planets or destroying them. The technology predates human civilization and was discovered in ancient alien ruins. The Federation claims to use it only for peaceful purposes, but rumors suggest it has been used as a weapon. The true extent of its power remains classified.",
    ),
    "Old Earth": LoreEntry(
        topic="Old Earth",
        content="The birthplace of humanity and the center of the Federation. Earth remains the most heavily populated and defended world in known space. It's said that all major decisions affecting the galaxy are made in the Federation Council chambers on Earth. The planet itself is now a monument to human achievement, though some say it's become a prison of bureaucracy.",
    ),
    "The Void": LoreEntry(
        topic="The Void",
        content="The unexplored regions between known sectors, where normal physics break down and strange phenomena occur. Many ships that venture too deep into the void never return. Those that do often report seeing impossible things—ships that shouldn't exist, planets that appear and disappear, and entities that defy description. Scientists believe the void may be a gateway to other dimensions or realities.",
    ),
    "Ancient Civilization": LoreEntry(
        topic="Ancient Civilization",
        content="An advanced alien race that existed millions of years before humanity. They left behind technology far beyond current understanding, including the Genesis Torpedo. Their ruins are found throughout the galaxy, but their fate remains unknown. Some believe they ascended to a higher plane of existence. Others think they were destroyed by something even more powerful.",
    ),
    "Pirate Code": LoreEntry(
        topic="Pirate Code",
        content="An unwritten set of rules that governs pirate behavior. While pirates are lawless, they maintain their own form of honor. Breaking the code results in being marked for death by all pirate factions. The code includes rules about not attacking each other's hideouts, respecting successful raids, and maintaining neutrality in certain conflicts.",
    ),
    "Federation Intelligence": LoreEntry(
        topic="Federation Intelligence",
        content="The secretive organization that handles the Federation's most sensitive operations. They're known for their extensive surveillance network, infiltration of other factions, and willingness to use extreme measures. Many believe they're responsible for events attributed to 'accidents' or 'natural causes.' Their true power and reach are unknown even to most Federation officials.",
    ),
    "The Great War": LoreEntry(
        topic="The Great War",
        content="A conflict that occurred two centuries ago, nearly destroying human civilization. The war was fought between Earth and the outer colonies over independence. It ended with the formation of the Federation, but the scars remain. Many current conflicts can be traced back to unresolved issues from the Great War.",
    ),
    "Alien Species": LoreEntry(
        topic="Alien Species",
        content="Several intelligent alien species have been encountered, though contact has been limited. The most significant are the Zephyrians, a peaceful race of traders; the K'tharr, a warrior species that respects strength; and the mysterious Void Dwellers, entities that exist in the void between sectors. Each species has its own technology, culture, and agenda.",
    ),
    "Stock Market Origins": LoreEntry(
        topic="Stock Market Origins",
        content="The galactic stock market was established after the Great War to stabilize the economy and prevent another collapse. The eight major companies that dominate it were chosen for their stability and importance to galactic infrastructure. However, rumors persist that the market is manipulated by shadow organizations with connections to Federation Intelligence.",
    ),
    "Holodeck Technology": LoreEntry(
        topic="Holodeck Technology",
        content="Advanced simulation technology that creates fully immersive experiences. While primarily used for entertainment, holodecks are also used for training, therapy, and classified simulations. Some programs are based on real historical events, including classified Federation operations. There are rumors of programs that can predict the future or access alternate realities.",
    ),
    "The Empire": LoreEntry(
        topic="The Empire",
        content="A militaristic faction that broke away from the Federation two decades ago, claiming the Federation had grown weak and corrupt. The Empire values strength, discipline, and order through conquest. They've conquered several sectors and established a rigid hierarchy. While they claim to bring order, many see them as oppressors. The Federation and Empire are in a cold war, with occasional skirmishes along their borders.",
    ),
    "Mercenary Companies": LoreEntry(
        topic="Mercenary Companies",
        content="Professional military organizations that work for hire. Mercenary companies range from small teams to massive organizations with their own fleets. They're bound by contracts and reputation—breaking a contract means no one will hire you again. The most respected companies can charge astronomical fees, but their success rates make them worth it. Some companies have been operating for centuries, passing leadership from generation to generation.",
    ),
    "Explorer's Guild": LoreEntry(
        topic="Explorer's Guild",
        content="An organization dedicated to charting unknown space and discovering new worlds. The Explorer's Guild maintains the most comprehensive maps of the galaxy and shares discoveries with all factions (for a fee). Guild members are known for their courage, curiosity, and sometimes recklessness. Many have died exploring the void, but their discoveries have led to the colonization of hundreds of worlds. The Guild's charter gives them rights to claim a percentage of resources found in newly discovered sectors.",
    ),
    "The Rebellion": LoreEntry(
        topic="The Rebellion",
        content="A loose network of freedom fighters who oppose Federation control. The Rebellion has no central leadership—instead, it's made up of independent cells that coordinate through encrypted channels. They've successfully liberated several colonies, but the Federation considers them terrorists. The Rebellion's methods range from peaceful protests to violent sabotage. Their ultimate goal is to establish a democratic government free from Federation control.",
    ),
    "Quantum Drive": LoreEntry(
        topic="Quantum Drive",
        content="The technology that enables faster-than-light travel. Quantum drives manipulate quantum fields to create 'bubbles' of space-time that allow ships to travel vast distances quickly. The technology was developed by Dr. Quantum fifty years ago and revolutionized space travel. However, the drives are expensive to build and maintain, and they require rare materials. Some believe the technology was reverse-engineered from alien artifacts.",
    ),
    "Sector Classification": LoreEntry(
        topic="Sector Classification",
        content="Sectors are classified by their danger level and development status. Core sectors are safe, well-developed areas under Federation control. Frontier sectors are developing regions with moderate danger. Dangerous sectors have high risk but valuable resources. Unexplored sectors are unknown territories where anything could be waiting. The classification system helps travelers understand what to expect, though classifications can change as sectors are explored and developed.",
    ),
    "The Arena": LoreEntry(
        topic="The Arena",
        content="A massive space station that hosts the galaxy's most prestigious combat tournaments. Fighters from all factions compete for fame, fortune, and the title of Arena Champion. The Arena is neutral territory—no faction disputes are allowed within its walls. The fights are broadcast throughout the galaxy, and champions become celebrities. Many fighters have used their Arena fame to gain political power or build mercenary companies. The Arena's owners are unknown, but they maintain strict neutrality and enforce the rules with overwhelming force.",
    ),
    "Ancient Ruins": LoreEntry(
        topic="Ancient Ruins",
        content="Remnants of the civilization that existed millions of years before humanity. These ruins are found throughout the galaxy and contain technology far beyond current understanding. The Genesis Torpedo was discovered in such ruins. Many expeditions have been lost exploring ruins, as they often contain traps, hostile automated defenses, or worse. Some ruins appear to be cities, others are research facilities, and a few seem to be weapons. Scientists believe there are thousands of ruins waiting to be discovered.",
    ),
    "The Black Market": LoreEntry(
        topic="The Black Market",
        content="An illegal network for trading restricted goods, stolen items, and information. The black market operates in the shadows, with connections in every major faction. Prices are high, but you can find things that are impossible to get legally. The market is controlled by several shadow organizations that maintain a delicate balance of power. Breaking the market's unwritten rules results in being blacklisted—or worse. Some say the black market is actually controlled by a single organization that manipulates prices and availability.",
    ),
    "Void Entities": LoreEntry(
        topic="Void Entities",
        content="Mysterious beings that exist in the void between sectors. Void entities defy description—those who have encountered them report seeing impossible things that don't follow normal physics. Some entities appear to be ships, others are massive creatures, and a few seem to be pure energy. Contact with void entities is extremely dangerous—many ships that encounter them never return. Scientists believe void entities may be from another dimension or reality, and that the void itself is a gateway between dimensions.",
    ),
    "The Great Exodus": LoreEntry(
        topic="The Great Exodus",
        content="The mass migration from Earth that occurred three centuries ago when Earth's resources were depleted. Millions of people left in colony ships, spreading humanity across the galaxy. The Exodus was chaotic and dangerous—many ships were lost, and some colonies failed. However, it led to the colonization of hundreds of worlds and the establishment of the Federation. The Exodus is remembered as both a tragedy and a triumph—the moment humanity left its cradle and claimed the stars.",
    ),
    "Faction Treaties": LoreEntry(
        topic="Faction Treaties",
        content="Agreements between factions that govern trade, borders, and military cooperation. Treaties can be broken if relations sour, which often leads to conflict. The most important treaty is the Neutral Zone Agreement, which establishes sectors where no faction has control. Treaties are negotiated by diplomats and enforced by military might. Breaking a treaty is considered an act of war, though some factions do it anyway if they think they can get away with it.",
    ),
    "The Lost Colonies": LoreEntry(
        topic="The Lost Colonies",
        content="Colony ships that disappeared during the Great Exodus and were never found. Some were destroyed, others may have reached unknown destinations, and a few might still be out there, lost in space. Finding a lost colony would be one of the greatest discoveries in history. Some explorers dedicate their lives to searching for lost colonies, following ancient records and sensor readings. A few lost colonies have been found over the years, but most remain mysteries.",
    ),
    "Galactic Currency": LoreEntry(
        topic="Galactic Currency",
        content="Credits are the standard currency used throughout the galaxy. The credit system was established after the Great War to facilitate trade between colonies. Credits are backed by the Federation, but their value fluctuates based on economic conditions. Some factions have tried to establish their own currencies, but credits remain the standard. The credit system is managed by the Galactic Banking Consortium, which maintains banks on major stations and planets. Credits can be stored in accounts, transferred electronically, or carried as physical chips.",
    ),
    "Ship Classes": LoreEntry(
        topic="Ship Classes",
        content="Ships are classified by size and purpose. Fighters are small, fast ships designed for combat. Freighters are large ships designed for cargo transport. Explorers are equipped for long-range missions and discovery. Cruisers are military ships designed for fleet combat. Capital ships are massive vessels that serve as mobile bases. Each class has advantages and disadvantages, and pilots often customize their ships to suit their needs. The most powerful ships are rare and expensive, requiring advanced technology and rare materials to build.",
    ),
    "The Phantom Fleet": LoreEntry(
        topic="The Phantom Fleet",
        content="A legend about ghost ships from the Great War that appear and disappear throughout the galaxy. Many pilots claim to have seen ships that shouldn't exist—vessels destroyed centuries ago. Some believe these are hallucinations caused by void exposure, others think they're time anomalies, and a few believe they're real ships somehow preserved. The Phantom Fleet is said to appear before major disasters, leading some to believe they're warnings or omens. No one has ever successfully made contact with the phantom ships.",
    ),
    "Alien Artifacts": LoreEntry(
        topic="Alien Artifacts",
        content="Objects left behind by alien civilizations, both ancient and recent. Alien artifacts range from simple tools to complex devices whose purpose is unknown. Some artifacts are harmless curiosities, others contain dangerous technology, and a few seem to be weapons. The Federation has strict regulations about alien artifacts, requiring them to be studied in secure facilities. However, many artifacts end up on the black market, where they fetch high prices. Some artifacts have been known to activate unexpectedly, with unpredictable results.",
    ),
    "The Void Gate": LoreEntry(
        topic="The Void Gate",
        content="A massive structure discovered in the deepest part of the void. The Void Gate appears to be a portal, but its destination is unknown. It's made of materials that don't exist anywhere else, and it defies all known physics. Scientists have been studying it for years, but no one has been able to activate it or determine its purpose. Some believe it's a gateway to another galaxy, others think it leads to another dimension, and a few fear it's a weapon waiting to be activated. The Gate is guarded by a joint task force from all major factions.",
    ),
    "The Shadow War": LoreEntry(
        topic="The Shadow War",
        content="A secret conflict being fought in the shadows between Federation Intelligence and unknown enemies. The Shadow War has been going on for decades, but most people don't know it exists. Federation Intelligence operates in complete secrecy, using extreme measures to fight enemies that may not even be human. The war has cost countless lives, but the public is never told. Some believe the Shadow War is actually a cover for Federation Intelligence's own operations, while others think the enemies are so terrible that the truth must be hidden.",
    ),
}

