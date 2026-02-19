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
                # アクティブスレッドを取得
                all_threads = list(channel.threads)

                # デバッグ：見つかったスレッド名を記録
                thread_names = [t.name for t in all_threads]
                print(f"チャンネル {channel.name}: スレッド {thread_names}")
                
                # アーカイブ済みスレッドも取得
                try:
                    async for archived_thread in channel.archived_threads(limit=100):
                        all_threads.append(archived_thread)
                except:
                    pass
                
                found = False
                for thread in all_threads:
                    if thread.name == self.thread_name.value:
                        print(f"マッチ: {channel.name} > {thread.name}")
                        # 画像ファイルを取得
                        files = []
                        if self.message.attachments:
                            for attachment in self.message.attachments:
                                file = await attachment.to_file()
                                files.append(file)
                        
                        # テキストと画像を一緒に送信
                           print(f"送信内容: content={bool(self.message.content)}, files={len(files)}")
                        if files:
                            await thread.send(content=self.message.content or "", files=files)
                        elif self.message.content:
                            await thread.send(self.message.content)
                        
                        success.append(f"#{channel.name} > {thread.name}")
                        found = True
                        break
                
                if not found:
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
