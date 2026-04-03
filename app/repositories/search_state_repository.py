from datetime import date

from sqlmodel import Session, select

from models import SearchState


class SearchStateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self) -> SearchState:
        state = self.session.exec(select(SearchState)).first()
        if not state:
            state = SearchState()
            self.session.add(state)
            self.session.commit()
            self.session.refresh(state)
        return state

    def update_initialized_at(self, value: date) -> None:
        state = self.get()
        state.initialized_at = value
        self.session.commit()

    def update_last_search(self, value: date) -> None:
        state = self.get()
        state.last_search = value
        self.session.commit()
