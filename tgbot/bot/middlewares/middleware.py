from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from common.models import Text


# from common.models import RequiredChannel


# class CounterMiddleware(BaseMiddleware):
#     def __init__(self) -> None:
#         self.counter = 0
#
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Message,
#             data: Dict[str, Any]
#     ) -> Any:
#         self.counter += 1
#         data['counter'] = self.counter
#         return await handler(event, data)


class TextMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        try:
            self.texts = Text.texts_data()
        except Exception as e:
            self.user = None

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['texts'] = self.texts
        return await handler(event, data)
