from pydantic import BaseModel, Field
from typing import Optional


class Film(BaseModel):
    id: int = Field(..., description="AlloCiné ID of the film")
    url: str = Field(..., description="URL of the film")
    titre: str = Field(..., description="Title of the film")
    synopsis: str = Field(..., description="Synopsis of the film")
    public: Optional[str] = Field(None, description="Public category of the film")
    note_presse: Optional[float] = Field(None, description="Press rating")
    nb_notes_presse: Optional[int] = Field(None, description="Number of press ratings")
    nb_critiques_presse: Optional[int] = Field(None, description="Number of press critiques")
    note_spectateurs: Optional[float] = Field(None, description="Spectator rating")
    nb_notes_spectateurs: Optional[int] = Field(None, description="Number of spectator ratings")
    nb_critiques_spectateurs: Optional[int] = Field(None, description="Number of spectator critiques")
    date: Optional[str] = Field(None, description="Release date")
    duree: Optional[int] = Field(None, description="Duration in minutes")
    distributeur: Optional[str] = Field(None, description="Distributor of the film")
    recompenses: Optional[int] = Field(0, description="Number of awards")
    type: Optional[str] = Field(None, description="Type of the film (e.g., feature, short)")
    box_office_france: Optional[int] = Field(None, description="French box office revenue")
    langues: Optional[str] = Field(None, description="Languages of the film")
    couleur: Optional[str] = Field(None, description="Film color format")


class QueryRequest(BaseModel):
    sql_query: str


class Critique(BaseModel):
    film_id: int
    user_id: int
    rating: float  # Rating entre 0 et 5
    review_text: Optional[str] = None