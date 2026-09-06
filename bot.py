import os
import threading
import time
import discord
from discord import ui
from flask import Flask

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (ОБХОД СТАНДАРТНОГО ТАЙМАУТА) ---
app = Flask("")


@app.route("/")
def home():
  return "⚡ Arizona Hub & Prime is alive!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# --- СПИСОК СЕРВЕРОВ ARIZONA RP ---
SERVERS = {
    "1": "Phoenix",
    "2": "Tucson",
    "3": "Scottdale",
    "4": "Chandler",
    "5": "Brainburg",
    "6": "Saint Rose",
    "7": "Mesa",
    "8": "Red-Rock",
    "9": "Gilbert",
    "10": "Surprise",
    "11": "Prescott",
    "12": "Glendale",
    "13": "Kingman",
    "14": "Winslow",
    "15": "Payson",
    "16": "Show-Low",
    "17": "Airit",  # Исправлено под реальное название сервера
    "18": "Casa-Grande",
    "19": "Page",
    "20": "Sun-City",
    "21": "Queen-Creek",
    "22": "Sedona",
    "23": "Holiday",
    "24": "Wednesday",
    "25": "Yava",
    "26": "Faraway",
    "27": "Bumble Bee",
    "28": "Christmas",
    "29": "Mirage",
    "30": "Love",
    "31": "Drake",
    "32": "Space",
    "33": "Home",
}


def format_server(server_input: str) -> str:
  clean_num = "".join(filter(str.isdigit, server_input))
  if clean_num in SERVERS:
    return f"**#{clean_num} | {SERVERS[clean_num]}**"
  return f"**#{server_input}**"


# --- ИНТЕРАКТИВНОЕ МЕНЮ В ЧАТЕ ---
class EventSelect(ui.Select):

  def __init__(self, guild=None):
    options = [
        discord.SelectOption(
            label="Операция «Мираж»",
            description="Мпшка на выживание (3-10 мин)",
            emoji=(
                discord.utils.get(guild.emojis, name="mirage")
                if guild
                else None
            ),
        ),
        discord.SelectOption(
            label="Капт",
            description="Захват территории для банд (5-60 мин)",
            emoji=(
                discord.utils.get(guild.emojis, name="kapt") if guild else None
            ),
        ),
        discord.SelectOption(
            label="Битва за притон",
            description="Сражение за наркопритон (до 24ч)",
            emoji=(
                discord.utils.get(guild.emojis, name="bitva_za_priton")
                if guild
                else None
            ),
        ),
        discord.SelectOption(
            label="Битва за нефтевышки",
            description="Борьба за нефтяные вышки (до 24ч)",
            emoji=(
                discord.utils.get(guild.emojis, name="bitva_za_neftevishky")
                if guild
                else None
            ),
        ),
        discord.SelectOption(
            label="Семейные битвы",
            description="Масштабные войны семей (до 24ч)",
            emoji=(
                discord.utils.get(guild.emojis, name="semeynaya_bitva")
                if guild
                else None
            ),
        ),
    ]

    super().__init__(
        placeholder="✨ Выберите мероприятие для создания оповещения...",
        min_values=1,
        max_values=1,
        options=options,
    )

  async def callback(self, interaction: discord.Interaction):
    selected = self.values[0]
    if selected == "Операция «Мираж»":
      await interaction.response.send_modal(MirageModal())
    elif selected == "Капт":
      await interaction.response.send_modal(CaptModal())
    elif selected == "Битва за притон":
      await interaction.response.send_modal(PritonModal())
    elif selected == "Битва за нефтевышки":
      await interaction.response.send_modal(OilModal())
    elif selected == "Семейные битвы":
      await interaction.response.send_modal(FamilyModal())


class EventView(ui.View):

  def __init__(self, guild=None):
    super().__init__(timeout=None)
    self.add_item(EventSelect(guild))


def get_emoji(guild, name):
  emoji = discord.utils.get(guild.emojis, name=name)
  return str(emoji) if emoji else f":{name}:"


def get_timestamp(minutes_str):
  try:
    mins = (
        int("".join(filter(str.isdigit, minutes_str)))
        if not minutes_str.isdigit()
        else int(minutes_str)
    )
  except:
    mins = 5

  future_unix = int(time.time()) + (mins * 60)
  return f"<t:{future_unix}:R>"


EMBED_COLOR = discord.Color.from_rgb(255, 87, 34)


# --- 1. МИРАЖ ---
class MirageModal(ui.Modal, title="✈️ Операция «Мираж»"):
  server_input = ui.TextInput(
      label="Номер сервера",
      placeholder="Например: 24",
      style=discord.TextStyle.short,
      required=True,
  )
  time_input = ui.TextInput(
      label="Минут до начала (число)",
      placeholder="Например: 5",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    CHANNEL_ID = 1545777967072813096
    role_mentions = "<@&1543326454648020992> <@&1545788983303348326>"

    try:
      channel = await interaction.client.fetch_channel(CHANNEL_ID)
    except Exception:
      channel = None

    guild = interaction.guild
    n = get_emoji(guild, "notify")
    s = get_emoji(guild, "server")
    t = get_emoji(guild, "time")
    c = get_emoji(guild, "command")
    a = get_emoji(guild, "avtor")

    server_str = format_server(self.server_input.value)
    time_code = get_timestamp(self.time_input.value)

    desc = (
        f"### {n} Оповещение » Мероприятие «Операция мираж»\n"
        f"───────────────────────────────\n"
        f"{s} **Сервер:** {server_str}\n"
        f"{t} **Начало МП:** {time_code}\n"
        f"{a} **Автор уведомления:** {interaction.user.mention}\n"
        f"{c} **Команда для телепорта на МП:** `/gomp`"
    )

    embed = discord.Embed(description=desc, color=EMBED_COLOR)
    embed.set_footer(
        text="⚡ Arizona Hub & Prime",
        icon_url=interaction.user.display_avatar.url,
    )

    if channel:
      await channel.send(content=role_mentions, embed=embed)
      await interaction.response.send_message(
          "✅ Оповещение опубликовано!", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "❌ Ошибка: Канал не найден!", ephemeral=True
      )


# --- 2. КАПТ ---
class CaptModal(ui.Modal, title="🔫 Захват территории (Капт)"):
  server_input = ui.TextInput(
      label="Номер сервера",
      placeholder="Например: 24",
      style=discord.TextStyle.short,
      required=True,
  )
  band_input = ui.TextInput(
      label="Банда",
      placeholder="Groove, Ballas, Vagos...",
      style=discord.TextStyle.short,
      required=True,
  )
  time_input = ui.TextInput(
      label="Минут до начала (число)",
      placeholder="Например: 10",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    CHANNEL_ID = 1545777967072813096
    role_mentions = "<@&1543326454648020992> <@&1545788983303348326>"

    try:
      channel = await interaction.client.fetch_channel(CHANNEL_ID)
    except Exception:
      channel = None

    guild = interaction.guild
    n = get_emoji(guild, "notify")
    s = get_emoji(guild, "server")
    t = get_emoji(guild, "time")
    a = get_emoji(guild, "avtor")
    b = get_emoji(guild, "band")

    server_str = format_server(self.server_input.value)
    time_code = get_timestamp(self.time_input.value)

    desc = (
        f"### {n} Оповещение » Мероприятие «Капт территории»\n"
        f"───────────────────────────────\n"
        f"{s} **Сервер:** {server_str}\n"
        f"{t} **Начало МП:** {time_code}\n"
        f"{a} **Автор уведомления:** {interaction.user.mention}\n"
        f"{b} **Банда:** `{self.band_input.value}`"
    )

    embed = discord.Embed(description=desc, color=EMBED_COLOR)
    embed.set_footer(
        text="⚡ Arizona Hub & Prime",
        icon_url=interaction.user.display_avatar.url,
    )

    if channel:
      await channel.send(content=role_mentions, embed=embed)
      await interaction.response.send_message(
          "✅ Оповещение опубликовано!", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "❌ Ошибка: Канал не найден!", ephemeral=True
      )


# --- 3. ПРИТОН ---
class PritonModal(ui.Modal, title="💊 Битва за притон"):
  server_input = ui.TextInput(
      label="Номер сервера",
      placeholder="Например: 24",
      style=discord.TextStyle.short,
      required=True,
  )
  band_input = ui.TextInput(
      label="Банда",
      placeholder="За кого заходим",
      style=discord.TextStyle.short,
      required=True,
  )
  time_input = ui.TextInput(
      label="Минут до начала (число)",
      placeholder="Например: 15",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    CHANNEL_ID = 1545777967072813096
    role_mentions = "<@&1543326454648020992> <@&1545788983303348326>"

    try:
      channel = await interaction.client.fetch_channel(CHANNEL_ID)
    except Exception:
      channel = None

    guild = interaction.guild
    n = get_emoji(guild, "notify")
    s = get_emoji(guild, "server")
    t = get_emoji(guild, "time")
    a = get_emoji(guild, "avtor")
    b = get_emoji(guild, "band")

    server_str = format_server(self.server_input.value)
    time_code = get_timestamp(self.time_input.value)

    desc = (
        f"### {n} Оповещение » Мероприятие «Битва за притон»\n"
        f"───────────────────────────────\n"
        f"{s} **Сервер:** {server_str}\n"
        f"{t} **Начало МП:** {time_code}\n"
        f"{a} **Автор уведомления:** {interaction.user.mention}\n"
        f"{b} **Банда:** `{self.band_input.value}`"
    )

    embed = discord.Embed(description=desc, color=EMBED_COLOR)
    embed.set_footer(
        text="⚡ Arizona Hub & Prime",
        icon_url=interaction.user.display_avatar.url,
    )

    if channel:
      await channel.send(content=role_mentions, embed=embed)
      await interaction.response.send_message(
          "✅ Оповещение опубликовано!", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "❌ Ошибка: Канал не найден!", ephemeral=True
      )


# --- 4. НЕФТЕВЫШКИ ---
class OilModal(ui.Modal, title="🛢️ Битва за нефтевышки"):
  server_input = ui.TextInput(
      label="Номер сервера",
      placeholder="Например: 24",
      style=discord.TextStyle.short,
      required=True,
  )
  band_input = ui.TextInput(
      label="За кого заходим",
      placeholder="Мафия / Семья / Организация",
      style=discord.TextStyle.short,
      required=True,
  )
  time_input = ui.TextInput(
      label="Минут до начала (число)",
      placeholder="Например: 20",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    CHANNEL_ID = 1545777967072813096
    role_mentions = "<@&1543326454648020992> <@&1545788983303348326>"

    try:
      channel = await interaction.client.fetch_channel(CHANNEL_ID)
    except Exception:
      channel = None

    guild = interaction.guild
    n = get_emoji(guild, "notify")
    s = get_emoji(guild, "server")
    t = get_emoji(guild, "time")
    a = get_emoji(guild, "avtor")
    b = get_emoji(guild, "band")

    server_str = format_server(self.server_input.value)
    time_code = get_timestamp(self.time_input.value)

    desc = (
        f"### {n} Оповещение » Мероприятие «Битва за нефтевышки»\n"
        f"───────────────────────────────\n"
        f"{s} **Сервер:** {server_str}\n"
        f"{t} **Начало МП:** {time_code}\n"
        f"{b} **За кого заходим:** `{self.band_input.value}`\n"
        f"{a} **Автор уведомления:** {interaction.user.mention}"
    )

    embed = discord.Embed(description=desc, color=EMBED_COLOR)
    embed.set_footer(
        text="⚡ Arizona Hub & Prime",
        icon_url=interaction.user.display_avatar.url,
    )

    if channel:
      await channel.send(content=role_mentions, embed=embed)
      await interaction.response.send_message(
          "✅ Оповещение опубликовано!", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "❌ Ошибка: Канал не найден!", ephemeral=True
      )


# --- 5. СЕМЕЙНЫЕ БИТВЫ ---
class FamilyModal(ui.Modal, title="👑 Семейные битвы"):
  server_input = ui.TextInput(
      label="Номер сервера",
      placeholder="Например: 24",
      style=discord.TextStyle.short,
      required=True,
  )
  family_input = ui.TextInput(
      label="Название семьи",
      placeholder="Введите название",
      style=discord.TextStyle.short,
      required=True,
  )
  phone_input = ui.TextInput(
      label="Связь",
      placeholder="Тег лидера / связь",
      style=discord.TextStyle.short,
      required=True,
  )
  time_input = ui.TextInput(
      label="Минут до начала (число)",
      placeholder="Например: 15",
      style=discord.TextStyle.short,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    CHANNEL_ID = 1545777967072813096
    role_mentions = "<@&1543326454648020992> <@&1545788983303348326>"

    try:
      channel = await interaction.client.fetch_channel(CHANNEL_ID)
    except Exception:
      channel = None

    guild = interaction.guild
    n = get_emoji(guild, "notify")
    s = get_emoji(guild, "server")
    t = get_emoji(guild, "time")
    a = get_emoji(guild, "avtor")
    f_emoji = get_emoji(guild, "family")
    p_emoji = get_emoji(guild, "phone")

    server_str = format_server(self.server_input.value)
    time_code = get_timestamp(self.time_input.value)

    desc = (
        f"### {n} Оповещение » Мероприятие «Семейные битвы»\n"
        f"───────────────────────────────\n"
        f"{s} **Сервер:** {server_str}\n"
        f"{t} **Начало МП:** {time_code}\n"
        f"{a} **Автор уведомления:** {interaction.user.mention}\n"
        f"{f_emoji} **Семья:** `{self.family_input.value}`\n"
        f"{p_emoji} **Связь с лидером семьи:** `{self.phone_input.value}`"
    )

    embed = discord.Embed(description=desc, color=EMBED_COLOR)
    embed.set_footer(
        text="⚡ Arizona Hub & Prime",
        icon_url=interaction.user.display_avatar.url,
    )

    if channel:
      await channel.send(content=role_mentions, embed=embed)
      await interaction.response.send_message(
          "✅ Оповещение опубликовано!", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "❌ Ошибка: Канал не найден!", ephemeral=True
      )


# --- ЗАПУСК БОТА ЧЕРЕЗ КЛИЕНТ ---
class MyBot(discord.Client):

  def __init__(self):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    super().__init__(intents=intents)
    self.tree = discord.app_commands.CommandTree(self)

  async def setup_hook(self):

    @self.tree.command(
        name="mpevent",
        description="Панель управления оповещениями мероприятий",
    )
    async def mpevent(interaction: discord.Interaction):
      view = EventView(interaction.guild)
      guild = interaction.guild
      zakrepit_emoji = get_emoji(guild, "zakrepit") if guild else "📌"

      await interaction.response.send_message(
          f"{zakrepit_emoji} **Панель создания оповещений**\nВыберите мероприятие:",
          view=view,
          ephemeral=True,
      )

    await self.tree.sync()


bot = MyBot()


@bot.event
async def on_ready():
  print(f"Бот {bot.user} успешно запущен!")


if __name__ == "__main__":
  # Запускаем бота в фоновом потоке, а Flask оставляем главным для Render
  bot_thread = threading.Thread(target=run_bot)
  bot_thread.start()

  run_web()

import os

bot.run(os.environ['DISCORD_TOKEN'])
