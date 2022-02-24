import os
from linebot import (
    LineBotApi
)
from linebot.models import (
    RichMenu, RichMenuArea,
    RichMenuBounds, RichMenuSize, MessageAction, RichMenuSwitchAction
)
from linebot.models.actions import PostbackAction

line_bot_api = LineBotApi('sEsX2yDRvj454rjlxv8JQ4coXHyUTaAwOextJx0YvtkGh2eZUPwz6opSHz3HKj7erXf+eMN5gXdFfwnTjsdMsChCBsMAeHbiNwfqEZZOBk5OSLlSLHeZVoFl5CXvyM0KKslYItAO/c9kwdpKvKQcegdB04t89/1O/w1cDnyilFU=')


def createRichmenu():
    result = False
    # define a new richmenu
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name='add how richmenu',
        chat_bar_text='TAP HERE',
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=1666, height=843),
                action=MessageAction(text="ログイン")
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
                action=MessageAction(text="How to use")
            )
        ]
    )
    richMenuId = line_bot_api.create_rich_menu(
        rich_menu=rich_menu_to_create)

    with open(r'C:\Users\shimoda\PycharmProjects\scrayping\auto_fav\line-bot-git\line-notify-call-me\image\add_how.jpeg', 'rb') as f:
        line_bot_api.set_rich_menu_image(richMenuId, "image/jpeg", f)

    # set the default rich menu
    print(richMenuId)
    line_bot_api.set_default_rich_menu(richMenuId)
    result = True

    return result

#print(createRichmenu())

line_bot_api.unlink_rich_menu_from_user('U039da9cf7fe9ea0875e633f69b7f8e2e')
#line_bot_api.link_rich_menu_to_user('U039da9cf7fe9ea0875e633f69b7f8e2e', 'richmenu-0451994b328bb4d2525bf11584accbef')