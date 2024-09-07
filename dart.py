import sqlite3, random
from os import environ, path
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,  MessageHandler, filters
from telegram import Update, Dice
from telegram.constants import ParseMode

load_dotenv()

TOKEN = str(environ.get("BOT_TOKEN"))
OWNER = int(458802161)

conn = sqlite3.connect('dice_scores.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS scores (chat_id BIGINT,user_id BIGINT, score INT, silent INT, clean INT)")
conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    list_dice = "".join(map(lambda x: str(x), Dice.ALL_EMOJI))
    await update.message.reply_text(f"""Hello {update.effective_user.first_name}! I'm here to record every epic {list_dice} thrown around in your chats and set the stage for an intense battle among your members vying for the crown in /top. If you have strategic ideas for this bot, reach out to my ally, @dopmherebot. Want me to join your group? [Click here](http://telegram.me/thedartbot?startgroup=botstart) and let the competition unfold!""",parse_mode=ParseMode.MARKDOWN)


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

    async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            c.execute("INSERT INTO scores (chat_id, user_id, score) VALUES (?, ?, ?)", (chat_id, user_id, score))
            conn.commit()
        c.execute("SELECT score FROM scores WHERE user_id = ? AND chat_id = ?", (user_id, chat_id));
        total = c.fetchone()[0]
        c.execute("SELECT silent, clean FROM scores WHERE chat_id=?", (chat_id,))
        silent = c.fetchone()[0]
        conn.close()
        if silent:
            await update.message.set_reaction(reaction='🍾')
        else:
            await update.message.reply_text(get_random(score, total))
      await update.message.reply_text("No point of playing alone. Please consider adding me in your groups!")


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != "private":
       conn = sqlite3.connect('dice_scores.db')
       c = conn.cursor()
       c.execute("SELECT user_id, MAX(score) AS max_score FROM scores WHERE chat_id=? GROUP BY user_id ORDER BY max_score DESC", (update.message.chat_id,))
       results = c.fetchmany(size=10) #c.fetchall()
       if results:
          leaderboard_text = " Leaderboard (top 10) \n"
          for user_id, max_score in results:
              user = (await context.bot.get_chat_member(update.message.chat_id, user_id)).user
              leaderboard_text += f"{user.full_name}: {max_score}\n"

          await update.message.reply_text(leaderboard_text)
          conn.close()
       else:
         await update.message.reply_text("There's no leaderboard to showcase. start playing and prove your competitive prowess!")
    else:
       await update.message.reply_text("Oh, absolutely, playing alone will surely land you at the top of the 'Solo Party for One' leaderboard.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id == OWNER:
       conn = sqlite3.connect('dice_scores.db')
       c = conn.cursor()
       c.execute("SELECT COUNT(DISTINCT user_id) FROM scores")
       total_user = c.fetchone()
       c.execute("SELECT COUNT(DISTINCT chat_id) FROM scores")
       total_chat = c.fetchone()
       c.execute("SELECT COUNT(score) FROM scores")
       total_score = c.fetchone()
       await update.message.reply_text(f"total unique users {total_user[0]} \ntotal unique chats {total_chat[0]} \ntotal score {total_score[0]}")
       conn.close()
    else:
       return None

async def silent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    if update.message.chat.type != "private" and any(admin.user.id == user_id for admin in (await context.bot.get_chat_administrators(chat_id))):
            conn = sqlite3.connect('dice_scores.db')
            c = conn.cursor()
            try:
                if str(context.args[0]).lower() == "no":
                    c.execute("UPDATE scores SET silent = 0 WHERE chat_id = ?", (chat_id,));
                    await update.message.reply_text(f"silent mode de-activated! I will send messages related to score updates from now on.")
                    conn.commit()
                    conn.close()
                elif str(context.args[0]).lower() == "yes":
                    c.execute("UPDATE scores SET silent = 1 WHERE chat_id = ?", (chat_id,));
                    await update.message.reply_text(f"silent mode activated! I will send reactions related to score updates instead of message.")
                    conn.commit()
                    conn.close()
                else:
                    await update.message.reply_text("""The /silent command allows you to control whether you receive notifications related to scores. When enabled, the command will suppress all score-related messages. \nUsage:
                        /silent [option]\nValid Options:
                        yes: Enable silent mode. This will prevent any score-related notifications from being sent to you.
                        no: Disable silent mode. You will start receiving score-related notifications again.""")
            except IndexError:
                await update.message.reply_text("""The /silent command allows you to control whether you receive notifications related to scores. When enabled, the command will suppress all score-related messages. \nUsage:
                        /silent [option]\nValid Options:
                        yes: Enable silent mode. This will prevent any score-related notifications from being sent to you.
                        no: Disable silent mode. You will start receiving score-related notifications again.""")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("silent",silent))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Dice.ALL, roll))
app.add_handler(CommandHandler("top", leaderboard))
app.add_handler(CommandHandler("stats", stats))
app.run_polling()