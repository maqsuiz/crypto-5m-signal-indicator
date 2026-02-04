# Crypto 5-Minute Trading Signal Indicator

A 5-minute timeframe crypto trading indicator designed to generate short-term
buy/sell signals based on momentum and volatility filtering.

## Purpose
This project focuses on short-term signal visibility in highly volatile
crypto markets. It is designed for educational and experimental purposes.

## Features
- Optimized for 5-minute timeframe
- Clear visual buy and sell signals
- Momentum and volatility-based filtering
- Designed for high-frequency crypto markets

## System Overview
This project combines a TradingView Pine Script indicator with
a Python-based alert system for real-time notifications.

## Alert Integration
- TradingView alerts are delivered via Gmail
- Incoming emails are parsed using Python
- Valid signals are forwarded to Discord using webhooks

## Use Case
Designed for real-time signal monitoring and alert delivery,
rather than fully automated trade execution.

## Limitations
- Not a guaranteed profit system
- Performs poorly in low-volatility or ranging markets
- Sensitive to sudden news-driven price movements
- Requires proper risk management by the user

## AI Assistance
AI prompt engineering was used during the design process to
refine indicator logic, reduce noise, and improve signal clarity.

## Security
Sensitive credentials (email access, webhook URLs) are removed
from this repository. Configuration values are excluded intentionally.

## Disclaimer
This project is not financial advice.
