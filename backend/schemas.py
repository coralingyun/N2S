"""Pydantic models for the screenplay YAML schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Project(BaseModel):
    title: str
    source_type: Literal["novel"]
    language: str
    adaptation_goal: Literal["screenplay_draft"]


class Metadata(BaseModel):
    author: str = ""
    created_at: str
    version: str = "0.1"
    source_chapter_count: int = Field(ge=3)


class Story(BaseModel):
    logline: str
    synopsis: str
    themes: list[str]
    tone: str
    narrative_perspective: str


class CharacterRelationship(BaseModel):
    character_id: str
    type: str
    description: str


class Character(BaseModel):
    id: str
    name: str
    role: str
    description: str
    motivation: str
    relationship_to_others: list[CharacterRelationship] = Field(default_factory=list)


class Act(BaseModel):
    act_id: str
    title: str
    function: str
    chapters_covered: list[str]


class Structure(BaseModel):
    acts: list[Act]


class SceneHeading(BaseModel):
    location: str
    time: str
    interior_exterior: Literal["INT", "EXT"]


class EmotionalArc(BaseModel):
    start: str
    end: str


class Beat(BaseModel):
    beat_id: str
    type: Literal["action", "dialogue", "narration", "note"]
    content: str
    character: str | None = None


class Scene(BaseModel):
    scene_id: str
    source_chapter: str
    scene_heading: SceneHeading
    purpose: str
    conflict: str
    characters_present: list[str]
    emotional_arc: EmotionalArc
    beats: list[Beat] = Field(min_length=1)


class Transition(BaseModel):
    from_scene: str
    to_scene: str
    type: str


class Notes(BaseModel):
    adaptation_notes: list[str] = Field(default_factory=list)
    unresolved_issues: list[str] = Field(default_factory=list)


class Screenplay(BaseModel):
    project: Project
    metadata: Metadata
    story: Story
    characters: list[Character] = Field(min_length=1)
    structure: Structure
    scenes: list[Scene] = Field(min_length=1)
    transitions: list[Transition] = Field(default_factory=list)
    notes: Notes

    @model_validator(mode="after")
    def validate_references(self) -> "Screenplay":
        character_ids = {character.id for character in self.characters}
        scene_ids = {scene.scene_id for scene in self.scenes}

        for scene in self.scenes:
            missing = [cid for cid in scene.characters_present if cid not in character_ids]
            if missing:
                raise ValueError(f"Scene {scene.scene_id} references unknown characters: {missing}")
            for beat in scene.beats:
                if beat.type == "dialogue" and not beat.character:
                    raise ValueError(f"Dialogue beat {beat.beat_id} is missing character.")
                if beat.character and beat.character not in character_ids:
                    raise ValueError(f"Beat {beat.beat_id} references unknown character {beat.character}.")

        for transition in self.transitions:
            if transition.from_scene not in scene_ids or transition.to_scene not in scene_ids:
                raise ValueError(
                    f"Transition references unknown scene: {transition.from_scene} -> {transition.to_scene}"
                )

        return self
