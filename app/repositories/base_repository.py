from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """
    Abstract Base Repository interface defining standard CRUD contracts.
    Follows OOP Dependency Inversion and Repository Pattern.
    """
    
    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass

    @abstractmethod
    def create(self, **kwargs: Any) -> T:
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        pass
