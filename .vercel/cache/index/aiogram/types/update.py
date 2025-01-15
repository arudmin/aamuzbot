from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, cast

from ..utils.mypy_hacks import lru_cache
from .base import TelegramObject

if TYPE_CHECKING:
    from .callback_query import CallbackQuery
    from .chat_boost_removed import ChatBoostRemoved
    from .chat_boost_updated import ChatBoostUpdated
    from .chat_join_request import ChatJoinRequest
    from .chat_member_updated import ChatMemberUpdated
    from .chosen_inline_result import ChosenInlineResult
    from .inline_query import InlineQuery
    from .message import Message
    from .message_reaction_count_updated import MessageReactionCountUpdated
    from .message_reaction_updated import MessageReactionUpdated
    from .poll import Poll
    from .poll_answer import PollAnswer
    from .pre_checkout_query import PreCheckoutQuery
    from .shipping_query import ShippingQuery


class Update(TelegramObject):
    """
    This `object <https://core.telegram.org/bots/api#available-types>`_ represents an incoming update.

    At most **one** of the optional parameters can be present in any given update.

    Source: https://core.telegram.org/bots/api#update
    """

    update_id: int
    """The update's unique identifier. Update identifiers start from a certain positive number and increase sequentially. This ID becomes especially handy if you're using `webhooks <https://core.telegram.org/bots/api#setwebhook>`_, since it allows you to ignore repeated updates or to restore the correct update sequence, should they get out of order. If there are no new updates for at least a week, then identifier of the next update will be chosen randomly instead of sequentially."""
    message: Optional[Message] = None
    """*Optional*. New incoming message of any kind - text, photo, sticker, etc."""
    edited_message: Optional[Message] = None
    """*Optional*. New version of a message that is known to the bot and was edited"""
    channel_post: Optional[Message] = None
    """*Optional*. New incoming channel post of any kind - text, photo, sticker, etc."""
    edited_channel_post: Optional[Message] = None
    """*Optional*. New version of a channel post that is known to the bot and was edited"""
    message_reaction: Optional[MessageReactionUpdated] = None
    """*Optional*. A reaction to a message was changed by a user. The bot must be an administrator in the chat and must explicitly specify :code:`"message_reaction"` in the list of *allowed_updates* to receive these updates. The update isn't received for reactions set by bots."""
    message_reaction_count: Optional[MessageReactionCountUpdated] = None
    """*Optional*. Reactions to a message with anonymous reactions were changed. The bot must be an administrator in the chat and must explicitly specify :code:`"message_reaction_count"` in the list of *allowed_updates* to receive these updates."""
    inline_query: Optional[InlineQuery] = None
    """*Optional*. New incoming `inline <https://core.telegram.org/bots/api#inline-mode>`_ query"""
    chosen_inline_result: Optional[ChosenInlineResult] = None
    """*Optional*. The result of an `inline <https://core.telegram.org/bots/api#inline-mode>`_ query that was chosen by a user and sent to their chat partner. Please see our documentation on the `feedback collecting <https://core.telegram.org/bots/inline#collecting-feedback>`_ for details on how to enable these updates for your bot."""
    callback_query: Optional[CallbackQuery] = None
    """*Optional*. New incoming callback query"""
    shipping_query: Optional[ShippingQuery] = None
    """*Optional*. New incoming shipping query. Only for invoices with flexible price"""
    pre_checkout_query: Optional[PreCheckoutQuery] = None
    """*Optional*. New incoming pre-checkout query. Contains full information about checkout"""
    poll: Optional[Poll] = None
    """*Optional*. New poll state. Bots receive only updates about stopped polls and polls, which are sent by the bot"""
    poll_answer: Optional[PollAnswer] = None
    """*Optional*. A user changed their answer in a non-anonymous poll. Bots receive new votes only in polls that were sent by the bot itself."""
    my_chat_member: Optional[ChatMemberUpdated] = None
    """*Optional*. The bot's chat member status was updated in a chat. For private chats, this update is received only when the bot is blocked or unblocked by the user."""
    chat_member: Optional[ChatMemberUpdated] = None
    """*Optional*. A chat member's status was updated in a chat. The bot must be an administrator in the chat and must explicitly specify :code:`"chat_member"` in the list of *allowed_updates* to receive these updates."""
    chat_join_request: Optional[ChatJoinRequest] = None
    """*Optional*. A request to join the chat has been sent. The bot must have the *can_invite_users* administrator right in the chat to receive these updates."""
    chat_boost: Optional[ChatBoostUpdated] = None
    """*Optional*. A chat boost was added or changed. The bot must be an administrator in the chat to receive these updates."""
    removed_chat_boost: Optional[ChatBoostRemoved] = None
    """*Optional*. A boost was removed from a chat. The bot must be an administrator in the chat to receive these updates."""

    if TYPE_CHECKING:
        # DO NOT EDIT MANUALLY!!!
        # This section was auto-generated via `butcher`

        def __init__(
            __pydantic__self__,
            *,
            update_id: int,
            message: Optional[Message] = None,
            edited_message: Optional[Message] = None,
            channel_post: Optional[Message] = None,
            edited_channel_post: Optional[Message] = None,
            message_reaction: Optional[MessageReactionUpdated] = None,
            message_reaction_count: Optional[MessageReactionCountUpdated] = None,
            inline_query: Optional[InlineQuery] = None,
            chosen_inline_result: Optional[ChosenInlineResult] = None,
            callback_query: Optional[CallbackQuery] = None,
            shipping_query: Optional[ShippingQuery] = None,
            pre_checkout_query: Optional[PreCheckoutQuery] = None,
            poll: Optional[Poll] = None,
            poll_answer: Optional[PollAnswer] = None,
            my_chat_member: Optional[ChatMemberUpdated] = None,
            chat_member: Optional[ChatMemberUpdated] = None,
            chat_join_request: Optional[ChatJoinRequest] = None,
            chat_boost: Optional[ChatBoostUpdated] = None,
            removed_chat_boost: Optional[ChatBoostRemoved] = None,
            **__pydantic_kwargs: Any,
        ) -> None:
            # DO NOT EDIT MANUALLY!!!
            # This method was auto-generated via `butcher`
            # Is needed only for type checking and IDE support without any additional plugins

            super().__init__(
                update_id=update_id,
                message=message,
                edited_message=edited_message,
                channel_post=channel_post,
                edited_channel_post=edited_channel_post,
                message_reaction=message_reaction,
                message_reaction_count=message_reaction_count,
                inline_query=inline_query,
                chosen_inline_result=chosen_inline_result,
                callback_query=callback_query,
                shipping_query=shipping_query,
                pre_checkout_query=pre_checkout_query,
                poll=poll,
                poll_answer=poll_answer,
                my_chat_member=my_chat_member,
                chat_member=chat_member,
                chat_join_request=chat_join_request,
                chat_boost=chat_boost,
                removed_chat_boost=removed_chat_boost,
                **__pydantic_kwargs,
            )

    def __hash__(self) -> int:
        return hash((type(self), self.update_id))

    @property
    @lru_cache()
    def event_type(self) -> str:
        """
        Detect update type
        If update type is unknown, raise UpdateTypeLookupError

        :return:
        """
        if self.message:
            return "message"
        if self.edited_message:
            return "edited_message"
        if self.channel_post:
            return "channel_post"
        if self.edited_channel_post:
            return "edited_channel_post"
        if self.inline_query:
            return "inline_query"
        if self.chosen_inline_result:
            return "chosen_inline_result"
        if self.callback_query:
            return "callback_query"
        if self.shipping_query:
            return "shipping_query"
        if self.pre_checkout_query:
            return "pre_checkout_query"
        if self.poll:
            return "poll"
        if self.poll_answer:
            return "poll_answer"
        if self.my_chat_member:
            return "my_chat_member"
        if self.chat_member:
            return "chat_member"
        if self.chat_join_request:
            return "chat_join_request"
        if self.message_reaction:
            return "message_reaction"
        if self.message_reaction_count:
            return "message_reaction_count"
        if self.chat_boost:
            return "chat_boost"
        if self.removed_chat_boost:
            return "removed_chat_boost"

        raise UpdateTypeLookupError("Update does not contain any known event type.")

    @property
    def event(self) -> TelegramObject:
        return cast(TelegramObject, getattr(self, self.event_type))


class UpdateTypeLookupError(LookupError):
    """Update does not contain any known event type."""
