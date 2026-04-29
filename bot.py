import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import datetime
import random
import string
import os

# ==============================
# 🔑 BOT TOKEN (SET IN RENDER ENV)
# ==============================
TOKEN = os.getenv("MTQ5OTExMDMwMTA1OTEyNTI4OA.GHgBCP.61lTE6ajw83csIcnYuitxQBLifGiAH5sA91dXw")

# ==============================
# SETUP
# ==============================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

keys = {}

# ==============================
# KEY GENERATOR
# ==============================
def gen_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

def create_key(hours=0, days=0):
    key = gen_key()
    expiry = datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)
    keys[key] = {
        "expiry": expiry,
        "hwid": None
    }
    return key, expiry

# ==============================
# DISCORD COMMAND
# ==============================
@bot.command()
async def key(ctx, duration: str):
    if duration == "1h":
        key, exp = create_key(hours=1)
    elif duration == "1w":
        key, exp = create_key(days=7)
    elif duration == "1m":
        key, exp = create_key(days=30)
    elif duration == "1y":
        key, exp = create_key(days=365)
    else:
        await ctx.send("❌ Use: !key 1h / 1w / 1m / 1y")
        return

    await ctx.send(f"🔑 Key: `{key}`\n⏳ Expires: {exp}")

# ==============================
# API (FOR YOUR C# APP)
# ==============================
@app.route("/redeem", methods=["POST"])
def redeem():
    try:
        data = request.json

        key = data.get("key")
        hwid = data.get("hwid")

        if key not in keys:
            return jsonify({"ok": False})

        k = keys[key]

        if datetime.datetime.now() > k["expiry"]:
            return jsonify({"ok": False, "error": "expired"})

        if k["hwid"] is None:
            k["hwid"] = hwid
        elif k["hwid"] != hwid:
            return jsonify({"ok": False, "error": "hwid_mismatch"})

        return jsonify({
            "ok": True,
            "expiry": k["expiry"].isoformat()
        })

    except:
        return jsonify({"ok": False})

# ==============================
# RUN BOT + API
# ==============================
def run_api():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_api).start()
    bot.run(TOKEN)
