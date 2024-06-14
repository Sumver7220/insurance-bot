from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 設定你的LINE Messaging API的Token與Secret
LINE_CHANNEL_ACCESS_TOKEN = "1wtqxQEnOqkQJ0oH+IgwqP6OU+GhExc6mFwnJPcgzqa8TeJF2HS7JsX+I+u+muwtgRxES1of4LSE7K2WFSQmXwYGgscCaDFvT/A0Y3DkRUV3yvVOBrAnwIEWUaZrZF1HAIwAksdzKhetrNeEk5OzowdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "8b9ecd4c1abe82ef5c977084c30c53a9"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    # 確認請求是來自LINE
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.lower()

    if "試算" in user_message:
        reply_message = "請提供您的年齡、性別和保險金額，我們將為您計算預估費用。"
    else:
        reply_message = "您好，這裡是保險問答機器人。請問有什麼可以幫您？"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))


def calculate_insurance(age, gender, amount):
    base_rate = 1000  # 基本費率
    age_factor = age * 10
    gender_factor = 1.2 if gender == "male" else 1.1
    total_cost = base_rate + age_factor * gender_factor + amount * 0.01
    return f"{total_cost:.2f}"


@handler.add(MessageEvent, message=TextMessage)
def handle_calculation_request(event):
    details = event.message.text.split(" ")
    if len(details) == 4 and details[0].lower() == "試算":
        try:
            age = int(details[1])
            gender = details[2].lower()
            amount = int(details[3])
            estimated_cost = calculate_insurance(age, gender, amount)
            reply_message = f"根據您提供的資料，預估保險費用為：{estimated_cost}元"
        except ValueError:
            reply_message = "請輸入有效的年齡和保險金額。"
    else:
        reply_message = "請提供您的年齡、性別和保險金額，我們將為您計算預估費用。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))


if __name__ == "__main__":
    app.run(port=3000)
