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
}

