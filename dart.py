import sqlite3, random, asyncio, random
from os import environ
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from telegram import ParseMode, Dice

load_dotenv()

TOKEN = str(environ.get("BOT_TOKEN"))
conn = sqlite3.connect('dice_scores.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS scores (chat_id BIGINT,user_id BIGINT, score INT)")


def start(update, context):
    user = update.effective_user
    list_dice = "".join(map(lambda x: str(x), Dice.ALL_EMOJI))
    update.message.reply_text(f"""Hello {user.first_name}! I'm here to record every epic {list_dice} thrown around in your chats and set the stage for an intense battle among your members vying for the crown in /top. If you have strategic ideas for this bot, reach out to my ally, @dopmherebot. Want me to join your group? [Click here](http://telegram.me/thedartbot?startgroup=botstart) and let the competition unfold!""",parse_mode=ParseMode.MARKDOWN)


def get_random(score, total):
  if score == 6:
    inside = [
    f"Bullseye! You nailed it with a score of {score}, and your total is now {total}.",
    f"Oh, superb shot! Your score of {score} brings your total to an impressive {total}.",
    f"Boom! Bullseye achieved! Your latest score is {score}, and your overall total stands at {total}.",
    f"Direct hit! You scored {score}, pushing your total score to an awesome {total}.",
    f"Spot-on! With a score of {score}, your total now reaches an outstanding {total}.",
    f"Perfect aim! Your latest score is {score}, and your grand total is a whopping {total}.",
    f"Bullseye! You scored {score}, and your total now climbs to an impressive {total}.",
    f"Excellent precision! Your score of {score} brings your total to an impressive {total}.",
    f"Wow, another Bullseye! With a score of {score}, your total is now an outstanding {total}.",
    f"Right on target! Your latest score is {score}, and your total stands at a solid {total}."
    ]

    return random.choice(inside)
  else:
    outside = [
    f"Almost there! You just scored {score} points, bringing your total to {total}.",
    f"Nice try! Your latest score is {score}, elevating your overall total to {total}.",
    f"Great effort! You earned {score} points, making your grand total {total}.",
    f"Close call! The last play earned you {score} points, pushing your cumulative score to {total}.",
    f"Not bad! Your latest score of {score} contributes to a grand total of {total}.",
    f"Missed it by a hair! You scored {score} points, bringing your overall total to {total}.",
    f"Solid attempt! You just notched up {score} points, making your new total {total}.",
    f"So close! With a score of {score}, your total now stands at {total}.",
    f"Keep it up! The last move earned you {score} points, and your grand total is {total}." 
    ]
    return random.choice(outside)


def roll(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    score = update.message.dice.value
    if update.message.chat.type != "private":
        conn = sqlite3.connect('dice_scores.db')
        c = conn.cursor()
        c.execute("SELECT EXISTS (SELECT 1 FROM scores WHERE user_id = ? AND chat_id = ?)", (user_id, chat_id));
        notnew = c.fetchone()[0]
        if notnew:
            c.execute("UPDATE scores SET score = score + ? WHERE user_id = ? AND chat_id = ?", (score, user_id, chat_id));
            conn.commit()

        else:
            c.execute("INSERT INTO scores VALUES (?, ?, ?)", (chat_id, user_id, score))
            conn.commit()
        c.execute("SELECT score FROM scores WHERE user_id = ? AND chat_id = ?", (user_id, chat_id));
        total = c.fetchone()[0]
        conn.close()
        update.message.reply_text(get_random(score, total))
    else:
      update.message.reply_text("No point of playing alone. Please consider adding me in your groups!")


def leaderboard(update, context):
    if update.message.chat.type != "private":
       conn = sqlite3.connect('dice_scores.db')
       c = conn.cursor()
       c.execute("SELECT user_id, MAX(score) AS max_score FROM scores WHERE chat_id=? GROUP BY user_id ORDER BY max_score DESC", (update.message.chat_id,))
       results = c.fetchmany(size=10) #c.fetchall()
       if results:
          leaderboard_text = " Leaderboard (top 10) \n"
          for user_id, max_score in results:
              user = context.bot.get_chat_member(update.message.chat_id, user_id).user
              leaderboard_text += f"{user.full_name}: {max_score}\n"

          update.message.reply_text(leaderboard_text)
          conn.close()
       else:
          update.message.reply_text("There's no leaderboard to showcase. start playing and prove your competitive prowess!")
    else:
       update.message.reply_text("Oh, absolutely, playing alone will surely land you at the top of the 'Solo Party for One' leaderboard.")

def unknown(update, context):
     update.message.send_message(update.effective_chat.id, "Sorry, I didn't understand that command.")

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start, run_async=True))
dispatcher.add_handler(CommandHandler('top', leaderboard,  run_async=True))
dispatcher.add_handler(MessageHandler(filters.Filters.dice, roll,  run_async=True))
#dispatcher.add_handler(MessageHandler(filters.command, unknown))


updater.start_polling()
updater.idle()
