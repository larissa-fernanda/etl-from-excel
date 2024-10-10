import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from etl_from_excel.discord_bot import MyClient

@pytest.mark.asyncio
async def test_on_message_with_template():
    """
    Test the on_message method of the MyClient class.
    It should send a message with the template.
    """
    client = MyClient()

    with patch.object(MyClient, 'user', new=MagicMock()):
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.mentions = [client.user]
        mock_message.content = "template"

        mock_message.channel.send = AsyncMock()

        await client.on_message(mock_message)

@pytest.mark.asyncio
async def test_on_message_with_file():
    """
    Test the on_message method of the MyClient class.
    It should save the file.
    """
    client = MyClient()

    with patch.object(MyClient, 'user', new=MagicMock()), patch("os.remove") as mock_remove:
        mock_message = MagicMock()
        mock_message.author = MagicMock()
        mock_message.attachments = [MagicMock(filename="test_file.xlsx")]
        mock_message.attachments[0].save = AsyncMock()

        mock_message.channel.send = AsyncMock()

        await client.on_message(mock_message)

        mock_message.attachments[0].save.assert_called_once_with("./temp_test_file.xlsx")
        mock_remove.assert_called_once_with("./temp_test_file.xlsx")