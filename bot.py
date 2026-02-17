import discord
from discord import app_commands
import os

intents = discord.Intents.default()
intents.guilds = True

class BroadcastBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = BroadcastBot()

@client.tree.command(name="broadcast", description="指定した名前のスレッドに全チャンネル一斉送信")
@app_commands.describe(
    thread_name="送信先スレッド名",
    message="送信するメッセージ"
)
async def broadcast(interaction: discord.Interaction, thread_name: str, message: str):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    success = []
    skipped = []

    for channel in guild.text_channels:
        # チャンネルのスレッドを取得（アクティブ）
        try:
            threads = channel.threads
            for thread in threads:
                if thread.name == thread_name:
                    await thread.send(message)
                    success.append(f"#{channel.name} > {thread.name}")
                    break
            else:
                skipped.append(f"#{channel.name}")
        except Exception as e:
            skipped.append(f"#{channel.name} (エラー: {e})")

    result = f"✅ 送信完了: {len(success)}件\n"
    if success:
        result += "\n".join(f"  - {s}" for s in success) + "\n"
    if skipped:
        result += f"\n⏭ スキップ: {len(skipped)}件"

    await interaction.followup.send(result, ephemeral=True)

client.run(os.environ["DISCORD_TOKEN"])
