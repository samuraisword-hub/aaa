import discord
from discord import app_commands
import os

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

class ThreadNameModal(discord.ui.Modal, title='ブロードキャスト'):
    thread_name = discord.ui.TextInput(
        label='送信先スレッド名',
        placeholder='例: お知らせ',
        required=True,
        max_length=100
    )

    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        success = []
        skipped = []

        for channel in guild.text_channels:
            try:
                threads = channel.threads
                for thread in threads:
                    if thread.name == self.thread_name.value:
                        # テキスト送信
                        if self.message.content:
                            await thread.send(self.message.content)
                        
                        # 添付ファイル（画像含む）送信
                        if self.message.attachments:
                            for attachment in self.message.attachments:
                                await thread.send(attachment.url)
                        
                        success.append(f"#{channel.name} > {thread.name}")
                        break
                else:
                    skipped.append(f"#{channel.name}")
            except Exception as e:
                skipped.append(f"#{channel.name} (エラー: {e})")

        result = f"✅ 送信完了: {len(success)}件\n"
        if success:
            result += "\n".join(f"  - {s}" for s in success[:10])
            if len(success) > 10:
                result += f"\n  ...他{len(success)-10}件"
        if skipped:
            result += f"\n\n⏭ スキップ: {len(skipped)}件"

        await interaction.followup.send(result, ephemeral=True)

class BroadcastBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = BroadcastBot()

@client.tree.context_menu(name="ブロードキャスト")
async def broadcast_message(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_modal(ThreadNameModal(message))

client.run(os.environ["DISCORD_TOKEN"])
