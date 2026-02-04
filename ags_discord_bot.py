# -*- coding: utf-8 -*-
# AGS PRO - TradingView Email to Discord Bot
# Bu bot TradingView email alertlerini Discord'a embed olarak gonderir

import imaplib
import email
from email.header import decode_header
import requests
import json
import time
import re
import sys
import io
from datetime import datetime, timezone

# Windows console encoding fix - REMOVED (Handled by batch file)
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════════════════════════
# AYARLAR - BU KISMI DOLDURUN
# ═══════════════════════════════════════════════════════════════════════════════

# Gmail Ayarlari
EMAIL_ADDRESS = "xxxxx@gmail.com"  # Gmail adresiniz
EMAIL_PASSWORD = "APP_PASSWORD_HERE"   # Gmail App Password (NOT A NORMAL PASSWORD)

# Discord Webhook URL
DISCORD_WEBHOOK = "DISCORD_WEBHOOK_URL"

# Kontrol Araligi (saniye)
CHECK_INTERVAL = 30  # Her 30 saniyede bir kontrol et

# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD EMBED GONDERME
# ═══════════════════════════════════════════════════════════════════════════════

def send_discord_message(message, mention_everyone=True):
    """Discord'a basit metin mesaj gonder"""
    
    # Turkiye saati (UTC+3)
    from datetime import timedelta
    turkey_time = datetime.now(timezone.utc) + timedelta(hours=3)
    current_time_str = turkey_time.strftime('%H:%M:%S')
    current_date_str = turkey_time.strftime('%d/%m/%Y')
    
    # Mesajın sonuna saat ekle
    full_message = f"{message}\n\n⏰ {current_time_str} | 📅 {current_date_str}"
    
    # @everyone ekle
    if mention_everyone:
        full_message = f"@everyone\n\n{full_message}"
    
    payload = {"content": full_message}
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"[OK] Discord'a gonderildi")
            return True
        else:
            print(f"[HATA] Discord hatasi: {response.status_code}")
            return False
    except Exception as e:
        print(f"[HATA] Baglanti hatasi: {e}")
        return False

def send_discord_embed(title, description, color, fields=None, mention_everyone=True):
    """Discord'a embed mesaj gonder - artık düz metin olarak gonderiliyor"""
    
    # Turkiye saati (UTC+3)
    from datetime import timedelta
    turkey_time = datetime.now(timezone.utc) + timedelta(hours=3)
    current_time_str = turkey_time.strftime('%H:%M:%S')
    current_date_str = turkey_time.strftime('%d/%m/%Y')
    
    # Basit metin formatina cevir
    message = f"**{title}**\n"
    message += f"{description}\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if fields:
        for field in fields:
            name = field.get("name", "")
            value = field.get("value", "")
            if name and value and name != "\u200b":
                message += f"{name}: {value}\n"
    
    message += f"\n⏰ {current_time_str} | 📅 {current_date_str}"
    
    # @everyone ekle
    if mention_everyone:
        message = f"@everyone\n\n{message}"
    
    payload = {"content": message}
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"[OK] Discord'a gonderildi: {title}")
            return True
        else:
            print(f"[HATA] Discord hatasi: {response.status_code}")
            return False
    except Exception as e:
        print(f"[HATA] Baglanti hatasi: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL OKUMA VE ISLEME
# ═══════════════════════════════════════════════════════════════════════════════

def parse_tradingview_alert(subject, body):
    """TradingView alert emailini parse et"""
    
    # Turkiye saati (UTC+3)
    from datetime import timedelta
    turkey_time = datetime.now(timezone.utc) + timedelta(hours=3)
    current_time_str = turkey_time.strftime('%H:%M:%S')
    
    # Sinyal tipini belirle
    if "AL" in subject.upper() or "LONG" in subject.upper() or "BUY" in subject.upper():
        signal_type = "AL"
        color = 65280  # Yesil
        emoji = "🟢 LONG"
        suggestion = "💡 **Öneri:** Yükseliş trendi bekleniyor. Risk yönetimine dikkat edin!"
        action_tip = "📈 Stop loss'u belirleyin, hedef fiyatı takip edin."
    elif "SAT" in subject.upper() or "SHORT" in subject.upper() or "SELL" in subject.upper():
        signal_type = "SAT"
        color = 16711680  # Kirmizi
        emoji = "🔴 SHORT"
        suggestion = "💡 **Öneri:** Düşüş trendi bekleniyor. Pozisyon boyutuna dikkat!"
        action_tip = "📉 Zarar kesimi önemli, TP seviyelerini takip edin."
    elif "DIVERGENCE" in subject.upper():
        signal_type = "DIVERGENCE"
        color = 5793266  # Mavi
        emoji = "🔵 UYUMSUZLUK"
        suggestion = "💡 **Öneri:** Trend dönüşü sinyali! Dikkatli olun."
        action_tip = "⚠️ Onay bekleyin, acele etmeyin."
    else:
        signal_type = "BILDIRIM"
        color = 16744192  # Turuncu
        emoji = "🟠 BİLGİ"
        suggestion = "💡 **Öneri:** Piyasayı izlemeye devam edin."
        action_tip = "📊 Genel piyasa durumunu takip edin."
    
    # Fiyat bilgisini cikar (TR ve ENG destegi)
    price_match = re.search(r'(?:Fiyat|Price)[:\s]*([0-9.,]+)', body, re.IGNORECASE)
    price = price_match.group(1) if price_match else "N/A"
    
    # Sembol bilgisini cikar (TR ve ENG destegi)
    symbol_match = re.search(r'(?:Sembol|Symbol)[:\s]*([A-Z0-9]+)', body, re.IGNORECASE)
    symbol = symbol_match.group(1) if symbol_match else "N/A"
    
    # SL/TP bilgilerini cikar
    sl_match = re.search(r'(?:SL|Stop)[:\s]*([0-9.,]+)', body, re.IGNORECASE)
    tp1_match = re.search(r'TP1[:\s]*([0-9.,]+)', body, re.IGNORECASE)
    tp2_match = re.search(r'TP2[:\s]*([0-9.,]+)', body, re.IGNORECASE)
    
    # RSI bilgisini cikar
    rsi_match = re.search(r'RSI[:\s]*([0-9.,]+)', body, re.IGNORECASE)
    rsi_value = rsi_match.group(1) if rsi_match else None
    
    # Timeframe bilgisini cikar
    tf_match = re.search(r'(?:Timeframe|TF|Periyot)[:\s]*([0-9]+[mhHMdDwW]?)', body, re.IGNORECASE)
    timeframe = tf_match.group(1) if tf_match else None
    
    fields = [
        {"name": "📊 Sembol", "value": f"`{symbol}`", "inline": True},
        {"name": "💰 Fiyat", "value": f"`{price}`", "inline": True},
        {"name": "⏰ Sinyal Saati", "value": f"`{current_time_str}`", "inline": True},
    ]
    
    if sl_match:
        fields.append({"name": "🛑 Stop Loss", "value": f"`{sl_match.group(1)}`", "inline": True})
    if tp1_match:
        fields.append({"name": "🎯 TP1", "value": f"`{tp1_match.group(1)}`", "inline": True})
    if tp2_match:
        fields.append({"name": "🎯 TP2", "value": f"`{tp2_match.group(1)}`", "inline": True})
    if rsi_value:
        fields.append({"name": "📈 RSI", "value": f"`{rsi_value}`", "inline": True})
    if timeframe:
        fields.append({"name": "⏱️ Periyot", "value": f"`{timeframe}`", "inline": True})
    
    # Bos alan ekle (gorsel duzenleme icin)
    fields.append({"name": "\u200b", "value": "\u200b", "inline": False})
    
    # Oneri ve aksiyon ipuclari ekle
    fields.append({"name": "📝 Öneri", "value": suggestion, "inline": False})
    fields.append({"name": "🎯 Aksiyon", "value": action_tip, "inline": False})
    
    # Uyari mesaji ekle
    fields.append({"name": "⚠️ Uyarı", "value": "*Bu finansal tavsiye değildir. Kendi araştırmanızı yapın!*", "inline": False})
    
    return {
        "title": f"{emoji} SİNYALİ",
        "description": f"**{subject}**\n\n━━━━━━━━━━━━━━━━━━━━━━",
        "color": color,
        "fields": fields
    }

def check_emails():
    """Yeni TradingView emaillerini kontrol et"""
    try:
        # Gmail'e baglan
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # TradingView'dan gelen okunmamis emailleri ara
        status, messages = mail.search(None, '(UNSEEN FROM "noreply@tradingview.com")')
        
        if status != "OK":
            return
        
        email_ids = messages[0].split()
        
        for email_id in email_ids:
            # Email'i oku
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            
            if status != "OK":
                continue
            
            # Email'i parse et
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Konu
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            
            # Icerik
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode()
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode()
            
            if not body:
                print(f"[UYARI] Bos email icerigi ({subject})")
                continue

            # JSON Kontrolu - JSON varsa parse et ve duz metin olarak gonder
            json_sent = False
            try:
                # "Alert:" ile baslayan JSON'u temizle
                clean_body = body
                if "Alert:" in body or "alert:" in body:
                    clean_body = re.sub(r'Alert:\s*', '', body, flags=re.IGNORECASE)
                
                # Suslu parantez arasindaki JSON'u bul
                json_match = re.search(r'(\{.*\})', clean_body.replace('\n', '').replace('\r', ''), re.DOTALL)
                if json_match:
                    possible_json = json_match.group(1)
                    json_data = json.loads(possible_json)
                    
                    if "embeds" in json_data:
                        print(f"[BILGI] JSON Discord embed verisi bulundu, duz metin formatina cevriliyor...")
                        
                        # JSON'dan bilgileri cikar ve duz metin olustur
                        embed = json_data["embeds"][0]
                        title = embed.get("title", "SINYAL")
                        description = embed.get("description", "")
                        fields = embed.get("fields", [])
                        
                        # Duz metin mesaji olustur
                        message = f"**{title}**\n"
                        if description:
                            message += f"{description}\n"
                        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
                        
                        for field in fields:
                            name = field.get("name", "")
                            value = field.get("value", "")
                            if name and value:
                                message += f"{name}: {value}\n"
                        
                        # Discord'a gonder
                        json_sent = send_discord_message(message)
                        
                        if json_sent:
                            mail.store(email_id, '+FLAGS', '\\Seen')
                            continue
            except json.JSONDecodeError:
                # JSON parse hatasi - onemli degil, text olarak devam et
                pass
            except Exception as e:
                 # Diger hatalar
                 print(f"[UYARI] JSON isleme hatasi: {e}")
                 pass
            
            # Normal Text Format (Eski usul veya basit alarmlar)
            alert_data = parse_tradingview_alert(subject, body)
            
            # SPAM KONTROLU
            # Eger Sembol ve Fiyat bilgisi yoksa ...
            is_valid_signal = False
            
            # 1. Kural: Sembol ve Fiyat var mi?
            has_price = False
            has_symbol = False
            for field in alert_data["fields"]:
                # Emoji'li alan adlarini kontrol et
                if "Sembol" in field["name"] and "`N/A`" not in field["value"]: has_symbol = True
                if "Fiyat" in field["name"] and "`N/A`" not in field["value"]: has_price = True
            
            if has_symbol or has_price:
                is_valid_signal = True

            # 2. Kural: Konu veya icerikte AGS PRO veya Divergence geciyor mu?
            subject_upper = subject.upper()
            body_upper = body.upper()
            if "AGS PRO" in subject_upper or "AGS PRO" in body_upper or \
               "DIVERGENCE" in subject_upper or "DIVERGENCE" in body_upper or \
               "BULLISH" in subject_upper or "BEARISH" in subject_upper or \
               "ALERT" in subject_upper:
               is_valid_signal = True
            
            if not is_valid_signal:
                print(f"[BILGI] Spam veya Gecersiz Sinyal Engellendi: {subject}")
                # Yine de islendi olarak isaretle ki tekrar tekrar okumasin
                mail.store(email_id, '+FLAGS', '\\Seen')
                continue

            send_discord_embed(
                alert_data["title"],
                alert_data["description"],
                alert_data["color"],
                alert_data["fields"]
            )
            
            # Email'i islendi olarak isaretle
            mail.store(email_id, '+FLAGS', '\\Seen')
        
        mail.logout()
        
    except imaplib.IMAP4.error as e:
        print(f"[HATA] IMAP hatasi: {e}")
        print("[BILGI] Gmail App Password olusturmaniz gerekiyor!")
        print("[BILGI] https://myaccount.google.com/apppasswords adresine gidin")
    except Exception as e:
        print(f"[HATA] Genel Hata: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# ANA DONGU
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  AGS PRO Discord Bot Baslatildi!")
    print("=" * 60)
    print(f"  Email: {EMAIL_ADDRESS}")
    print(f"  Kontrol araligi: {CHECK_INTERVAL} saniye")
    print("=" * 60)
    
    # Baslangic mesaji gonder
    send_discord_embed(
        "AGS PRO Bot Aktif",
        "TradingView email bildirimleri Discord'a yonlendirilecek.",
        65280,
        [{"name": "Durum", "value": "Calisiyor", "inline": True}]
    )
    
    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[{current_time}] Email kontrol ediliyor...")
            check_emails()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nBot kapatiliyor...")
            break
        except Exception as e:
            print(f"[HATA] Hata: {e}")
            time.sleep(60)  # Hata durumunda 1 dakika bekle

if __name__ == "__main__":
    main()
