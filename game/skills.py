"""
Skills system for LOGDTW2002
Handles player skill progression and development
"""

class Skill:
    """Represents a player skill"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.level = 1
        self.experience = 0
        self.max_level = 100
        self.experience_to_next = 100
    
    def gain_experience(self, amount: int) -> bool:
        """Gain experience in this skill, return True if leveled up"""
        self.experience += amount
        
        # Check for level up
        if self.experience >= self.experience_to_next:
            if self.level < self.max_level:
                self.level += 1
                self.experience -= self.experience_to_next
                self.experience_to_next = int(self.experience_to_next * 1.2)
                return True
        
        return False
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage to next level"""
        if self.level >= self.max_level:
            return 100.0
        return (self.experience / self.experience_to_next) * 100
    
    def get_skill_bonus(self) -> float:
        """Get skill bonus based on level"""
        return self.level * 0.1  # 10% bonus per level
    
    def get_description(self) -> str:
        """Get detailed skill description"""
        desc = f"[bold cyan]{self.name}[/bold cyan]\n"
        desc += f"[italic]{self.description}[/italic]\n\n"
        desc += f"Level: {self.level}/{self.max_level}\n"
        desc += f"Experience: {self.experience}/{self.experience_to_next}\n"
        desc += f"Progress: {self.get_progress_percentage():.1f}%\n"
        desc += f"Bonus: +{self.get_skill_bonus():.1f}%\n"
        
        return desc 