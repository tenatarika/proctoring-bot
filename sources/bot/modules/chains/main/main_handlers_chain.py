"""
Bot main handlers chain implementation module.
"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import ChatType
from aiogram.types import InlineKeyboardMarkup

from ....loggers import LogInstaller
from ...handlers_chain import HandlersChain
from ...handlers_registrar import HandlersRegistrar as Registrar
from ...keyboard.keyboard import KeyboardBuilder


class MainStates(StatesGroup):
    """
    Bot main handlers chain states class implementation.
    """


class MainKeyboardsBuilder:
    """
    Bot main handlers chain keyboard builder class implementation.
    """

    @staticmethod
    def get_private_start_keyboard() -> InlineKeyboardMarkup:
        """
        Gets keyboard to send message to private user chat.

        :return: Returns inline keyboard markup.
        :rtype: :obj:`InlineKeyboardMarkup`
        """
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Пройти регистрацию": "auth",
                },
            ]
        )

    @staticmethod
    def get_info_keyboard() -> InlineKeyboardMarkup:
        """
        Gets keyboard to send information about user message to chat.

        :return: Returns inline keyboard markup.
        :rtype: :obj:`InlineKeyboardMarkup`
        """
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Посмотреть информацию": "info",
                },
            ]
        )


class MainHandlersChain(HandlersChain):
    """
    Bot main handlers chain class implementation.
    """

    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)

    @staticmethod
    async def _start_routine(message: types.Message, state: FSMContext):
        await state.update_data(username=message.from_user.username)
        data = await state.get_data()
        data_size = len(data.get("auth").keys())
        greeting = f"Привет, {message.from_user.first_name}\n"

        if data_size != 3 and data_size != 1:
            text = f"{greeting}Вы не зарегестрированы\n"
            keyboard_markup = MainKeyboardsBuilder.get_private_start_keyboard()
        else:
            text = f"{greeting}Вы уже зарегестрированы"
            keyboard_markup = MainKeyboardsBuilder.get_info_keyboard()

        return text, keyboard_markup

    @staticmethod
    @Registrar.message_handler(commands=["start"], chat_type=ChatType.GROUP)
    async def start_handler(message: types.Message, state: FSMContext):
        """
        Asks user ro start registration process or speaks about that he is registered.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        MainHandlersChain._logger.debug("Start main group conversation state")
        text, _ = await MainHandlersChain._start_routine(message, state)
        await message.reply(text)

    @staticmethod
    @Registrar.message_handler(commands=["start"], chat_type=ChatType.PRIVATE)
    async def start_handler(message: types.Message, state: FSMContext):
        """
        Starts dialog with user by 'start' command. Shows to user main keyboard to choose action.
        Send to user registration state message.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        MainHandlersChain._logger.debug("Start main private conversation state")
        text, keyboard_markup = await MainHandlersChain._start_routine(message, state)
        await message.reply(text, reply_markup=keyboard_markup)

    @staticmethod
    @Registrar.message_handler(commands=["info"])
    async def get_info_handler(message: types.Message, state: FSMContext):
        """
        Sends to user information: username, name, group and subgroup by 'info' command.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        data = await state.get_data()
        await message.reply(MainHandlersChain.get_info(data))

    @staticmethod
    @Registrar.callback_query_handler(text="info")
    async def get_info_handler(query: types.CallbackQuery, state: FSMContext):
        """
        Sends to user information: username, name, group and subgroup by 'info' callback query message.

        :param query: Callback query message
        :type query: :obj:`types.CallbackQuery`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        data = await state.get_data()
        await query.message.reply(MainHandlersChain.get_info(data))

    @staticmethod
    def get_info(user_data) -> str:
        """
        Gets to user information: username, name, group and subgroup from spreadsheet storage.

        :param user_data: User data
        :type user_data: :obj:`dict[Any]`

        :return: Returns information about user.
        :rtype: :obj:`str`
        """
        auth_data = user_data.get("auth")

        if user_data["type"] == "student":
            name = auth_data.get("name")
            group = auth_data.get("group")
            subgroup = auth_data.get("subgroup")

            return f"Информация о Вас:\nФИО: {name}\nГруппа: {group}\nПодгруппа: {subgroup}\n"
        elif user_data["type"] == "teacher":
            name = auth_data.get("ФИО")

            return f"Информация о Вас:\nФИО: {name}\n"
