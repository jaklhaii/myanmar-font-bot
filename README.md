# Professional Myanmar Font Converter Telegram Bot

ဤ Project သည် Telegram မှ ကူးယူလာသော မည်သည့်မြန်မာစာသားကိုမဆို PowerPoint တွင် ဖောင့်မကွဲစေရန် **Pyidaungsu Unicode** သို့ အမှန်ကန်ဆုံးနှင့် အညီညာဆုံး အလိုအလျောက် ပြောင်းပေးသော Professional Bot ဖြစ်ပါသည်။

---

## 📁 Project Structure
- `bot.py`: Telegram Bot ၏ ပင်မ Source Code (Commands, Handlers, Logging နှင့် Application Loop)။
- `converter.py`: ဇော်ဂျီနှင့် ယူနီကုတ်ကို ဉာဏ်ရည်သုံးစနစ်ဖြင့် စစ်ဆေးပြောင်းလဲပေးသော Universal Normalizer Module။
- `rabbit.py`: အဆင့်မြင့် Zawgyi-to-Unicode conversion အင်ဂျင်။

---

## 🚀 Deployment & Running
1. လိုအပ်သော Libraries များကို ထည့်သွင်းပါ:
   ```bash
   pip install python-telegram-bot
   ```
2. Bot ကို စတင် Run ပါ:
   ```bash
   python3 bot.py
   ```
